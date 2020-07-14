import sys
import pytest

sys.path.insert(0, '../..')
from FrameNetNLTK import remove_lu

remove_lu(your_lexicon_folder='test_lexicon',
                   lu_id=4,
                   verbose=2)

try:
    remove_lu(your_lexicon_folder='test_lexicon',
              lu_id=1,
              verbose=2)
except AssertionError:
    print('AssertionError was correctly raised for lu_id 1 since it is part of an endocentric compound.')