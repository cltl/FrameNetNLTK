

import sys
sys.path.insert(0, '..')
sys.path.insert(0, '../..')

from FrameNetNLTK import add_lu, load
from nltk.corpus import framenet as fn

lexemes = [{
    'order' : '1',
    'headword' : 'false',
    'breakBefore' : 'false',
    'name' : 'aan'
},
    {'order' : '2',
     'headword' : 'false',
     'breakBefore' : 'false',
     'POS' : 'V',
     'name' : 'bieden'}]

add_lu(your_lexicon_folder='test_lexicon',
       fn_en=fn,
       lu_name='aanbieden.v',
       lexemes=lexemes,
       definition='iets aan iemand aanbieden',
       status='Created',
       pos='V',
       frame='Giving',
       agent='MartenPostma',
       provenance='manual',
       lu_type='phrasal',
       incorporated_fe=None,
       verbose=2)