import nltk

STATUS = {'Unknown', 'FN1_Sent', 'Test', 'Add_Annotation',
          'New', 'Finished_Checked', 'FN1_NoSent',
          'Rules_Defined', 'SC_Defined', 'In_Use', 'Finished_Initial',
          'BTDT', 'Finished_X-Gov', 'Insufficient_Attestations', 'Created',
          'Problem', 'Needs_SCs', 'Pre-Marked'}

POS = {'PRON', 'NUM', 'A', 'PREP', 'IDIO', 'N', 'INTJ', 'V', 'ART', 'SCON', 'ADV', 'C'}

LEXEME_ATTRS = {
    'order',
    'headword',
    'breakBefore',
    'POS',
    'name'
}


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

def validate_lexeme(lexeme):
    for lexeme_attr in LEXEME_ATTRS:
        assert lexeme_attr in lexeme, f'missing atribute {lexeme_attr} in {lexeme} (required are {LEXEME_ATTRS}'

    int(lexeme['order'])
    assert lexeme['headword'] in {'true', 'false'}, f'possible values for headword are "true" and "false". You specified {lexeme["headword"]}'
    assert lexeme['breakBefore'] in {'true', 'false'}, f'possible values for breakBefore are "true" and "false". You specified {lexeme["breakBefore"]}'
    validate_pos(pos=lexeme["POS"])

    name = lexeme['name']
    assert type(name) == str, f'the name of lexeme should be a string, you provided a {type(name)}.'


def validate_lexemes(lexemes):
    for lexeme in lexemes:
        validate_lexeme(lexeme=lexeme)


def frames_with_lemma_pos_in_lexicon(your_fn, lemma, pos):
    frames = your_fn.frames_by_lemma(f'{lemma}.{pos.lower()}')

    frame_to_frame_obj = dict()
    for frame in frames:
        frame_to_frame_obj[frame.name] = frame

    return frame_to_frame_obj


