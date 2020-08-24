from statistics import mean
from collections import defaultdict
import operator
import pandas


def get_frame_stats_df(your_fn):
    """
    compute three metrics:
    - total number of frames
    - number of lexical frames
    - number of non-lexical frames

    :param nltk.corpus.reader.framenet.FramenetCorpusReader your_fn: your loaded NLTK FrameNet

    :rtype: pandas.core.frame.DataFrame
    :return: dataframe with two columns, one row per metric
    """
    frame_cat_to_freq = {
        'number of lexical frames': 0,
        'number of non-lexical frames': 0,
        'total number of frames': 0
    }

    for frame in your_fn.frames():

        frame_cat_to_freq['total number of frames'] += 1

        if len(frame.lexUnit) == 0:
            frame_cat_to_freq['number of non-lexical frames'] += 1
        elif len(frame.lexUnit) >= 1:
            frame_cat_to_freq['number of lexical frames'] += 1
        else:
            raise Exception(f'the number of LUs is not a positive number: {frame}.')

    assert frame_cat_to_freq['total number of frames'] == (
                frame_cat_to_freq['number of non-lexical frames'] + frame_cat_to_freq['number of lexical frames'])

    list_of_lists = []
    headers = ['Metric', 'Frequency']
    for key, value in frame_cat_to_freq.items():
        one_row = [key, value]
        list_of_lists.append(one_row)

    df = pandas.DataFrame(list_of_lists, columns=headers)

    return df


def get_lu_stats_df(your_fn):
    """
    Compute two metrics about LUs:
    - total number of LUs
    - LUs / lexical frame

    :param nltk.corpus.reader.framenet.FramenetCorpusReader your_fn: your loaded NLTK FrameNet

    :rtype: pandas.core.frame.DataFrame
    :return: dataframe with two columns, one row per metric
    """
    lexical_frame_to_num_lus = {}

    for frame in your_fn.frames():
        if len(frame.lexUnit) >= 1:
            lexical_frame_to_num_lus[frame.name] = len(frame.lexUnit)

    lus_per_lexical_frame = mean(lexical_frame_to_num_lus.values())

    list_of_lists = []
    headers = ['Metric', 'Value']

    one_row = ['total number of LUs', str(len(your_fn.lus()))]
    list_of_lists.append(one_row)

    one_row = ['LUs per lexical frame', round(lus_per_lexical_frame, 1)]
    list_of_lists.append(one_row)

    df = pandas.DataFrame(list_of_lists, columns=headers)

    return df


def get_lu_per_pos_stats_df(your_fn):
    """
    create table in which the number of LUs per POS are shown

    :param nltk.corpus.reader.framenet.FramenetCorpusReader your_fn: your loaded NLTK FrameNet

    :rtype: pandas.core.frame.DataFrame
    :return: dataframe with two columns, one row per metric
    """
    pos_to_freq = defaultdict(int)

    for lu in your_fn.lus():
        pos_to_freq[lu.POS] += 1

    list_of_lists = []
    headers = ['Part of speech tag', 'Number of LUs']
    for pos, freq in sorted(pos_to_freq.items(),
                            key=operator.itemgetter(1),
                            reverse=True):
        one_row = [pos, freq]
        list_of_lists.append(one_row)

    df = pandas.DataFrame(list_of_lists, columns=headers)

    return df



def get_lexeme_stats_df(your_fn):
    """
    create table in which the number of lexemes

    :param nltk.corpus.reader.framenet.FramenetCorpusReader your_fn: your loaded NLTK FrameNet

    :rtype: pandas.core.frame.DataFrame
    :return: dataframe with two columns, one row per metric
    """
    num_lexemes_to_freq = defaultdict(int)

    for lu in your_fn.lus():
        num_lexemes = len(lu.lexemes)
        num_lexemes_to_freq[num_lexemes] += 1

    list_of_lists = []
    headers = ['Number of lexemes', 'LUs']

    for num_lexemes, freq in sorted(num_lexemes_to_freq.items()):
        one_row = [num_lexemes, freq]
        list_of_lists.append(one_row)

    df = pandas.DataFrame(list_of_lists, columns=headers)

    return df


def get_ambiguity_df(your_fn):
    """
    create table to show the ambiguity metrics of the framenet

    :param nltk.corpus.reader.framenet.FramenetCorpusReader your_fn: your loaded NLTK FrameNet

    :rtype: pandas.core.frame.DataFrame
    :return: dataframe with two columns, one row per metric
    """
    lemma_pos_to_frames = defaultdict(set)

    for lu in your_fn.lus():
        frame_id = lu.frame.ID
        lemma_pos_to_frames[lu.name].add(frame_id)

    list_of_lists = []
    headers = ['Lemma - pos', 'Num_evoked_frames']
    for lemma_pos, frames in lemma_pos_to_frames.items():
        one_row = [lemma_pos, len(frames)]
        list_of_lists.append(one_row)

    df = pandas.DataFrame(list_of_lists, columns=headers)

    metrics = [('Minimum ambiguity', 'min'),
               ('Mean ambiguity', 'mean'),
               ('Maximum ambiguity', 'max')]

    list_of_lists = []
    headers = ['Metric', 'Value']
    for label, function_name in metrics:
        function = getattr(df, function_name)
        value = function().Num_evoked_frames
        one_row = [label, round(value, 1)]
        list_of_lists.append(one_row)

    stats_df = pandas.DataFrame(list_of_lists, columns=headers)

    return stats_df





def get_stats_html(your_fn,
                   html_path,
                   functions=(('Frame', 'get_frame_stats_df'),
                              ('LUs', 'get_lu_stats_df'),
                              ('LUs per POS', 'get_lu_per_pos_stats_df'),
                              ('Lexemes per LU', 'get_lexeme_stats_df'),
                              ('Ambiguity', 'get_ambiguity_df')),
                   verbose=0):
    """
    Combine
    :param nltk.corpus.reader.framenet.FramenetCorpusReader your_fn: your loaded NLTK FrameNet
    :param str html_path: path to store your html page with the descriptive statistics
    :param tuple functions: tuple of tuples, each containing two strings:
    -the first string is the header for the table
    -the second string is the function to call as part of this Python module (stats_utils.py)
    """
    components = []

    html_start = '<html>\n<body>\n'
    components.append(html_start)

    for title, function_name in functions:
        header = f'<h2>{title}</h2>'
        components.append(header)

        function = globals()[function_name]
        df = function(your_fn)
        html_table = df.to_html(index=False,
                                border=0,
                                justify="center")
        components.append(html_table)

    html_end = '</body>\n</html>'
    components.append(html_end)

    html = ''.join(components)

    with open(html_path, 'w') as outfile:
        outfile.write(html)

    if verbose >= 1:
        print(f'written the descriptive statistics to {html_path}')