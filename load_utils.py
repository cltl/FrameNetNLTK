from nltk.corpus.reader.framenet import FramenetCorpusReader



def load(folder):
    """

    :param str folder:
    :return:
    """
    your_fn = FramenetCorpusReader(folder, ['frameIndex.xml'])
    return your_fn