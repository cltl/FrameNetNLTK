import time

def get_next_lu_id():
    milliseconds = int(round(time.time() * 1000))
    return milliseconds


def get_lemma_pos_from_lu_name(lu_name):
    lemma, pos = lu_name.rsplit('.', 1)
    return lemma, pos


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


def get_luid(my_fn,
             frame_label,
             lemma,
             pos):
    """
    Given a frame, lemma, and pos
    try to retrieve the lu identifier.

    :param my_fn: loaded framenet using NLTK's FrameNetCorpusReader
    :param str frame_label: a frame label
    :param str lemma: a lemma, e.g., election
    :param str pos: a FrameNet part of speech tag, e.g., N (see validation_utils.POS for the full set)

    :return: the lu identifier or None if not found
    """
    lu_ids = set()
    target = f'{lemma}.{pos.lower()}'
    for lu_id, lemma_pos in my_fn.lu_ids_and_names().items():
        if lemma_pos == target:
            lu = my_fn.lu(lu_id)
            frame = lu.frame

            if frame.name == frame_label:
                lu_ids.add(lu_id)

    if len(lu_ids) >= 2:
        target_lu_id = None
        reason = f'{lemma}.{pos.lower()} found in multiple frames (lu ids are {lu_ids}'
    elif len(lu_ids) == 1:
        target_lu_id = list(lu_ids)[0]
        reason = 'succes'
    else:
        target_lu_id = None
        reason = f'no lu id found matching {lemma}.{pos.lower()}'

    return target_lu_id, reason
