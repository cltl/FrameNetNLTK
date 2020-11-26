import sys
import os
sys.path.insert(0, '../..')
import FrameNetNLTK
from FrameNetNLTK import load, convert_to_lemon


my_fn = load(folder='test_lexicon',
             verbose=2)


output_path = os.path.join(os.getcwd(),
                           'stats',
                           'lemon.nt')

convert_to_lemon(lemon=FrameNetNLTK.lemon,
                 premon_nt_path=FrameNetNLTK.premon_nt,
                 ontolex=FrameNetNLTK.ontolex,
                 fn_pos_to_lexinfo=FrameNetNLTK.fn_pos_to_lexinfo,
                 your_fn=my_fn,
                 namespace='http://rdf.cltl.nl/dfn/',
                 language='nld',
                 major_version=0,
                 minor_version=1,
                 output_path=output_path,
                 verbose=5)