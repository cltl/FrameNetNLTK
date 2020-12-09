import sys

from rdflib import Graph

sys.path.insert(0, '../..')
import FrameNetNLTK

def load_nt_graph(nt_path):
    g = Graph()
    with open(nt_path, 'rb') as infile:
        g.parse(file=infile, format='nt')

    return g


frame_uri = 'http://premon.fbk.eu/resource/fn17-change_of_leadership'
fe_label = 'Function'

premon = load_nt_graph(nt_path=FrameNetNLTK.premon_nt)

query = """SELECT ?o WHERE {
         ?o <http://www.w3.org/2000/01/rdf-schema#label> "%s" . 
         <%s> <http://premon.fbk.eu/ontology/core#semRole> ?o
    }"""
the_query = query % (fe_label, frame_uri)

results = premon.query(the_query)

labels = set()
for result in results:
    print(result)
    label = str(result.asdict()['o'])
    labels.add(label)

assert len(labels) == 1, f'expected one label for frame ({frame_uri}) with FE label ({fe_label}), got {labels}'

