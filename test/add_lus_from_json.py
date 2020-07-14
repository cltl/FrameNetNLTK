import sys
from nltk.corpus import framenet as fn

sys.path.insert(0, '../..')
from FrameNetNLTK import add_lus_from_json

add_lus_from_json(your_lexicon_folder='test_lexicon',
                  fn_en=fn,
                  json_path='../res/json/lus.json',
                  verbose=2)
