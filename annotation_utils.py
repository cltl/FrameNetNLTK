import os
import shutil

from lxml import etree
from rdflib import Graph

from .path_utils import get_relevant_paths
from .xml_utils import strip_corpus_els_and_save
from .xml_utils import add_annotations_to_nltk_doc
from .naf_utils import get_sentid_to_info
from .naf_utils import load_annotations_from_naf
from .rdf_utils import load_graph


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


    if verbose >= 5:
        print()
        print(f'name and description: {name_to_description_and_id}')
        print(f'is a new entry for type {type}: {new}')

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


def create_document(example_doc,
                    output_path,
                    corpus_id,
                    corpus_name,
                    corpus_description,
                    doc_id,
                    doc_name,
                    doc_description,
                    verbose=0):
    """
    <header>
        <corpus description="Texts from WikiMedia--WikiNews and Wikipedia" name="WikiTexts" ID="246">
            <document description="Fires_4" name="Fires_4" ID="25619"/>
        </corpus>
    </header>

    :param example_doc:
    :param corpus_id:
    :param corpus_name:
    :param corpus_description:
    :param doc_id:
    :param doc_name:
    :param doc_description:
    :param verbose:
    :return:
    """
    # load example_doc and strip existing elements
    parser = etree.XMLParser(remove_blank_text=True)
    doc = etree.parse(example_doc, parser)

    root = doc.getroot()
    for child_el in root.getchildren():
        child_el.getparent().remove(child_el)

    els = root.getchildren()
    assert len(els) == 0

    # add header
    header_el = etree.Element('header')
    corpus_el = etree.Element('corpus',
                              attrib={
                                  'description' : corpus_description,
                                  'name' : corpus_name,
                                  'ID' : str(corpus_id)
                              })
    doc_el = etree.Element('document',
                           attrib={
                               'description' : doc_name,
                               'name' : doc_name,
                               'ID' : str(doc_id)
                           })

    corpus_el.append(doc_el)
    header_el.append(corpus_el)
    root.append(header_el)

    # save to disk
    doc.write(output_path,
              encoding='utf-8',
              pretty_print=True,
              xml_declaration=True)

    if verbose >= 2:
        print(f'created new document at {output_path}')



def get_sent_id(corpus_id,
                doc_id,
                naf_sent_id,
                fill_width=8):
    """

    :param corpus_id:
    :param doc_id:
    :param naf_sent_id:
    :return:
    """
    nltk_sent_id = ''

    for id_ in [corpus_id, doc_id, naf_sent_id]:
        id_filled = str(id_).zfill(fill_width)

        nltk_sent_id += id_filled

    return nltk_sent_id


def remove_corpus(corpus_name):
    # TODO: what does this actually mean?
    pass

def remove_document(fulltext_xml_path,
                    doc_id,
                    doc_path,
                    verbose=0):

    # remove document
    os.remove(doc_path)
    if verbose >= 2:
        print(f'removed existing document from {doc_path}')

    # remove document from fulltext_xml index
    parser = etree.XMLParser(remove_blank_text=True)
    doc = etree.parse(fulltext_xml_path, parser)

    query = '{http://framenet.icsi.berkeley.edu}corpus/{http://framenet.icsi.berkeley.edu}document'
    doc_els = doc.findall(query)
    els_to_remove = []
    for doc_el in doc_els:
        doc_el_id = doc_el.get('ID')
        if doc_el_id == str(doc_id):
            els_to_remove.append(doc_el)

    assert len(els_to_remove) == 1, f'expected to find one document el to remove from fulltextindex.xml, found {len(els_to_remove)}'
    for el_to_remove in els_to_remove:
        el_to_remove.getparent().remove(el_to_remove)

    doc.write(fulltext_xml_path,
              encoding='utf-8',
              pretty_print=True,
              xml_declaration=True)



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
    if os.path.exists(your_paths['fulltext_dir']):
        if start_from_scratch:
            shutil.rmtree(your_paths['fulltext_dir'])
            if verbose >= 2:
                print(f'removed {your_paths["fulltext_dir"]}')

    if not os.path.exists(your_paths['fulltext_dir']):
        os.mkdir(your_paths['fulltext_dir'])
        if verbose >= 2:
            print(f'created folder fulltext at {your_paths["fulltext_dir"]}')

    keys = ['fulltextIndex.xsl', 'fullText.xsl']
    for key in keys:
        if os.path.exists(your_paths[key]):
            if start_from_scratch:
                os.remove(your_paths['fulltextIndex.xsl'])
                if verbose >= 2:
                    print(f'removed {your_paths[key]}')

        if not os.path.exists(your_paths[key]):
            shutil.copy(src=en_paths[key],
                        dst=your_paths[key])
            if verbose >= 2:
                print(f'copied {en_paths[key]} to {your_paths[key]}')

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
                                path_to_your_fn_in_lemon,
                                fn_en,
                                premon_nt,
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
    :param rdflib.graph.Graph premon: use FrameNetNLTK.premon_nt

    :param str corpus_name: abbreviated name of the corpus, e.g., HDD, which will be the value
    of the attribute "name" of element "corpus" in the file fulltextIndex.xml
    :param str corpus_description: a longer description of the corpus, e.g., HistoricalDistanceData, which will be the value
    of the attribute "description" of element "corpus" in the file fulltextIndex.xml
    :param str naf_path: path to a NAF file in version 3.1
    :param bool overwrite: if True, remove the document if it exists and add only information from the provided file
    """
    your_paths = get_relevant_paths(root=your_fn._root, check_if_exists=False)
    en_paths = get_relevant_paths(root=fn_en._root, check_if_exists=True)

    premon = load_graph(path=premon_nt, format='nt')
    your_fn_in_lemon = load_graph(path=path_to_your_fn_in_lemon, format='ttl')

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
    output_path = os.path.join(your_paths['fulltext_dir'],
                               f'{corpus_name}__{doc_name}.xml')

    doc_id, new_doc = generate_id(fulltext_xml_path=your_paths['fulltextIndex.xml'],
                                  type='document',
                                  the_name=doc_name,
                                  the_description=doc_name,
                                  verbose=verbose)

    # remove the document if it exists and the user wants to overwrite
    if all([not new_doc,
            overwrite,
            ]):
        remove_document(fulltext_xml_path=your_paths['fulltextIndex.xml'],
                        doc_id=doc_id,
                        doc_path=output_path,
                        verbose=verbose)
        new_doc = True # since the document was removed, it is a now a new document


    if new_doc:
        add_document_to_index(fulltext_xml_path=your_paths['fulltextIndex.xml'],
                              corpus_id=corpus_id,
                              doc_name=doc_name,
                              doc_description=doc_name,
                              verbose=verbose)

    if new_doc:
        create_document(example_doc=en_paths['example_document'],
                        output_path=output_path,
                        corpus_id=corpus_id,
                        corpus_name=corpus_name,
                        corpus_description=corpus_description,
                        doc_id=doc_id,
                        doc_name=doc_name,
                        doc_description=doc_name,
                        verbose=verbose)

    # load NAF annotations
    naf_sentid_to_info = get_sentid_to_info(naf_path=naf_path)

    # update with sentence identifier (verify that identifier is new)
    for naf_sentid, sent_info in naf_sentid_to_info.items():
        nltk_sent_id = get_sent_id(corpus_id=corpus_id,
                                   doc_id=doc_id,
                                   naf_sent_id=naf_sentid,
                                   fill_width=8)
        sent_info['nltk_sent_id'] = nltk_sent_id

    # load annotations from NAF
    sentid_to_annotations = load_annotations_from_naf(your_fn=your_fn,
                                                      path_to_your_fn_in_lemon=path_to_your_fn_in_lemon,
                                                      naf_path=naf_path,
                                                      doc_id=doc_id,
                                                      premon=premon)


    # update annotations
    add_annotations_to_nltk_doc(doc_xml_path=output_path,
                                sentid_to_annotations=sentid_to_annotations,
                                sentid_to_info=naf_sentid_to_info,
                                corpus_id=corpus_id,
                                doc_id=doc_id,
                                verbose=verbose)








