import os
import shutil
from glob import glob


def remove_and_create_folder(fldr, verbose=0):
    """
    Remove a folder, if existing, and re-create it.
    """
    if os.path.exists(fldr):
        shutil.rmtree(fldr)

        if verbose >= 1:
            print(f'removed folder at {fldr}')
    os.mkdir(fldr)
    if verbose >= 1:
        print(f'recreated folder at {fldr}')


def get_relevant_paths(root, check_if_exists=True):
    label_to_path = {}

    label_and_basenames = [
        ('frRelation.xml', 'frRelation.xml'),
        ('frameIndex.xml', 'frameIndex.xml'),
        ('frameIndex.xsl', 'frameIndex.xsl'),
        ('luIndex.xml', 'luIndex.xml'),
        ('luIndex.xsl', 'luIndex.xsl'),
        ('semTypes.xml', 'semTypes.xml'),
        ('lu_dir', 'lu'),
        ('lexUnit.xsl', 'lu/lexUnit.xsl'),
        ('frame_dir', 'frame'),
        ('frame.xsl', 'frame/frame.xsl')
    ]

    for label, basename in label_and_basenames:
        full_path = os.path.join(root, basename)

        if check_if_exists:
            assert os.path.exists(full_path)
        label_to_path[label] = full_path

    label_to_path['frame_to_xml_path'] = dict()
    frame_dir = label_to_path['frame_dir']
    for frame_xml in glob(f'{frame_dir}/*xml'):
        basename = os.path.basename(frame_xml)
        frame = basename[:-4]

        label_to_path['frame_to_xml_path'][frame] = os.path.join(frame_dir,
                                                                 basename)

    return label_to_path

def get_frame_xml_path(your_fn, frame_name):
    pass

