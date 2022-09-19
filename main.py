"""
Recommendation Robot
Manual Testing Interface
===========================
Available commands:
y - Yes
n - No
b - Busy
r - Repeat
mb - Maybe
dn - Don't know
ls - Low score
hs - High score
d - Default
-
Any other - Null
===========================
"""

import sys
from nn_app.core import RecommendRobot


if __name__ == '__main__':
    rr = RecommendRobot()
    print(__doc__)
    print('CTRL+C to STOP')
    try:
        rr.run()
    except KeyboardInterrupt:
        pass
    print('STOP: ', rr.result)
    sys.exit(0)
