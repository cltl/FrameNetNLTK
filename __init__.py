import os
import json
from rdflib import Graph

from .xml_utils import initialize

from .load_utils import load

from .lexicon import add_lu

from .lexicon import add_lus_from_json

from .lexicon import remove_lu

from .lexicon_utils import get_luid

# rdf
from .rdf_utils import generate_lexicon_rdf_uri
from .rdf_utils import generate_le_and_lu_rdf_uri
from .rdf_utils import convert_to_lemon

# annotations
# TODO: add_annotations_from_naf_3.1
    # TODO: check if corpus exists
    # TODO: add_corpus
    # TODO: remove_corpus
    # TODO: add_document (make sure it does not exist, generate document_id)
    # TODO: add_sentence (make sure it does not exist, generate sent_id)
    # TODO: add_annotation_set (make sure it does not exist, generate anno_id)

# stats
from .stats_utils import get_frame_stats_df
from .stats_utils import get_lu_stats_df
from .stats_utils import get_lu_per_pos_stats_df
from .stats_utils import get_lexeme_stats_df
from .stats_utils import get_stats_html
from .stats_utils import get_ambiguity_df


# load
dir_path = os.path.dirname(os.path.realpath(__file__))
lemon_ttl_path = os.path.join(dir_path,
                              'res/rdf/lemon.ttl')

lemon = Graph()
lemon.parse(lemon_ttl_path, format='ttl')

path_fn_pos_to_lexinfo = os.path.join(dir_path,
                                      'res',
                                      'rdf',
                                      'mappings',
                                      'fn_pos_to_lexinfo.json')
fn_pos_to_lexinfo = json.load(open(path_fn_pos_to_lexinfo))


from .rdf_utils import load_nt_graph
premon_nt = os.path.join(dir_path, 'res/premon/premon-2018a-fn17-noinf.nt')
premon = load_nt_graph(nt_path=premon_nt)