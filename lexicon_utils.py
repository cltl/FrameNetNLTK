
def get_next_lu_id(your_fn):
    lu_ids_and_names = your_fn.lu_ids_and_names()
    if lu_ids_and_names:
        highest = max(lu_ids_and_names)
        new_lu_id = highest+1
    else:
        new_lu_id = 1
    return new_lu_id

def get_lemma_id(your_fn,
                 lemma,
                 pos):
    """
    FrameNet stores an identifier for each lemma.pos combination.
    In this function, we retrieve it or generate a new one.
    """
    chosen_lemma_id = None
    target = f'{lemma}.{pos.lower()}'
    for lu_id, lemma_pos in your_fn.lu_ids_and_names().items():
        if lemma_pos == target:
            lu = your_fn.lu(lu_id)
            chosen_lemma_id = lu.lemmaID
            break

    if chosen_lemma_id is None:
        lemma_ids = set()
        for lu in your_fn.lus():
            lemma_ids.add(lu.lemmaID)

        if lemma_ids:
            maximum = max(lemma_ids)
        else:
            maximum = 0
        chosen_lemma_id = maximum + 1

    return chosen_lemma_id







def create_lemma(lexemes):

    order_to_lexeme = dict()
    for lexeme in lexemes:
        order_to_lexeme[int(lexeme['order'])] = lexeme

    parts = []
    for order, lexeme in sorted(order_to_lexeme.items()):

        prefix = ''
        if lexeme['breakBefore'] == 'true':
            prefix = ' '
        parts.append(prefix + lexeme['name'])

    lemma = ''.join(parts)
    return lemma


lexemes = [{
    'order' : '1',
    'headword' : 'false',
    'breakBefore' : 'false',
    'POS' : 'V',
    'name' : 'give'
},
    {
        'order': '2',
        'headword': 'false',
        'breakBefore': 'true',
        'POS': 'A',
        'name': 'up'
    }
]
assert create_lemma(lexemes) == 'give up'