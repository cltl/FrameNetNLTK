import sys
from nltk.corpus import framenet as fn

sys.path.insert(0, '../..')
from FrameNetNLTK import add_lu

# in this example, we add the identifier r_n-8986 from the Referentie Bestand Nederlands to our new FrameNet
lexemes = [{
    'order' : '1',
    'headword' : 'false',
    'breakBefore' : 'false',
    'POS' : 'N',
    'name' : 'Californiër'
}]

add_lu(your_lexicon_folder='test_lexicon',
       fn_en=fn,
       lexemes=lexemes,
       definition='van Calfornië',
       status='New',
       pos='N',
       frame='People_by_origin',
       provenance='manual',
       verbose=2)
