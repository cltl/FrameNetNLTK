from lxml import etree


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


def extract_annotations_from_naf(naf_path):
    """

    :param naf_path:
    :return:
    """
    parser = etree.XMLParser(remove_blank_text=True, strip_cdata=False)
    doc = etree.parse(naf_path, parser)

    sentid_to_info = {}

    for wf_el in doc.xpath('text/wf'):

        sent_id = wf_el.get('sent')

        if sent_id not in sentid_to_info:
            sentid_to_info[sent_id] = {
                'tokens' : [],
                'paragNo' : '0',
                'sentNo' : str(sent_id)
            }

        sentid_to_info[sent_id]['tokens'].append(wf_el)

    for sent_id, info in sentid_to_info.items():
        sentence = get_sentence(wf_els=info['tokens'])
        info['sentence'] = sentence

    return sentid_to_info