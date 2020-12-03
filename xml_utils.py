import os
import shutil

from lxml import etree

from . import path_utils


def strip_lexunit_els_and_save(input_path,
                               output_path):
    parser = etree.XMLParser(remove_blank_text=True)
    doc = etree.parse(input_path, parser)
    root = doc.getroot()

    for lexunit_el in root.findall("{http://framenet.icsi.berkeley.edu}lexUnit"):
        lexunit_el.getparent().remove(lexunit_el)

    els = root.findall("{http://framenet.icsi.berkeley.edu}lexUnit")
    assert len(els) == 0

    doc.write(output_path,
              encoding='utf-8',
              pretty_print=True,
              xml_declaration=True)


def strip_lu_els_and_save(input_path,
                          output_path):
    parser = etree.XMLParser(remove_blank_text=True)
    doc = etree.parse(input_path, parser)
    root = doc.getroot()

    query = '{http://framenet.icsi.berkeley.edu}lu'
    for lu_el in root.findall(query):
        lu_el.getparent().remove(lu_el)

    els = root.findall(query)
    assert len(els) == 0

    doc.write(output_path,
              encoding='utf-8',
              pretty_print=True,
              xml_declaration=True)


def strip_corpus_els_and_save(input_path,
                              output_path,
                              verbose=0):
    parser = etree.XMLParser(remove_blank_text=True)
    doc = etree.parse(input_path, parser)
    root = doc.getroot()

    query = '{http://framenet.icsi.berkeley.edu}corpus'
    for lu_el in root.findall(query):
        lu_el.getparent().remove(lu_el)

    els = root.findall(query)
    assert len(els) == 0

    doc.write(output_path,
              encoding='utf-8',
              pretty_print=True,
              xml_declaration=True)

    if verbose >= 2:
        print(f'removed corpus els and saved it to {output_path}')


def initialize(folder,
               fn_en,
               verbose=0):
    # validate fn_en
    root_en = fn_en.root
    assert os.path.exists(
        root_en), f'Unable to find the root folder on disk for the fn_en object ({root_en}). Please inspect.'

    # create folder
    path_utils.remove_and_create_folder(folder, verbose=verbose)

    # get relevant paths
    paths_your_fn = path_utils.get_relevant_paths(folder, check_if_exists=False)
    paths_fn_en = path_utils.get_relevant_paths(root_en)

    # cp files and folder
    path_utils.remove_and_create_folder(fldr=paths_your_fn['lu_dir'], verbose=verbose)
    path_utils.remove_and_create_folder(fldr=paths_your_fn['frame_dir'], verbose=verbose)

    for label in ['frRelation.xml',
                  'frameIndex.xml',
                  'frameIndex.xsl',
                  'luIndex.xsl',
                  'lexUnit.xsl',
                  'semTypes.xml',
                  'frame.xsl']:
        shutil.copy(src=paths_fn_en[label],
                    dst=paths_your_fn[label])

    # load frame/*xml files and remove lexUnit elements
    for frame, frame_xml in paths_fn_en['frame_to_xml_path'].items():
        output_path = os.path.join(paths_your_fn['frame_dir'],
                                   f'{frame}.xml')
        strip_lexunit_els_and_save(input_path=frame_xml,
                                   output_path=output_path)

    # load luIndex.xml and strip luIndex/lu elements
    strip_lu_els_and_save(input_path=paths_fn_en['luIndex.xml'],
                          output_path=paths_your_fn['luIndex.xml'])

    if verbose:
        print(f'initialized empty FrameNet lexicon at {folder}')


def create_lexeme_els(lexemes):
    order_to_lexeme = {}
    for lexeme in lexemes:
        order_to_lexeme[int(lexeme['order'])] = lexeme

    lexeme_els = []
    for order, lexeme in order_to_lexeme.items():
        lexeme_el = etree.Element('lexeme',
                                  attrib=lexeme)
        lexeme_els.append(lexeme_el)

    return lexeme_els


def create_lu_xml_file(fn_en,
                       your_fn,
                       frame,
                       lu_id,
                       status,
                       lexemes,
                       lemma,
                       pos,
                       definition,
                       lu_type,
                       incorporated_fe=None,
                       optional_lu_attrs={}):
    frame = fn_en.frame_by_name(frame)

    assert len(frame.lexUnit), f'{frame} is not lexicalized in English. Not able to add the LU.'

    # we select the first English LU from the frame that we want to add a new LU to
    # we modify the existing XML file for the English to create the new XML file for the new LU
    for lu_obj in frame.lexUnit.values():
        en_lu_id = lu_obj.ID
        break

    input_path = os.path.join(fn_en.root,
                              fn_en._lu_dir,
                              f'lu{en_lu_id}.xml')

    parser = etree.XMLParser(remove_blank_text=True)
    doc = etree.parse(input_path, parser)
    root = doc.getroot()

    root.set('status', status)
    root.set('POS', pos)
    root.set('name', f'{lemma}.{pos.lower()}')
    root.set('totalAnnotated', '0')
    root.set('ID', str(lu_id))
    root.set('lu_type', lu_type)

    if incorporated_fe is not None:
        root.set('incorporatedFE', incorporated_fe)
    else:
        if 'incorporatedFE' in root.attrib:
            del root.attrib['incorporatedFE']

    for key, value in optional_lu_attrs.items():
        root.set(key, value)

    def_el = root.find('{http://framenet.icsi.berkeley.edu}definition')
    if definition is None:
        definition = ''
    def_el.text = definition

    # update lexemes
    queries = ['{http://framenet.icsi.berkeley.edu}lexeme',
               '{http://framenet.icsi.berkeley.edu}valences',
               '{http://framenet.icsi.berkeley.edu}subCorpus',
               '{http://framenet.icsi.berkeley.edu}semType',
               '{http://framenet.icsi.berkeley.edu}header/{http://framenet.icsi.berkeley.edu}corpus']
    for query in queries:
        for el in root.findall(query):
            el.getparent().remove(el)

    lexeme_els = create_lexeme_els(lexemes)
    for lexeme_el in lexeme_els:
        root.append(lexeme_el)

    output_path = os.path.join(your_fn.root,
                               your_fn._lu_dir,
                               f'lu{lu_id}.xml')
    doc.write(output_path,
              encoding='utf-8',
              pretty_print=True,
              xml_declaration=True)
    return root


def add_lu_el_to_luindex(path_lu_index,
                         frame_id,
                         frame_name,
                         status,
                         lemma,
                         pos,
                         lu_id,
                         lu_type,
                         optional_lu_attrs={}):
    parser = etree.XMLParser(remove_blank_text=True)
    doc = etree.parse(path_lu_index, parser)
    root = doc.getroot()

    lu_el = etree.Element('lu',
                          attrib={
                              'numAnnotInstances': "0",
                              'hasAnnotation': "false",
                              'frameID': str(frame_id),
                              'frameName': frame_name,
                              'status': status,
                              'name': f'{lemma}.{pos.lower()}',
                              'lu_type': lu_type,
                              'ID': str(lu_id)
                          })

    for key, value in optional_lu_attrs.items():
        lu_el.set(key, value)

    root.append(lu_el)

    doc.write(path_lu_index,
              encoding='utf-8',
              pretty_print=True,
              xml_declaration=True)


def add_lu_to_frame_xml_file(your_fn,
                             frame,
                             status,
                             lemma,
                             lemma_id,
                             pos,
                             lu_id,
                             lexemes,
                             provenance,
                             cdate,
                             definition,
                             lu_type,
                             incorporated_fe=None,
                             optional_lu_attrs={}):
    frame_xml_path = os.path.join(your_fn.root,
                                  'frame',
                                  f'{frame}.xml')

    parser = etree.XMLParser(remove_blank_text=True)
    doc = etree.parse(frame_xml_path, parser)
    root = doc.getroot()

    lu_el = etree.Element('lexUnit',
                          attrib={
                              'status': status,
                              'POS': pos,
                              'name': f'{lemma}.{pos.lower()}',
                              'ID': str(lu_id),
                              'lemmaID': str(lemma_id),
                              'cBy': provenance,
                              'cDate': cdate,
                              'lu_type' : lu_type
                          })
    if incorporated_fe is not None:
        lu_el.set('incorporatedFE', incorporated_fe)

    for key, value in optional_lu_attrs.items():
        lu_el.set(key, value)

    def_el = etree.Element('definition')
    if definition is None:
        definition = ''
    def_el.text = definition
    lu_el.append(def_el)

    lu_el.append(etree.Element('sentenceCount', attrib={'annotated': '0', 'total': '0'}))

    lexeme_els = create_lexeme_els(lexemes)
    for lexeme_el in lexeme_els:
        lu_el.append(lexeme_el)

    root.append(lu_el)

    doc.write(frame_xml_path,
              encoding='utf-8',
              pretty_print=True,
              xml_declaration=True)


def remove_lu_xml_file(your_fn,
                       lu_id):
    input_path = os.path.join(your_fn.root,
                              your_fn._lu_dir,
                              f'lu{lu_id}.xml')
    os.remove(input_path)


def remove_lu_el_from_luindex(path_lu_index,
                              lu_id):
    parser = etree.XMLParser(remove_blank_text=True)
    doc = etree.parse(path_lu_index, parser)
    root = doc.getroot()

    query = '{http://framenet.icsi.berkeley.edu}lu'
    els = root.findall(query)

    before = len(els)

    for lu_el in els:
        if lu_el.get('ID') == str(lu_id):
            lu_el.getparent().remove(lu_el)

    els = root.findall(query)
    after = len(els)

    assert before == (after + 1)

    doc.write(path_lu_index,
              encoding='utf-8',
              pretty_print=True,
              xml_declaration=True)


def remove_lexunit_el_from_frame_xml(your_fn,
                                     lu_id):
    lu = your_fn.lu(lu_id)
    frame_name = lu.frame.name

    frame_xml_path = os.path.join(your_fn.root,
                                  'frame',
                                  f'{frame_name}.xml')

    parser = etree.XMLParser(remove_blank_text=True)
    doc = etree.parse(frame_xml_path, parser)
    root = doc.getroot()

    query = '{http://framenet.icsi.berkeley.edu}lexUnit'
    els = root.findall(query)

    before = len(els)

    for lu_el in els:
        if lu_el.get('ID') == str(lu_id):
            lu_el.getparent().remove(lu_el)

    els = root.findall(query)
    after = len(els)

    assert before == (after + 1)

    doc.write(frame_xml_path,
              encoding='utf-8',
              pretty_print=True,
              xml_declaration=True)


def add_annotations_to_nltk_doc(doc_xml_path,
                                sentid_to_annotations,
                                sentid_to_info,
                                corpus_id,
                                doc_id,
                                verbose=0):
    """

    :param sentid_to_annotations:
    :param sentid_to_info:
    :return:
    """
    # load xml file
    parser = etree.XMLParser(remove_blank_text=True)
    doc = etree.parse(doc_xml_path, parser)
    root = doc.getroot()

    num_sents_added = 0
    num_annotations_added = 0

    for sent_id, annotations in sentid_to_annotations.items():

        # add sentence information
        sent_info = sentid_to_info[sent_id]

        sent_el = etree.Element('sentence',
                                attrib={
                                    'corpID' : str(corpus_id),
                                    'docID' : str(doc_id),
                                    'sentNo' : sent_info['sentNo'],
                                    'paragNo' : sent_info['paragNo'],
                                    'aPos' : '0',
                                    'ID' : sent_info['nltk_sent_id'],
                                })
        text_el = etree.Element('text')
        text_el.text = sent_info['sentence']
        sent_el.append(text_el)
        root.append(sent_el)

        num_sents_added += 1

        # add annotations
        for index, annotation in enumerate(annotations):

            if index == 0: # we need to add annotationSet with status="UNANN" for first annotation
                anno_set_el = etree.Element('annotationSet',
                                            attrib={
                                                'cDate' : annotation['cDate'],
                                                'status' : 'UNANN',
                                                'ID' : str(int(annotation['ID'])-1)
                                            })
                penn_layer = etree.Element('layer', attrib={'rank' : '1', 'name' : 'PENN'})
                ner_layer = etree.Element('layer', attrib={'rank' : '1', 'name' : 'NER'})
                wsl_layer = etree.Element('layer', attrib={'rank' : '1', 'name' : 'WSL'})
                anno_set_el.extend([penn_layer, ner_layer, wsl_layer])
                sent_el.append(anno_set_el)


            anno_set_el = etree.Element('annotationSet',
                                        attrib={
                                            'cDate': annotation['cDate'],
                                            'luID': annotation['luID'],
                                            'luName' : annotation['luName'],
                                            'frameID' : annotation['frameID'],
                                            'frameName' : annotation['frameName'],
                                            'status' : annotation['status'],
                                            'ID' : annotation['ID']
                                        })

            target_layer = etree.Element('layer', attrib={'rank': '1', 'name': 'Target'})

            for start_end_offsets in annotation['pred_offsets']:
                label_el = etree.Element('label', attrib={
                    'cBy' : annotation['cBy'],
                    'start' : str(start_end_offsets['start_offset_in_sent']),
                    'end' : str(start_end_offsets['end_offset_in_sent']),
                    'name' : 'Target'
                })
                target_layer.append(label_el)
            fe_layer = etree.Element('layer', attrib={'rank': '1', 'name': 'FE'})
            gf_layer = etree.Element('layer', attrib={'rank': '1', 'name': 'GF'})
            pt_layer = etree.Element('layer', attrib={'rank' : '1', 'name' : 'PT'})
            other_layer = etree.Element('layer', attrib={'rank' : '1', 'name' : 'Other'})
            sent_layer = etree.Element('layer', attrib={'rank' : '1', 'name' : 'Sent'})
            verb_layer = etree.Element('layer', attrib={'rank' : '1', 'name' : 'Verb'})

            anno_set_el.extend([target_layer, fe_layer, gf_layer, pt_layer, other_layer, sent_layer, verb_layer])
            sent_el.append(anno_set_el)
            num_annotations_added += 1

    # write to disk
    doc.write(doc_xml_path,
              encoding='utf-8',
              pretty_print=True,
              xml_declaration=True)

    if verbose >= 2:
        print()
        print(f'added {num_sents_added} sentences')
        print(f'added {num_annotations_added} annotations')
        print(f'written to {doc_xml_path}')