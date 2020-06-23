#!/usr/bin/env bash

pytest attributes.py
python initialize_lexicon.py
python load_lexicon.py
python add_lu.py
pytest lemma_pos_in_same_frame.py
python remove_lu.py