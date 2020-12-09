import sys
import os
sys.path.insert(0, '../..')
import FrameNetNLTK
from FrameNetNLTK import load, convert_to_lemon


my_fn = load(folder='test_lexicon',
             verbose=2)


output_path = os.path.join(os.getcwd(),
                           'stats',
                           'dfn_0.1.ttl')

convert_to_lemon(lemon=FrameNetNLTK.lemon,
                 premon_nt_path=FrameNetNLTK.premon_nt,
                 ontolex=FrameNetNLTK.ontolex,
                 fn_pos_to_lexinfo=FrameNetNLTK.fn_pos_to_lexinfo,
                 your_fn=my_fn,
                 namespace='http://rdf.cltl.nl/dfn/',
                 namespace_prefix='dfn',
                 language='nld',
                 major_version=0,
                 minor_version=1,
                 output_path=output_path,
                 verbose=4)


output_path = os.path.join(os.getcwd(),
                           'stats',
                           'efn_1.7.ttl')

#convert_to_lemon(lemon=FrameNetNLTK.lemon,
#                 premon_nt_path=FrameNetNLTK.premon_nt,
#                 ontolex=FrameNetNLTK.ontolex,
#                 fn_pos_to_lexinfo=FrameNetNLTK.fn_pos_to_lexinfo,
#                 your_fn=my_fn,
#                 namespace='http://rdf.cltl.nl/efn/',
#                 namespace_prefix='efn',
#                 language='eng',
#                 major_version=1,
#                 minor_version=7,
#                 output_path=output_path,
#                 verbose=4)