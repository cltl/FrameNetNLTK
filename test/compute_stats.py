import sys
sys.path.insert(0, '../..')
from FrameNetNLTK import load, get_frame_stats_df, get_lu_stats_df, get_lu_per_pos_stats_df, get_lexeme_stats_df, get_ambiguity_df
from FrameNetNLTK import get_stats_html

my_fn = load('test_lexicon')

frame_df = get_frame_stats_df(my_fn)

print(frame_df)

lu_stats_df = get_lu_stats_df(my_fn)

print(lu_stats_df)

lu_per_pos_stats_df = get_lu_per_pos_stats_df(my_fn)

print(lu_per_pos_stats_df)

lexeme_stats_df = get_lexeme_stats_df(my_fn)

print(lexeme_stats_df)

ambiguity_df = get_ambiguity_df(my_fn)

print(ambiguity_df)

get_stats_html(your_fn=my_fn,
               html_path='stats/descriptive_statistics.html')