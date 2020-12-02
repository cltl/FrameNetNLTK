import sys

sys.path.insert(0, '..')
sys.path.insert(0, '../..')
from nltk.corpus import framenet as fn
from FrameNetNLTK import add_annotations_from_naf_31
from FrameNetNLTK import load


naf_path = 'test_naf_files/predicate_in_compound.naf'
corpus_name = 'HDD'
corpus_description = 'HistoricalDistanceData'

my_fn = load(folder='test_lexicon',
             verbose=2)

add_annotations_from_naf_31(your_fn=my_fn,
                            fn_en=fn,
                            corpus_name=corpus_name,
                            corpus_description=corpus_description,
                            naf_path=naf_path,
                            overwrite=True,
                            start_from_scratch=True,
                            verbose=2)


my_fn = load(folder='test_lexicon',
             verbose=2)

#for annotation in my_fn.annotations():
#    print(annotation)