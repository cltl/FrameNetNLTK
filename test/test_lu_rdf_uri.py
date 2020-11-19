import sys
import pytest
sys.path.insert(0, '..')
sys.path.insert(0, '../..')
from FrameNetNLTK import load, get_luid, generate_le_and_lu_rdf_uri


fn = load('../test/test_lexicon')

lu_id, reason = get_luid(my_fn=fn,
                         frame_label='Change_of_leadership',
                         lemma='verkiezing',
                         pos='N')

lu_id, reason = get_luid(my_fn=fn,
                         frame_label='Change_of_leadership',
                         lemma='verkiezing',
                         pos='N')


def test_version():
    with pytest.raises(AssertionError):
        le_rdf_uri, leform_rdf_uri, lu_rdf_uri = generate_le_and_lu_rdf_uri(your_fn=fn,
                                         namespace='http://rdf.cltl.nl/dfn/',
                                         language='nld',
                                         major_version='0',
                                         minor_version=1,
                                         lu_id=lu_id)


def test_namespace():
    with pytest.raises(AssertionError):
        le_rdf_uri, leform_rdf_uri, lu_rdf_uri = generate_le_and_lu_rdf_uri(your_fn=fn,
                                         namespace='tp://rdf.cltl.nl/',
                                         language='nld',
                                         major_version=0,
                                         minor_version=1,
                                         lu_id=lu_id)


def test_language():
    with pytest.raises(AssertionError):
        le_rdf_uri, leform_rdf_uri, lu_rdf_uri = generate_le_and_lu_rdf_uri(your_fn=fn,
                                         namespace='http://rdf.cltl.nl/dfn/',
                                         language='it',
                                         major_version=0,
                                         minor_version=1,
                                         lu_id=lu_id)


le_rdf_uri, leform_rdf_uri, lu_rdf_uri = generate_le_and_lu_rdf_uri(your_fn=fn,
                                 namespace='http://rdf.cltl.nl/dfn/',
                                 language='nld',
                                 major_version=0,
                                 minor_version=1,
                                 lu_id=lu_id)
print(le_rdf_uri)
print(leform_rdf_uri)
print(lu_rdf_uri)


