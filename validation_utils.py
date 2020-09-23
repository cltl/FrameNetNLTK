import nltk


STATUS = {'Unknown', 'FN1_Sent', 'Test', 'Add_Annotation',
          'New', 'Finished_Checked', 'FN1_NoSent',
          'Rules_Defined', 'SC_Defined', 'In_Use', 'Finished_Initial',
          'BTDT', 'Finished_X-Gov', 'Insufficient_Attestations', 'Created',
          'Problem', 'Needs_SCs', 'Pre-Marked'}

POS = {'PRON', 'NUM', 'A', 'PREP', 'IDIO', 'N', 'INTJ', 'V', 'ART', 'SCON', 'ADV', 'C',
       'I'}

LEXEME_ATTRS = {
    'order',
    'headword',
    'breakBefore',
    'POS',
    'name'
}

OPTIONAL_LEXEME_ATTRS = {
    'incorporatedFE',
    'lu_id'
}

TYPES = {
    'singleton',
    'phrasal',
    'idiom',
    'endocentric compound',
    'exocentric compound'
}

def create_lemma(lexemes, separator=''):
    order_to_lexeme = dict()
    for lexeme in lexemes:
        order_to_lexeme[int(lexeme['order'])] = lexeme

    parts = []
    for order, lexeme in sorted(order_to_lexeme.items()):
        if order == 1:
            parts.append(lexeme['name'])
        elif order >= 2:
            parts.append(separator + lexeme['name'])

    lemma = ''.join(parts)
    return lemma


the_lexemes = [{
    'order': '1',
    'headword': 'false',
    'breakBefore': 'false',
    'POS': 'V',
    'name': 'give'
},
    {
        'order': '2',
        'headword': 'false',
        'breakBefore': 'false',
        'POS': 'A',
        'name': 'up'
    }
]
assert create_lemma(lexemes=the_lexemes, separator=' ') == 'give up'

def validate_status(status):
    assert status in STATUS, f'{status} not part of accepted set: {STATUS}'


validate_status(status='New')


def validate_pos(pos):
    assert pos in POS, f'{pos} not part of accepted set: {POS}'


validate_pos(pos='N')


def validate_frame(your_fn, frame_name):
    try:
        your_fn.frame_by_name(frame_name)
    except nltk.corpus.reader.framenet.FramenetError:
        raise KeyError(f'{frame_name} not part of your FrameNet.')


def validate_lexeme(my_fn, lexeme, lu_type):
    for lexeme_attr in LEXEME_ATTRS:

        # a lexeme of a phrasal verb does not need to have a POS attribute
        # we do not specify it for the verb particle
        if all([lu_type == 'phrasal',
                lexeme_attr == 'POS']):
            continue

        assert lexeme_attr in lexeme, \
            f'missing atribute {lexeme_attr} in {lexeme} (required are {LEXEME_ATTRS}'

    for lexeme_attr, value in lexeme.items():
        assert lexeme_attr in LEXEME_ATTRS | OPTIONAL_LEXEME_ATTRS, \
            f'{lexeme_attr} not part of allowed attributes. Please inspect.'

        if lexeme_attr == 'lu_id':
            assert int(value) in my_fn.lu_ids_and_names(), \
                f'lu id {value} not found in your FrameNet. Please inspect.'

    int(lexeme['order'])
    assert lexeme['headword'] in {'true', 'false'}, \
        f'possible values for headword are "true" and "false". You specified {lexeme["headword"]}'
    assert lexeme['breakBefore'] in {'true', 'false'}, \
        f'possible values for breakBefore are "true" and "false". You specified {lexeme["breakBefore"]}'

    if 'POS' in lexeme:
        validate_pos(pos=lexeme["POS"])

    name = lexeme['name']
    assert type(name) == str, f'the name of lexeme should be a string, you provided a {type(name)}.'


def validate_order_attr(lexemes):
    orders_gold = [str(i) for i in range(1, len(lexemes) + 1)]
    orders_provided = [lexeme['order'] for lexeme in lexemes]

    assert set(orders_gold) == set(orders_provided), f'Please inspect order attribute: {lexemes}'


def validate_lexemes(my_fn, lexemes, lu_type):
    for lexeme in lexemes:
        validate_lexeme(my_fn=my_fn, lexeme=lexeme, lu_type=lu_type)

    if len(lexemes) == 1:
        lexeme = lexemes[0]
        assert 'lu_id' not in lexeme, \
            f'the optional attribute lu_id is only allowed in multi-lexeme expressions. Please inspect.'


def frames_with_lemma_pos_in_lexicon(your_fn, lemma, pos):
    frames = your_fn.frames_by_lemma(f'{lemma}.{pos.lower()}')

    frame_to_frame_obj = dict()
    for frame in frames:
        frame_to_frame_obj[frame.name] = frame

    return frame_to_frame_obj


def validate_incorporated_fe(fn_en,
                             frame_label,
                             incorporated_fe):
    """
    we validate that the incorporated_fe is part of the frame
    that the LU is added to.
    (for more information about incorporation, we refer to
    Subsubsection 3.2.4 from the FrameNet book
    https://framenet2.icsi.berkeley.edu/docs/r1.7/book.pdf)

    :param fn_en:
    :param frame_label:
    :param incorporated_fe:
    :return:
    """
    frame = fn_en.frame_by_name(frame_label)
    assert incorporated_fe in frame.FE.keys(), f'{incorporated_fe} not part of frame {frame_label}'


def validate_incorporate_fe_lu_and_lexemes(incorporated_fe,
                                           lexemes):
    if len(lexemes) == 1:
        return

    incorporated_fes = set()
    for lexeme in lexemes:
        incor_fe = lexeme.get('incorporatedFE', None)
        if incor_fe is not None:
            incorporated_fes.add(incor_fe)

    incorporated_fe_lu = set()
    if incorporated_fe is not None:
        incorporated_fe_lu.add(incorporated_fe)
    assert incorporated_fes == incorporated_fe_lu,\
        f'mismatch between incorporatedFE at LU level and in the lexemes: {incorporated_fe} {lexemes}'


def validate_lu_type(lu_type):
    assert lu_type in TYPES, f'type {lu_type} is not part of the accepted set: {TYPES}'


def validate_lu_pos(lu_pos, pos):
    assert lu_pos == pos.lower(), f'different POS provided for lu_name and pos of lu: {lu_pos} and {pos}'


def validate_num_lexemes(lexemes, lu_type):
    if lu_type in {'singleton'}:
        assert len(lexemes) == 1, f'for lu_type {lu_type} the number of lexemes should be one, you provided {len(lexemes)}.'

    elif lu_type in {'phrasal',
                     'endocentric compound'}:
        assert len(lexemes) >= 2, f'for lu_type {lu_type} the number of lexemes should be 2>, you provided {len(lexemes)}.'


def validate_lexemes_vs_luname(lexemes, lu_type, lu_lemma):
    if lu_type == 'singleton':
        lexeme = lexemes[0]['name']
        assert lexeme == lu_lemma, f'for lu_type singleton, the lu_name ({lu_lemma}) and lexeme ({lexeme}) should match.'
    elif lu_type == 'endocentric compound':
        recreated_lemma = create_lemma(lexemes=lexemes,
                                       separator='')

        parts = [f'recreated lemma from lexemes ({recreated_lemma}) does not match the lu_name ({lu_lemma})',
                 f'for the chosen lu_type ({lu_type}), this is needed.']
        error_message = '\n'.join(parts)
        assert lu_lemma == recreated_lemma, error_message
    elif lu_type in {'idiom',
                     'phrasal',
                     'exocentric compound'}:
        for lexeme in lexemes:
            name = lexeme['name']
            parts = [f'lexeme: {name} is not part of the lu_lemma ({lu_lemma})']
            error_message = '\n'.join(parts)
            assert name in lu_lemma, error_message

