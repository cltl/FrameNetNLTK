import sys

from nltk.corpus import framenet as fn

sys.path.insert(0, '..')
sys.path.insert(0, '../..')
from FrameNetNLTK import get_luid


lu_id, reason = get_luid(my_fn=fn,
                         frame_label='Change_of_leadership',
                         lemma='election',
                         pos='N')

assert lu_id == 10900