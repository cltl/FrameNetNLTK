import sys
import os
sys.path.insert(0, '../..')
import FrameNetNLTK
from FrameNetNLTK import convert_rbn_to_lemon


output_path = os.path.join(os.getcwd(),
                           'stats',
                           'rbn_1.0.ttl')

convert_rbn_to_lemon(namespace='http://rdf.cltl.nl/rbn/',
                     lemon=FrameNetNLTK.lemon,
                     major_version=1,
                     minor_version=0,
                     rbn_pos_to_lexinfo=FrameNetNLTK.rbn_pos_to_lexinfo,
                     language='nld',
                     output_path=output_path,
                     verbose=2)

