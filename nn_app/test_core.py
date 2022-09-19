from .core import RecommendRobot


def test_create():
    rr = RecommendRobot()

    assert rr.state == 'hello_main'


def test_repeat():
    rr = RecommendRobot()
    rr.said_null()
    assert rr.state == 'hello_null'
    rr.said_repeat()
    assert rr.state == 'hello_repeat'


def test_null_null():
    rr = RecommendRobot()
    rr.said_null()
    assert rr.state == 'hello_null'
    rr.said_null()
    assert rr.state == 'stop'


def test_score_positive():
    rr = RecommendRobot()
    rr.said_yes()
    assert rr.state == 'recommend_main'
    rr.said_high_score()
    assert rr.result['hangup'] == 'positive_response'


def test_complex_response():
    rr = RecommendRobot()
    rr.said_null()
    assert rr.state == 'hello_null'
    rr.said_yes()
    assert rr.state == 'recommend_main'
    rr.said_maybe()
    assert rr.state == 'recommend_scoreneutral'
    rr.said_no()
    assert rr.state == 'recommend_scorenegative'
    rr.said_question()
    assert rr.result['bridge'] == 'forward'
    assert rr.state == 'stop'

