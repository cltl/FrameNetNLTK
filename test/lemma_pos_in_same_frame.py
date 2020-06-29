import pytest
import sys
from nltk.corpus import framenet as fn

sys.path.insert(0, '../..')
from FrameNetNLTK import add_lu

lexemes = [{
    'order' : '1',
    'headword' : 'false',
    'breakBefore' : 'false',
    'POS' : 'N',
    'name' : 'Mexicaan'
}]


add_lu(your_lexicon_folder='test_lexicon',
       fn_en=fn,
       lexemes=lexemes,
       definition='uit Mexico',
       status='Created',
       pos='N',
       frame='People_by_origin',
       provenance='manual',
       incorporated_fe='Origin',
       verbose=2)


def test_twice_the_same():
    with pytest.raises(AssertionError):
        add_lu(your_lexicon_folder='test_lexicon',
               fn_en=fn,
               lexemes=lexemes,
               definition='uit Mexico',
               status='Created',
               pos='N',
               frame='People_by_origin',
               provenance='manual',
               verbose=2)

test_twice_the_same()