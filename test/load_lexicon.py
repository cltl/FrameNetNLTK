import sys

sys.path.insert(0, '../..')
from FrameNetNLTK import load

my_fn = load(folder='test_lexicon',
             verbose=2)


for annotation in my_fn.annotations():
    print(annotation)