import os
import shutil

from lxml import etree

from .path_utils import get_relevant_paths
from .xml_utils import strip_corpus_els_and_save


def generate_id(fulltext_xml_path,
                type,
                the_name,
                the_description,
                verbose=0):
    """

    :param nltk.corpus.reader.framenet.FramenetCorpusReader your_fn: a FrameNet in the NLTK format
    :param str type: corpus | document
    :param str the_name: value of attribute name
    :param str the_description: value of attribute description
    :param verbose:

    :rtype: int
    :return: the corpus identifier
    """
    name_to_description_and_id = {}
    new = False

    the_types = {'corpus', 'document'}
    assert type in the_types, f'provided type ({type}) not part of accepted set: {the_types}'

    if type == 'corpus':
        query = '{http://framenet.icsi.berkeley.edu}corpus'
    elif type == 'document':
        query = '{http://framenet.icsi.berkeley.edu}corpus/{http://framenet.icsi.berkeley.edu}document'

    doc = etree.parse(fulltext_xml_path)

    for el in doc.findall(query):
        name = el.get('name')
        description = el.get('description')
        id_ = int(el.get('ID'))

        assert name not in name_to_description_and_id, f'{name} occurs more than once. Please inspect.'
        name_to_description_and_id[name] = (description, id_)

    if verbose >= 2:
        print(f'found {len(name_to_description_and_id)} of type {type} in your FrameNet.')

    if the_name in name_to_description_and_id:
        description, id_ = name_to_description_and_id[the_name]
        error_message = f'corpus name exists, but provided description is different. Please inspect {name_to_description_and_id}'
        assert description == the_description, error_message

        the_id = id_
    else:
        ids = [id_
               for (description, id_) in name_to_description_and_id.values()]

        if ids:
            the_id = max(ids) + 1
        else:
            the_id = 1
        new = True

    return the_id, new

def add_corpus_to_index(fulltext_xml_path,
                        corpus_name,
                        corpus_description,
                        corpus_id,
                        verbose=0):
    parser = etree.XMLParser(remove_blank_text=True)
    doc = etree.parse(fulltext_xml_path, parser)

    corpus_el = etree.Element('corpus',
                              attrib={
                                  'description' : corpus_description,
                                  'name' : corpus_name,
                                  'ID' : str(corpus_id)
                              })

    root = doc.getroot()
    root.append(corpus_el)

    doc.write(fulltext_xml_path,
              encoding='utf-8',
              pretty_print=True,
              xml_declaration=True)


def add_document_to_index(fulltext_xml_path,
                          corpus_id,
                          doc_name,
                          doc_description,
                          verbose=0):
    parser = etree.XMLParser(remove_blank_text=True)
    doc = etree.parse(fulltext_xml_path, parser)

    query = f'{{http://framenet.icsi.berkeley.edu}}corpus[@ID="{corpus_id}"]'
    corpus_el = doc.find(query)

    doc_el = etree.Element('document',
                              attrib={
                                  'description' : doc_name,
                                  'name' : doc_description,
                                  'ID' : str(corpus_id)
                              })

    corpus_el.append(doc_el)

    doc.write(fulltext_xml_path,
              encoding='utf-8',
              pretty_print=True,
              xml_declaration=True)


def remove_corpus(corpus_name):
    # TODO: what does this actually mean?
    pass

def add_document(corpus_name,
                 document_name):
    # TODO: check if document exists
    pass

def remove_document(corpus_name,
                    document_name):
    # TODO: what does this entail?
    pass

def add_sentence(corpus,
                 document,
                 sentence):
    pass

def remove_sentence(corpus,
                    document,
                    sentence): pass

def add_annotation_set(corpus,
                       document,
                       sentence,
                       annotation_info): pass

def remove_annotation_set(corpus,
                          document,
                          sentence,
                          annotation_info): pass


def setup_fulltext(your_paths,
                   en_paths,
                   start_from_scratch=False,
                   verbose=0):
    """

    :param your_paths:
    :param en_paths:
    :return:
    """
    if os.path.exists(your_paths['fulltextIndex.xsl']):
        if start_from_scratch:
            os.remove(your_paths['fulltextIndex.xsl'])
            if verbose >= 2:
                print(f'removed {your_paths["fulltextIndex.xsl"]}')

    if not os.path.exists(your_paths['fulltextIndex.xsl']):
        shutil.copy(src=en_paths['fulltextIndex.xsl'],
                    dst=your_paths['fulltextIndex.xsl'])
        if verbose >= 2:
            print(f'copied {en_paths["fulltextIndex.xsl"]} to {your_paths["fulltextIndex.xsl"]}')


    if os.path.exists(your_paths['fulltext_dir']):
        if start_from_scratch:
            shutil.rmtree(your_paths['fulltext_dir'])
            if verbose >= 2:
                print(f'removed {your_paths["fulltext_dir"]}')

    if not os.path.exists(your_paths['fulltext_dir']):
        os.mkdir(your_paths['fulltext_dir'])
        if verbose >= 2:
            print(f'created folder fulltext at {your_paths["fulltext_dir"]}')

    # strip fulltextIndex.xml and copy to your FrameNet
    if os.path.exists(your_paths['fulltextIndex.xml']):
        if start_from_scratch:
            os.remove(your_paths['fulltextIndex.xml'])

    if not os.path.exists(your_paths['fulltextIndex.xml']):
        if any([not os.path.exists(your_paths['fulltextIndex.xml']),
                start_from_scratch]):
            strip_corpus_els_and_save(input_path=en_paths['fulltextIndex.xml'],
                                      output_path=your_paths['fulltextIndex.xml'],
                                      verbose=verbose)


def add_annotations_from_naf_31(your_fn,
                                fn_en,
                                corpus_name,
                                corpus_description,
                                naf_path,
                                overwrite=False,
                                start_from_scratch=False,
                                verbose=0):
    """
    Add annotations from NAF 3.1

    :param nltk.corpus.reader.framenet.FramenetCorpusReader your_fn: a FrameNet in the NLTK format
    :param nltk corpus.reader.framenet.FramenetCorpusReader fn_en: English FrameNet in the NLTK format

    :param str corpus_name: abbreviated name of the corpus, e.g., HDD, which will be the value
    of the attribute "name" of element "corpus" in the file fulltextIndex.xml
    :param str corpus_description: a longer description of the corpus, e.g., HistoricalDistanceData, which will be the value
    of the attribute "description" of element "corpus" in the file fulltextIndex.xml
    :param str naf_path: path to a NAF file in version 3.1
    :param bool overwrite: if True, remove the document if it exists and add only information from the provided file
    """
    your_paths = get_relevant_paths(root=your_fn._root, check_if_exists=False)
    en_paths = get_relevant_paths(root=fn_en._root, check_if_exists=True)

    setup_fulltext(your_paths=your_paths,
                   en_paths=en_paths,
                   start_from_scratch=start_from_scratch,
                   verbose=verbose)

    # corpus in index
    corpus_id, new_corpus = generate_id(fulltext_xml_path=your_paths['fulltextIndex.xml'],
                                 type='corpus',
                                 the_name=corpus_name,
                                 the_description=corpus_description,
                                 verbose=verbose)

    if new_corpus:
        add_corpus_to_index(fulltext_xml_path=your_paths['fulltextIndex.xml'],
                            corpus_name=corpus_name,
                            corpus_description=corpus_description,
                            corpus_id=corpus_id,
                            verbose=verbose)


    # document in index
    doc_name = os.path.basename(naf_path)
    doc_id, new_doc = generate_id(fulltext_xml_path=your_paths['fulltextIndex.xml'],
                                  type='document',
                                  the_name=corpus_name,
                                  the_description=corpus_name,
                                  verbose=verbose)

    if new_doc:
        add_document_to_index(fulltext_xml_path=your_paths['fulltextIndex.xml'],
                              corpus_id=corpus_id,
                              doc_name=doc_name,
                              doc_description=doc_name,
                              verbose=verbose)

    # annotation document




