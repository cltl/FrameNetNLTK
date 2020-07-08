import sys
from nltk.corpus import framenet as fn

sys.path.insert(0, '../..')
from FrameNetNLTK import add_lu

lexemes = [{
    'order' : '1',
    'headword' : 'false',
    'breakBefore' : 'false',
    'POS' : 'N',
    'name' : 'president',
    'evokes' : 'false',
    'incorporatedFE' : 'Function'
},
{
    'order' : '2',
    'headword' : 'false',
    'breakBefore' : 'false',
    'POS' : 'I',
    'name' : 's',
    'evokes' : 'false'
},
{
    'order': '3',
    'headword': 'true',
    'breakBefore': 'false',
    'POS': 'N',
    'name': 'verkiezing',
    'evokes' : 'true'
}
]
add_lu(your_lexicon_folder='test_lexicon',
       fn_en=fn,
       lexemes=lexemes,
       definition='het proces van het kiezen van een president.',
       status='Created',
       pos='N',
       frame='Change_of_leadership',
       provenance='manual',
       incorporated_fe="Function",
       verbose=2)

lexemes = [{
    'order' : '1',
    'headword' : 'false',
    'breakBefore' : 'false',
    'POS' : 'N',
    'name' : 'aanslag',
    'evokes' : 'true',
},
{
    'order' : '2',
    'headword' : 'true',
    'breakBefore' : 'false',
    'POS' : 'N',
    'name' : 'pleger',
    'evokes' : 'false',
    'incorporatedFE': 'Assailant'
},
]
add_lu(your_lexicon_folder='test_lexicon',
       fn_en=fn,
       lexemes=lexemes,
       definition='een entiteit die een aanslag pleegt.',
       status='Created',
       pos='N',
       frame='Attack',
       provenance='manual',
       incorporated_fe="Assailant",
       verbose=2)


lexemes = [{
    'order' : '1',
    'headword' : 'false',
    'breakBefore' : 'false',
    'POS' : 'N',
    'name' : 'Duitser'
}]

add_lu(your_lexicon_folder='test_lexicon',
       fn_en=fn,
       lexemes=lexemes,
       definition='uit Duitsland',
       status='Created',
       pos='N',
       frame='People_by_origin',
       provenance='manual',
       incorporated_fe="Origin",
       optional_lu_attrs={"RBN_sense_ID" : "r_n-11800", "RBN_matching_relation" : "equivalence"},
       verbose=2)

