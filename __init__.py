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
from .rdf_utils import derive_model

# annotations
from .annotation_utils import add_annotations_from_naf_31


# stats
from .stats_utils import get_frame_stats_df
from .stats_utils import get_lu_stats_df
from .stats_utils import get_lu_per_pos_stats_df
from .stats_utils import get_lexeme_stats_df
from .stats_utils import get_stats_html
from .stats_utils import get_ambiguity_df


# load
dir_path = os.path.dirname(os.path.realpath(__file__))


# lemon
lemon_ttl_path = os.path.join(dir_path,
                              'res/lemon/lemon.ttl')

lemon = Graph()
lemon.parse(lemon_ttl_path, format='ttl')

# FN pos -> lexinfo
path_fn_pos_to_lexinfo = os.path.join(dir_path,
                                      'res',
                                      'rdf',
                                      'mappings',
                                      'fn_pos_to_lexinfo.json')
fn_pos_to_lexinfo = json.load(open(path_fn_pos_to_lexinfo))

path_rbn_pos_to_lexinfo = os.path.join(dir_path,
                                      'res',
                                      'rdf',
                                      'mappings',
                                      'rbn_pos_to_lexinfo.json')
rbn_pos_to_lexinfo = json.load(open(path_rbn_pos_to_lexinfo))


# premon
premon_nt = os.path.join(dir_path, 'res/premon/premon-2018a-fn17-noinf.nt')

# ontolex
ontolex_path = os.path.join(dir_path,
                            'res',
                            'ontolex',
                            'ontolex.rdf')
ontolex = Graph()
ontolex.parse(ontolex_path)

# skos
skos_path = os.path.join(dir_path,
                         'res',
                         'skos',
                         'skos.rdf')
skos = Graph()
skos.parse(skos_path)
