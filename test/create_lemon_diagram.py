import os
from itertools import combinations
from rdflib import Graph, Namespace

import sys
sys.path.insert(0, '../..')

import FrameNetNLTK

# lemon
fn_nl_ttl_path = 'stats/dfn_0.1.ttl'
output_path = 'stats/dfn_0.1.ttl' + '.gv'

lemon = Graph()
lemon.parse(fn_nl_ttl_path, format='ttl')

FrameNetNLTK.derive_model(fn_in_lemon=lemon,
                          output_path=output_path,
                          verbose=2)

# lemon
fn_nl_ttl_path = 'stats/efn_1.7.ttl'
output_path = 'stats/efn_1.7.ttl' + '.gv'

lemon = Graph()
lemon.parse(fn_nl_ttl_path, format='ttl')

FrameNetNLTK.derive_model(fn_in_lemon=lemon,
                          output_path=output_path,
                          verbose=2)
