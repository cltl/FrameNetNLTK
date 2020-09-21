from .xml_utils import initialize

from .load_utils import load

from .lexicon import add_lu

from .lexicon import add_lus_from_json

from .lexicon import remove_lu

from .lexicon import generate_lu_rdf_uri

from .lexicon_utils import get_luid



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