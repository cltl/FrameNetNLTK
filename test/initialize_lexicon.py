import pytest
import sys
from nltk.corpus import framenet as fn

sys.path.insert(0, '../..')
from FrameNetNLTK import initialize

initialize(folder='test_lexicon',
           fn_en=fn,
           verbose=2)