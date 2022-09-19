"""
Recommendation Robot
Core
"""

import logging
from transitions import EventData
from transitions.extensions import HierarchicalGraphMachine as HGMachine
from time import sleep

from .msg import substitute
from .util import UserInput

# logging.basicConfig(level=logging.INFO)


class RecommendRobot(HGMachine):
    """
    Recommend Robot State Machine
    """
    def __init__(self,
                 username: str = 'Default Defaultovich',
                 companyname: str = 'Vector Plus',
                 max_repeats: int = 3,
                 max_steps: int = 9):

        states = [
            'stop',
            'idle',
            {'name': 'hello',
             'children': ['main',
                          'repeat',
                          'null']},
            {'name': 'recommend',
             'children': ['main',
                          'repeat',
                          'repeat2',
                          'null',
                          'default',
                          'scorepositive',
                          'scorenegative',
                          'scoreneutral']},
            {'name': 'hangup',
             'children': ['positive',
                          'negative',
                          'wrongtime',
                          'repeats',
                          'null']},
            'forward'
        ]

        self.result = None
        self.context = {'username': username,
                        'companyname': companyname}

        self.repeats = 0
        self.max_repeats = max_repeats
        self.steps = 0
        self.max_steps = max_steps

        self.nlu: UserInput = UserInput()  # Dummy recognition input

        super().__init__(model=self,
                         states=states,
                         initial='hello_main',
                         before_state_change='reply',
                         send_event=True,
                         ignore_invalid_triggers=True)

        # Transitions
        self.add_transition('do_stop',
                            '*',
                            'stop')

        self.add_transition('said_null',
                            'hello',
                            'hello_null')

        self.add_transition('said_null',
                            ['hello_null'],
                            'hangup_null')

        self.add_transition('said_repeat',
                            ['hello'],
                            'hello_repeat',
                            prepare=['increase_repeats'],
                            unless=['too_many_repeats'])

        self.add_transition('said_repeat',
                            'hello',
                            'hangup_repeats',
                            conditions=['too_many_repeats'])

        self.add_transition('said_busy',
                            ['hello', 'recommend'],
                            'hangup_wrongtime')

        self.add_transition('said_no',
                            ['hello'],
                            'hangup_wrongtime')

        self.add_transition('said_yes',
                            'hello',
                            'recommend_main')

        self.add_transition('said_default',
                            'hello',
                            'recommend_main',
                            prepare='reset_repeats')

        self.add_transition('said_null',
                            'recommend',
                            'recommend_null')

        self.add_transition('said_null',
                            'recommend_null',
                            'hangup_null')

        self.add_transition('said_default',
                            'recommend',
                            'hangup_null',
                            conditions=['too_many_repeats'])

        self.add_transition('said_default',
                            'recommend',
                            'recommend_default',
                            prepare=['increase_repeats'],
                            unless=['too_many_repeats'])

        self.add_transition('said_repeat',
                            'recommend',
                            'recommend_repeat2',
                            prepare=['increase_repeats'],
                            unless=['too_many_repeats'])

        self.add_transition('said_repeat',
                            'recommend',
                            'hangup_repeats',
                            conditions=['too_many_repeats'])

        self.add_transition('said_high_score',
                            ['recommend'],
                            'hangup_positive')

        self.add_transition('said_low_score',
                            ['recommend'],
                            'hangup_negative')

        self.add_transition('said_yes',
                            ['recommend'],
                            'recommend_scorepositive')

        self.add_transition('said_no',
                            ['recommend'],
                            'recommend_scorenegative')

        self.add_transition('said_maybe',
                            'recommend',
                            'recommend_scoreneutral')

        self.add_transition('said_dunno',
                            'recommend',
                            'recommend_repeat2')

        self.add_transition('said_question',
                            'recommend',
                            'forward')

    # Conditions check
    def too_many_repeats(self, evt: EventData):
        return self.repeats >= self.max_repeats

    # Utilities
    def _(self, msg_key: str):
        return substitute(msg_key, **self.context)

    def reply(self, evt: EventData):
        # Print message associated with nex transition destination to console
        # In real life will be hooked to voice synthesis output
        print(self._(evt.transition.dest))

    def reset_repeats(self, evt: EventData):
        self.repeats = 0

    def increase_repeats(self, evt: EventData):
        self.repeats += 1

    # Callbacks
    def on_enter_hangup(self, evt: EventData):
        self.do_stop()

    def on_exit_hangup_wrongtime(self, evt: EventData):
        self.result = {'hangup': 'wrong_time'}

    def on_exit_hangup_null(self, evt: EventData):
        self.result = {'hangup': 'recognition_error'}

    def on_exit_hangup_positive(self, evt: EventData):
        self.result = {'hangup': 'positive_response'}

    def on_exit_hangup_negative(self, evt: EventData):
        self.result = {'hangup': 'negative_response'}

    def on_exit_hangup_repeats(self, evt: EventData):
        self.result = {'hangup': 'too_many_repeats'}

    def on_exit_forward(self, evt: EventData):
        self.result = {'bridge': 'forward'}
        self.do_stop()

    def on_enter_stop(self, evt: EventData):
        # Gracefully disconnect from recognition interface or whatever
        self.nlu.shut_down()
        pass

    # Process user input
    def request_user_input(self):
        match _i := self.nlu.get_raw_input():
            # result = nlu.extract(text, self.entities_list)
            # if result.has_entities():
            #     match ...:
            case 'y':  # entity['confirm_true']
                self.said_yes()
            case 'n':  # entity['confirm_false']
                self.said_no()
            case 'b':  # entity['busy']
                self.said_busy()
            case 'r':  # entity['repeat']
                self.said_repeat()
            case 'd':
                self.said_default()
            case 'ls':
                self.said_low_score()
            case 'hs':
                self.said_high_score()
            case 'mb':
                self.said_maybe()
            case 'dn':
                self.said_dunno()
            case _:
                self.said_null()

    def run(self):
        self.to_hello_main()

        while self.state not in ['stop', 'forward']:
            print('Step:', self.steps)
            self.steps += 1
            if self.steps >= self.max_steps:
                self.to_hangup_repeats()
                break
            sleep(.1)
            self.request_user_input()

        return self.result


