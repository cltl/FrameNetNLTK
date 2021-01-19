import sys
sys.path.insert(0, '../..')
from nltk.corpus import framenet as fn
import FrameNetNLTK
import ODWN_reader


lexemes = [{
    'order' : '1',
    'headword' : 'false',
    'breakBefore' : 'false',
    'POS' : 'N',
    'name' : 'Duitser'
}]


orbn_id = 'r_n-11800'

skos_predicate_to_external_references = {
    'exactMatch' : {ODWN_reader.senseid_to_uri[orbn_id]}
}


FrameNetNLTK.add_lu(your_lexicon_folder='test_lexicon',
                    fn_en=fn,
                    lu_name='Duitser.n',
                    lexemes=lexemes,
                    definition='uit Duitsland',
                    status='Created',
                    pos='N',
                    frame='People_by_origin',
                    provenance='manual',
                    lu_type='singleton',
                    incorporated_fe="Origin",
                    skos_predicate_to_external_references=skos_predicate_to_external_references,
                    skos=FrameNetNLTK.skos,
                    verbose=2)