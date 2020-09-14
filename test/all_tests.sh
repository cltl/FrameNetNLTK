#!/usr/bin/env bash

rm -r stats
mkdir stats

pytest attributes.py
python initialize_lexicon.py
python load_lexicon.py
python test_get_luid.py
python add_compound_with_lu_id.py
python add_compound_without_lu_id.py
python add_lus_from_json.py
pytest lemma_pos_in_same_frame.py
python remove_lu.py
python compute_stats.py