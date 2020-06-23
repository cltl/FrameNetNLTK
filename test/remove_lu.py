import sys

sys.path.insert(0, '../..')
from FrameNetNLTK import remove_lu

remove_lu(your_lexicon_folder='test_lexicon',
          lu_id=1)