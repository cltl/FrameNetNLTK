import sys
sys.path.insert(0, '..')
sys.path.insert(0, '../..')

from FrameNetNLTK import add_lu
from nltk.corpus import framenet as fn

lexemes = [{
    'order' : '1',
    'headword' : 'false',
    'breakBefore' : 'false',
    'POS' : 'N',
    'name' : 'senaat',
    'incorporatedFE' : 'Function',
},
{
    'order' : '2',
    'headword' : 'false',
    'breakBefore' : 'false',
    'POS' : 'I',
    'name' : 's',
},
{
    'order': '3',
    'headword': 'true',
    'breakBefore': 'false',
    'POS': 'N',
    'name': 'verkiezing',
}
]

add_lu(your_lexicon_folder='test_lexicon',
       fn_en=fn,
       lexemes=lexemes,
       definition='het proces van het kiezen van een senator.',
       status='Created',
       pos='N',
       frame='Change_of_leadership',
       provenance='manual',
       incorporated_fe="Function",
       verbose=2)