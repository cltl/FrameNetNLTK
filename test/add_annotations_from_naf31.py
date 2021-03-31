import sys

sys.path.insert(0, '..')
sys.path.insert(0, '../..')

from lxml import etree
from rdflib import Graph

from nltk.corpus import framenet as fn
import FrameNetNLTK
from FrameNetNLTK import add_annotations_from_naf_31
from FrameNetNLTK import load, get_luid
from rdflib.term import URIRef

naf_path = 'test_naf_files/predicate_in_compound.naf'
corpus_name = 'HDD'
corpus_description = 'HistoricalDistanceData'

my_fn = load(folder='test_lexicon',
             verbose=2)

# load Dutch FrameNet in Lemon
path_dfn_in_lemon = 'stats/dfn_0.1.ttl'
dfn_in_lemon = Graph()
dfn_in_lemon.parse(path_dfn_in_lemon, format='ttl')

# update NAF file with correct LU URIs
parser = etree.XMLParser(remove_blank_text=True, strip_cdata=False)
doc = etree.parse(naf_path, parser)

# ext_ref_el for predicate annotation
ext_ref_els = doc.findall('srl/predicate/externalReferences/externalRef')
assert len(ext_ref_els) == 1, f'expected 2 externalRef elements, found {len(ext_ref_els)}'
ext_ref_el = ext_ref_els[0]
predicate_lu_uri = ext_ref_el.get('lu_uri')

new_lu_id, reason = get_luid(my_fn=my_fn,
                             frame_label='Change_of_leadership',
                             lemma='verkiezing',
                             pos='N')

base, old_lu_id = predicate_lu_uri.rsplit('-', 1)
new_predicate_lu_uri = '-'.join([base, str(new_lu_id)])
assert URIRef(new_predicate_lu_uri) in dfn_in_lemon.subjects()
ext_ref_el.set('lu_uri', new_predicate_lu_uri)

doc.write(naf_path,
          encoding='utf-8',
          pretty_print=True,
          xml_declaration=True)

add_annotations_from_naf_31(your_fn=my_fn,
                            path_to_your_fn_in_lemon=path_dfn_in_lemon,
                            fn_en=fn,
                            premon_nt=FrameNetNLTK.premon_nt,
                            corpus_name=corpus_name,
                            corpus_description=corpus_description,
                            naf_path=naf_path,
                            overwrite=True,
                            start_from_scratch=False,
                            verbose=5)


my_fn = load(folder='test_lexicon',
             verbose=2)

for annotation in my_fn.annotations():
    print(annotation)