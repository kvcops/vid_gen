from shots_a import *
try:
    from shots_b import *
except ImportError as e:
    print('shots_b missing', e)
try:
    from shots_c import *
except ImportError as e:
    print('shots_c missing', e)
