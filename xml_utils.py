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


def initialize(folder,
               fn_en,
               verbose=0):

    # validate fn_en
    root_en = fn_en._root
    assert os.path.exists(root_en), f'Unable to find the root folder on disk for the fn_en object ({root_en}). Please inspect.'

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
                       incorporated_fe=None,
                       optional_lu_attrs={}):

    frame = fn_en.frame_by_name(frame)

    assert len(frame.lexUnit), f'{frame} is not lexicalized in English. Not able to add the LU.'

    # we select the first English LU from the frame that we want to add a new LU to
    # we modify the existing XML file for the English to create the new XML file for the new LU
    for lu_obj in frame.lexUnit.values():
        en_lu_id = lu_obj.ID
        break

    input_path = os.path.join(fn_en._root,
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
               '{http://framenet.icsi.berkeley.edu}header/{http://framenet.icsi.berkeley.edu}corpus']
    for query in queries:
        for el in root.findall(query):
            el.getparent().remove(el)

    lexeme_els = create_lexeme_els(lexemes)
    for lexeme_el in lexeme_els:
        root.append(lexeme_el)

    root.append(etree.Element('valences'))
    subcorpus_el = etree.Element('subCorpus', attrib={'name': 'manually-added'})
    root.append(subcorpus_el)

    output_path=os.path.join(your_fn._root,
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
                         optional_lu_attrs={}):
    parser = etree.XMLParser(remove_blank_text=True)
    doc = etree.parse(path_lu_index, parser)
    root = doc.getroot()

    lu_el = etree.Element('lu',
                          attrib={
                            'numAnnotInstances' : "0",
                            'hasAnnotation' : "false",
                            'frameID' : str(frame_id),
                            'frameName' : frame_name,
                            'status' : status,
                            'name' : f'{lemma}.{pos.lower()}',
                            'ID' : str(lu_id)
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
                             incorporated_fe=None,
                             optional_lu_attrs={}):
    frame_xml_path = os.path.join(your_fn._root,
                                  'frame',
                                  f'{frame}.xml')

    parser = etree.XMLParser(remove_blank_text=True)
    doc = etree.parse(frame_xml_path, parser)
    root = doc.getroot()

    lu_el = etree.Element('lexUnit',
                          attrib={
                              'status' : status,
                              'POS' : pos,
                              'name' : f'{lemma}.{pos.lower()}',
                              'ID' : str(lu_id),
                              'lemmaID' : str(lemma_id),
                              'cBy' : provenance,
                              'cDate' : cdate,
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

    lu_el.append(etree.Element('sentenceCount', attrib={'annotated' : '0', 'total' : '0'}))

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
    input_path = os.path.join(your_fn._root,
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

    assert before == (after+1)

    doc.write(path_lu_index,
              encoding='utf-8',
              pretty_print=True,
              xml_declaration=True)


def remove_lexunit_el_from_frame_xml(your_fn,
                                     lu_id):

    lu = your_fn.lu(lu_id)
    frame_name = lu.frame.name

    frame_xml_path = os.path.join(your_fn._root,
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



