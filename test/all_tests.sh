#!/usr/bin/env bash

rm -r stats
mkdir stats

pytest attributes.py || exit
python initialize_lexicon.py || exit
python load_lexicon.py || exit
python add_compound_with_lu_id.py || exit
python test_get_luid.py || exit
python add_phrasal_verb.py || exit
python add_compound_without_lu_id.py || exit
python add_lus_from_json.py || exit
pytest lemma_pos_in_same_frame.py || exit
python add_lu_with_external_ref.py || exit
python remove_lu.py || exit
pytest test_lu_rdf_uri.py || exit
python compute_stats.py || exit
python convert_to_lemon.py || exit
python create_lemon_diagram.py || exit
