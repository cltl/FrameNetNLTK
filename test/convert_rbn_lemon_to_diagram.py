from rdflib import Graph

import sys
sys.path.insert(0, '../..')

import FrameNetNLTK

# lemon
rbn_ttl_path = 'stats/rbn_1.0.ttl'
output_path = rbn_ttl_path + '.gv'

lemon = Graph()
lemon.parse(rbn_ttl_path, format='ttl')

FrameNetNLTK.derive_model(fn_in_lemon=lemon,
                          output_path=output_path,
                          verbose=4)


