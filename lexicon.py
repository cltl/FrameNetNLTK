import json
import warnings
from datetime import datetime
from collections import Counter

from . import validation_utils
from . import lexicon_utils
from . import xml_utils
from . import path_utils
from . import load_utils


def add_lu(your_lexicon_folder,
           fn_en,
           lu_name,
           lexemes,
           definition,
           status,
           pos,
           frame,
           provenance,
           lu_type='singleton',
           incorporated_fe=None,
           timestamp=None,
           optional_lu_attrs={},
           verbose=0):
    succes = False

    your_fn = load_utils.load(folder=your_lexicon_folder)

    lu_lemma, lu_pos = lexicon_utils.get_lemma_pos_from_lu_name(lu_name=lu_name)

    # attribute validation steps
    validation_utils.validate_lu_pos(lu_pos, pos)
    validation_utils.validate_lexemes(my_fn=your_fn, lexemes=lexemes)
    validation_utils.validate_order_attr(lexemes=lexemes)
    validation_utils.validate_status(status=status)
    validation_utils.validate_pos(pos=pos)
    validation_utils.validate_frame(your_fn=your_fn, frame_name=frame)
    validation_utils.validate_lu_type(lu_type)

    if incorporated_fe is not None:
        validation_utils.validate_incorporated_fe(fn_en=fn_en,
                                                  frame_label=frame,
                                                  incorporated_fe=incorporated_fe)

    validation_utils.validate_incorporate_fe_lu_and_lexemes(incorporated_fe=incorporated_fe,
                                                            lexemes=lexemes)

    # lexicon validation steps
    lemma_pos_in_lexicon = validation_utils.frames_with_lemma_pos_in_lexicon(your_fn=your_fn,
                                                                             lemma=lu_lemma,
                                                                             pos=pos)

    if frame in lemma_pos_in_lexicon:
        warnings.warn(f'{lu_lemma} {pos} is already part of {frame}. Please inspect.')
        return succes

    frame_obj = fn_en.frame_by_name(frame)
    frame_id = frame_obj.ID

    # update XML files

    # get relevant paths
    paths_your_fn = path_utils.get_relevant_paths(your_fn.root, check_if_exists=False)

    lu_id = lexicon_utils.get_next_lu_id(your_fn=your_fn)
    lemma_id = lexicon_utils.get_lemma_id(your_fn=your_fn,
                                          lemma=lu_lemma,
                                          pos=pos)

    if timestamp is None:
        cdate = datetime.utcnow().strftime("%m/%d/%Y %H:%M:%S UTC %a")
    else:
        cdate = timestamp.strftime("%m/%d/%Y %H:%M:%S UTC %a")

    # create lu/LU_ID.xml file
    xml_utils.create_lu_xml_file(fn_en,
                                 your_fn,
                                 frame,
                                 lu_id,
                                 status,
                                 lexemes,
                                 lu_lemma,
                                 pos,
                                 definition,
                                 lu_type,
                                 incorporated_fe=incorporated_fe,
                                 optional_lu_attrs=optional_lu_attrs)

    # add lu element to luIndex.xml
    xml_utils.add_lu_el_to_luindex(path_lu_index=paths_your_fn['luIndex.xml'],
                                   frame_id=frame_id,
                                   frame_name=frame,
                                   status=status,
                                   lemma=lu_lemma,
                                   pos=pos,
                                   lu_id=lu_id,
                                   lu_type=lu_type,
                                   optional_lu_attrs=optional_lu_attrs)

    # add lu to frame/FRAME_NAME.xml file
    xml_utils.add_lu_to_frame_xml_file(your_fn,
                                       frame,
                                       status,
                                       lu_lemma,
                                       lemma_id,
                                       pos,
                                       lu_id,
                                       lexemes,
                                       provenance,
                                       cdate,
                                       definition,
                                       lu_type,
                                       incorporated_fe=incorporated_fe,
                                       optional_lu_attrs=optional_lu_attrs)

    if verbose >= 1:
        print(f'added lu id {lu_id}: {lu_lemma}.{pos} -> {frame}')

    succes = True
    return succes


def add_lus_from_json(your_lexicon_folder,
                      fn_en,
                      json_path,
                      verbose=0):
    """

    :param verbose:
    :param your_lexicon_folder:
    :param fn_en:
    :param json_path:
    :return:
    """
    json_lus = json.load(open(json_path))

    status = []

    for lu in json_lus['lus']:

        the_timestamp = lu['timestamp']
        if lu['timestamp'] is not None:
            year, month, day = lu['timestamp']
            the_timestamp = datetime(year=year, month=month, day=day)

        succes = add_lu(your_lexicon_folder,
                        fn_en,
                        lu_name=lu['lu_name'],
                        lexemes=lu['lexemes'],
                        definition=lu['definition'],
                        status=lu['status'],
                        pos=lu['POS'],
                        frame=lu['frame'],
                        provenance=lu['provenance'],
                        lu_type=lu['lu_type'],
                        incorporated_fe=lu['incorporated_fe'],
                        timestamp=the_timestamp,
                        optional_lu_attrs=lu['optional_lu_attrs'],
                        verbose=verbose)

        if succes:
            status.append('added')
        else:
            status.append('failed to add')

    if verbose:
        print(f'{len(status)} LUs were provided to be added.')
        print(f'the process resulted in: {Counter(status)}')


def remove_lu(your_lexicon_folder,
              lu_id,
              verbose=0):
    """

    :param your_lexicon_folder:
    :param int lu_id: the integer of the lu identifier
    :param verbose:
    :return:
    """
    assert type(lu_id) == int, f'the lu id has to be an integer, you provided {type(lu_id)}'

    your_fn = load_utils.load(folder=your_lexicon_folder)
    paths_your_fn = path_utils.get_relevant_paths(your_fn.root)

    # inspect that no endocentric compound is referring to it in a lexeme
    source_lu_ids = set()
    for lu in your_fn.lus():
        for lexeme in lu.lexemes:
            if 'lu_id' in lexeme:
                if lexeme['lu_id'] == lu_id:
                    source_lu_ids.add(lexeme['lu_id'])

    if source_lu_ids:
        assert False, f'LUs {source_lu_ids} are referring to the LU that you want to remove in a lexeme.'

    # remove lu from frame/FRAME_NAME.xml file
    xml_utils.remove_lexunit_el_from_frame_xml(your_fn,
                                               lu_id)

    # remove lu/LU_ID.xml file
    xml_utils.remove_lu_xml_file(your_fn=your_fn,
                                 lu_id=lu_id)

    # remove lu element from luIndex.xml
    xml_utils.remove_lu_el_from_luindex(path_lu_index=paths_your_fn['luIndex.xml'],
                                        lu_id=lu_id)

    if verbose:
        print(f'removed lu id {lu_id} from the lexicon.')

    succes = True
    return succes
