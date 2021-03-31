from collections import defaultdict
from datetime import datetime
import os

from lxml import etree
import nltk

from nltk.corpus import framenet as fn_en

from .rdf_utils import get_rdf_label, get_lu_identifier, load_graph



def get_sentence(wf_els):
    tokens = [wf_els[0].text]
    for prev_wf_el, cur_wf_el in zip(wf_els[:-1], wf_els[1:]):
        prev_start = int(prev_wf_el.get('offset'))
        prev_end = prev_start + int(prev_wf_el.get('length'))

        cur_start = int(cur_wf_el.get('offset'))

        delta = cur_start - prev_end  # how many characters are between current token and previous token?

        # no chars between two token (for example with a dot .)
        if delta == 0:
            trailing_chars = ''
        # 1 or more characters between tokens -> n spaces added
        if delta >= 1:
            trailing_chars = ' ' * delta
        elif delta < 0:
            raise AssertionError(f'please check the offsets of {prev_wf_el.text} and {cur_wf_el.text} (delta of {delta})')

        tokens.append(trailing_chars + cur_wf_el.text)

    raw_text = ''.join(tokens)
    return raw_text


def get_sentid_to_info(naf_path):
    """

    :param naf_path:
    :return:
    """
    parser = etree.XMLParser(remove_blank_text=True, strip_cdata=False)
    doc = etree.parse(naf_path, parser)

    sentid_to_info = {}

    for wf_el in doc.xpath('text/wf'):

        sent_id = int(wf_el.get('sent'))

        if sent_id not in sentid_to_info: # I assume this is the first wf_el of the sent
            sentid_to_info[sent_id] = {
                'wf_els' : [],
                'id_to_el' : {},
                'paragNo' : '0',
                'sentNo' : str(sent_id),
                'sent_offset_start' : int(wf_el.get('offset'))
            }

        sentid_to_info[sent_id]['wf_els'].append(wf_el)

        sentid_to_info[sent_id]['id_to_el'][wf_el.get('id')] = wf_el
        for subtoken_el in wf_el.xpath('subtoken'):
            sentid_to_info[sent_id]['id_to_el'][subtoken_el.get('id')] = subtoken_el

    for sent_id, info in sentid_to_info.items():
        sentence = get_sentence(wf_els=info['wf_els'])
        info['sentence'] = sentence

    return sentid_to_info


def string_to_datetime_obj(timestamp):
    return datetime.strptime(timestamp, "%Y-%m-%dT%H:%M:%S")



def get_markable_id_to_info(doc,
                            naf_path):
    """

    :param doc:
    :return:
    """
    wfid_to_sentid = {}
    for wf_el in doc.xpath('text/wf'):
        sent_id = int(wf_el.get('sent'))
        wfid_to_sentid[wf_el.get('id')] = sent_id
        for subtoken_el in wf_el.xpath('subtoken'):
            wfid_to_sentid[subtoken_el.get('id')] = sent_id

    tid_to_wfid = {}
    for term_el in doc.xpath('terms/term'):
        tid = term_el.get('id')
        for target_el in term_el.xpath('span/target'):
            tid_to_wfid[tid] = [target_el.get('id')]
        for comp_el in term_el.xpath('component'):
            comp_id = comp_el.get('id')
            for target_el in comp_el.xpath('span/target'):
                tid_to_wfid[comp_id] = [target_el.get('id')]

    mwid_to_wfids = {}
    for mw_el in doc.xpath('multiwords/mw'):
        mw_id = mw_el.get('id')
        t_ids = {target_el.get('id')
                 for target_el in mw_el.xpath('component/span/target')}
        wf_ids = [tid_to_wfid[t_id][0] for t_id in t_ids]
        sent_ids = [wfid_to_sentid[wf_id] for wf_id in wf_ids]
        assert len(set(sent_ids)) == 1, f'multiword {mw_id} is in 2 or more sentences.'
        mwid_to_wfids[mw_id] = wf_ids

    sentid_to_info = get_sentid_to_info(naf_path=naf_path)
    markable_id_to_info = {}

    for a_dict in [tid_to_wfid, mwid_to_wfids]:
        for id_, wfids in a_dict.items():

            # what is needed here?
            markable_info = []
            for wfid in wfids:
                sent_id = wfid_to_sentid[wfid]
                sent_info = sentid_to_info[sent_id]

                wf_like_el = sent_info['id_to_el'][wfid]
                start_offset_in_sent = int(wf_like_el.get('offset')) - sent_info['sent_offset_start']
                end_offset_in_sent = start_offset_in_sent + (int(wf_like_el.get('length'))-1)

                wf_like_el_info = {
                    'start_offset_in_sent' : start_offset_in_sent,
                    'end_offset_in_sent' : end_offset_in_sent,
                    'naf_sent_id' : sent_id
                }
                markable_info.append(wf_like_el_info)

            markable_id_to_info[id_] = markable_info

    return markable_id_to_info


def get_most_recent_premon_uri(el):
    """

    :param pred_el:
    :return:
    """
    most_recent = datetime(1,1,1)
    the_premon_uri = None
    the_source = None
    the_lu_uri = None

    query = 'externalReferences/externalRef[@resource="http://premon.fbk.eu/premon/fn17"]'
    for ext_ref_el in el.xpath(query):
        timestamp = ext_ref_el.get('timestamp')
        datetime_obj = string_to_datetime_obj(timestamp=timestamp)
        source = ext_ref_el.get('source')
        premon_uri = ext_ref_el.get('reference')
        lu_uri = ext_ref_el.get('lu_uri')

        if datetime_obj > most_recent:
            most_recent = datetime_obj
            the_premon_uri = premon_uri
            the_source = source
            the_lu_uri = lu_uri

    return the_premon_uri, the_source, most_recent, the_lu_uri



def get_annotation_dict(naf_el, markable_id_to_info, premon, verbose=0):

    if naf_el.get('status') == 'deprecated':
        return None, None, None, None, None, None, None

    # get predicate target id
    markable_id = naf_el.find('span/target').get('id')

    # get start_offset_in_sent and end_offset_in_sent
    pred_offsets = markable_id_to_info[markable_id]
    naf_sent_id = pred_offsets[0]['naf_sent_id']

    status = naf_el.get('status')
    premon_uri, source, timestamp, lu_uri = get_most_recent_premon_uri(el=naf_el)

    # obtain frame label using premon
    label = get_rdf_label(graph=premon,
                          uri=premon_uri)

    return label, naf_sent_id, status, lu_uri, timestamp, pred_offsets, source


def get_fe_colors(fn_en, frame_label, fe_label):

    frame_xml_path = os.path.join(fn_en._root, 'frame', f'{frame_label}.xml')
    assert os.path.exists(frame_xml_path)

    doc = etree.parse(frame_xml_path)
    root = doc.getroot()

    for fe_el in root.findall('{http://framenet.icsi.berkeley.edu}FE'):
        if fe_el.get('name') == fe_label:
            bg_color = fe_el.get('bgColor')
            fg_color = fe_el.get('fgColor')

    return bg_color, fg_color

def load_annotations_from_naf(your_fn,
                              path_to_your_fn_in_lemon,
                              naf_path,
                              doc_id,
                              premon):
    """

    """
    parser = etree.XMLParser(remove_blank_text=True, strip_cdata=False)
    doc = etree.parse(naf_path, parser)

    your_fn_in_lemon = load_graph(path=path_to_your_fn_in_lemon, format='ttl')

    sentid_to_annotations = defaultdict(list)

    anno_set_counter = 1

    markable_id_to_info = get_markable_id_to_info(doc=doc,
                                                  naf_path=naf_path)

    for pred_el in doc.xpath('srl/predicate'):

        frame_label, naf_sent_id,\
        status, lu_uri, timestamp,\
        pred_offsets, source = get_annotation_dict(naf_el=pred_el,
                                                   markable_id_to_info=markable_id_to_info,
                                                   premon=premon)
        if frame_label is None:
            continue

        # load frame in NLTK and obtain attribute values
        frame = your_fn.frame_by_name(frame_label)

        # annoset id
        anno_set_id = f'{doc_id}{str(naf_sent_id).zfill(8)}{str(anno_set_counter).zfill(8)}'
        anno_set_counter += 1

        # query lemon for luID and luName, else to discuss
        lu_id = get_lu_identifier(graph=your_fn_in_lemon, lu_uri=lu_uri)

        # query for luName
        try:
            lu_obj = your_fn.lu(lu_id)
            lu_name = lu_obj.name
        except nltk.corpus.reader.framenet.FramenetError:
            lu_name = 'CANDIDATE-TO-BE-ADDED'

        predicate = {
            'cDate': timestamp.strftime("%m/%d/%Y %H:%M:%S UTC %a"),  # predicate timestamp
            'luID': str(lu_id),  # query Lemon representation of the lexicon
            "luName": lu_name,  # NLTK lexicon
            "frameID": str(frame.ID),  # NLTK lexicon
            "frameName": frame_label,  # NLTK lexicon
            "status": status,  # perhaps stick to NAF labels
            "ID": anno_set_id,  # generate annotationset id,
            'pred_offsets': pred_offsets,
            "cBy": source  # extract from header,
        }

        # add frame elements
        fe_label_to_fe_info = {}
        for role_el in pred_el.xpath('role'):
            fe_label, naf_sent_id, \
            status, lu_uri, timestamp, \
            fe_offsets, source = get_annotation_dict(naf_el=role_el,
                                                       markable_id_to_info=markable_id_to_info,
                                                       premon=premon)
            if fe_label is None:
                continue

            fe_obj = frame.FE[fe_label]
            fe_id = fe_obj.ID

            bg_color, fg_color = get_fe_colors(fn_en=fn_en, frame_label=frame_label, fe_label=fe_label)

            # example: cBy="CFB" feID="1805" bgColor="0000FF" fgColor="FFFFFF" end="24" start="21" name="Count"
            fe_info = {
                "cBy" : source,
                "pred_offsets" : fe_offsets,
                "name" : fe_label,
                'feID' : fe_id,
                'bgColor' : bg_color,
                'fgColor' : fg_color
            }

            fe_label_to_fe_info[fe_label] = fe_info

        predicate['fe_label_to_fe_info'] = fe_label_to_fe_info

        sentid_to_annotations[int(naf_sent_id)].append(predicate)

    return sentid_to_annotations


