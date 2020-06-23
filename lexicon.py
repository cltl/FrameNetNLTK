from datetime import datetime

from . import validation_utils
from . import lexicon_utils
from . import xml_utils
from . import path_utils
from . import load_utils

def add_lu(your_lexicon_folder,
           fn_en,
           lexemes,
           definition,
           status,
           pos,
           frame,
           provenance,
           timestamp=None,
           verbose=0):

    your_fn = load_utils.load(folder=your_lexicon_folder)

    # attribute validation steps
    validation_utils.validate_status(status=status)
    validation_utils.validate_pos(pos=pos)
    validation_utils.validate_frame(your_fn=your_fn, frame_name=frame)
    validation_utils.validate_lexemes(lexemes=lexemes)

    # lexicon validation steps
    lemma = lexicon_utils.create_lemma(lexemes)

    lemma_pos_in_lexicon = validation_utils.frames_with_lemma_pos_in_lexicon(your_fn=your_fn,
                                                                             lemma=lemma,
                                                                             pos=pos)

    print(lemma_pos_in_lexicon)
    assert frame not in lemma_pos_in_lexicon, f'{lemma} {pos} is already part of {frame}. Please inspect.'
    frame_obj = fn_en.frame_by_name(frame)
    frame_id = frame_obj.ID

    # update XML files

    # get relevant paths
    paths_your_fn = path_utils.get_relevant_paths(your_fn._root, check_if_exists=False)
    paths_fn_en = path_utils.get_relevant_paths(fn_en._root)

    lu_id = lexicon_utils.get_next_lu_id(your_fn=your_fn)
    lemma_id = lexicon_utils.get_lemma_id(your_fn=your_fn,
                                          lemma=lemma,
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
                                 lemma,
                                 pos,
                                 definition)

    # add lu element to luIndex.xml
    xml_utils.add_lu_el_to_luindex(path_lu_index=paths_your_fn['luIndex'],
                                   frame_id=frame_id,
                                   frame_name=frame,
                                   status=status,
                                   lemma=lemma,
                                   pos=pos,
                                   lu_id=lu_id)

    # add lu to frame/FRAME_NAME.xml file
    xml_utils.add_lu_to_frame_xml_file(your_fn,
                                       frame,
                                       status,
                                       lemma,
                                       lemma_id,
                                       pos,
                                       lu_id,
                                       lexemes,
                                       provenance,
                                       cdate,
                                       definition)


def remove_lu(your_lexicon_folder,
              lu_id,
              verbose=0):
    your_fn = load_utils.load(folder=your_lexicon_folder)
    paths_your_fn = path_utils.get_relevant_paths(your_fn._root)

    # remove lu from frame/FRAME_NAME.xml file
    xml_utils.remove_lexunit_el_from_frame_xml(your_fn,
                                               lu_id)

    # remove lu/LU_ID.xml file
    xml_utils.remove_lu_xml_file(your_fn=your_fn,
                                 lu_id=lu_id)

    # remove lu element from luIndex.xml
    xml_utils.remove_lu_el_from_luindex(path_lu_index=paths_your_fn['luIndex'],
                                        lu_id=lu_id)



