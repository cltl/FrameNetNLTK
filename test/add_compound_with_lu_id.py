import sys
from nltk.corpus import framenet as fn

sys.path.insert(0, '..')
sys.path.insert(0, '../..')
from FrameNetNLTK import add_lu, load
from FrameNetNLTK import get_luid

lexemes = [{
    'order' : '1',
    'headword' : 'false',
    'breakBefore' : 'false',
    'POS' : 'N',
    'name' : 'president'
}]

add_lu(your_lexicon_folder='test_lexicon',
       fn_en=fn,
       lu_name='president.n',
       lexemes=lexemes,
       definition='een gekozen functionaris met regerende macht over een republikeinse staat, universiteit of bedrijf.',
       status='Created',
       pos='N',
       frame='Appellations',
       agent='MartenPostma',
       provenance='manual',
       lu_type='singleton',
       incorporated_fe="Title",
       verbose=2)


lexemes = [{
    'order' : '1',
    'headword' : 'false',
    'breakBefore' : 'false',
    'POS' : 'N',
    'name' : 'verkiezing'
}]

add_lu(your_lexicon_folder='test_lexicon',
       fn_en=fn,
       lu_name='verkiezing.n',
       lexemes=lexemes,
       definition='een formele procedure waarbij een persoon gekozen wordt.',
       status='Created',
       pos='N',
       frame='Change_of_leadership',
       agent='MartenPostma',
       provenance='manual',
       lu_type='singleton',
       verbose=2)


my_fn = load('test_lexicon')
president_lu_id, reason = get_luid(my_fn=my_fn,
                                   frame_label='Appellations',
                                   lemma='president',
                                   pos='N')


verkiezing_lu_id, reason = get_luid(my_fn=my_fn,
                                    frame_label='Change_of_leadership',
                                    lemma="verkiezing",
                                    pos="N")

lexemes = [{
    'order' : '1',
    'headword' : 'false',
    'breakBefore' : 'false',
    'POS' : 'N',
    'name' : 'president',
    'incorporatedFE' : 'Function',
    'lu_id' : str(president_lu_id)
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
    'lu_id' : str(verkiezing_lu_id)
}
]
add_lu(your_lexicon_folder='test_lexicon',
       fn_en=fn,
       lu_name='presidentsverkiezing.n',
       lexemes=lexemes,
       definition='het proces van het kiezen van een president.',
       status='Created',
       pos='N',
       frame='Change_of_leadership',
       agent='MartenPostma',
       provenance='manual',
       lu_type='endocentric compound',
       incorporated_fe="Function",
       verbose=2)

