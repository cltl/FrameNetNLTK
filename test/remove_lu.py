import sys
import pytest

sys.path.insert(0, '../..')
from FrameNetNLTK import load, remove_lu, get_luid

fn = load('../test/test_lexicon')


lu_id, reason = get_luid(my_fn=fn,
                         frame_label='People_by_origin',
                         lemma='Fransman',
                         pos='N')

remove_lu(your_lexicon_folder='test_lexicon',
          lu_id=lu_id,
          verbose=2)



lu_id, reason = get_luid(my_fn=fn,
                         frame_label='Appellations',
                         lemma='president',
                         pos='N')

try:
    remove_lu(your_lexicon_folder='test_lexicon',
              lu_id=lu_id,
              verbose=2)
except AssertionError:
    print(f'AssertionError was correctly raised for lu_id {lu_id} since it is part of an endocentric compound.')