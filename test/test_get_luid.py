import sys

from nltk.corpus import framenet as fn

sys.path.insert(0, '..')
sys.path.insert(0, '../..')
from FrameNetNLTK import load, get_luid

fn = load('../test/test_lexicon')


lu_id, reason = get_luid(my_fn=fn,
                         frame_label='Change_of_leadership',
                         lemma='verkiezing',
                         pos='N')

assert type(lu_id) == int
assert len(str(lu_id)) == 13