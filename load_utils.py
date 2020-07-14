from nltk.corpus.reader.framenet import FramenetCorpusReader


def load(folder, verbose=0):
    """

    :param verbose:
    :param str folder:
    :return:
    """
    your_fn = FramenetCorpusReader(folder, ['frameIndex.xml'])

    if verbose >= 1:
        print(f'loaded FrameNet lexicon from: {folder}')

    return your_fn
