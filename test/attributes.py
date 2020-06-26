import sys
import pytest

sys.path.append('../')

import validation_utils
import lexicon_utils
from nltk.corpus import framenet as fn

def test_assertion_error_for_status():
    with pytest.raises(AssertionError):
        validation_utils.validate_status(status='new')

def test_assertion_error_for_pos():
    with pytest.raises(AssertionError):
        validation_utils.validate_status(status='n')

def test_keyerror_for_frame():
    with pytest.raises(KeyError):
        validation_utils.validate_frame(your_fn=fn, frame_name='hello')

def test_assertion_error_for_lexeme_1():
    with pytest.raises(AssertionError):
        validation_utils.validate_lexeme(lexeme={'a' : 1})

def test_assertion_error_for_lexeme_2():
    with pytest.raises(ValueError):
        lexeme = {
            'order' : 'a',
            'headword' : 'true',
            'breakBefore' : 'true',
            'POS' : 'N',
            'name' : 'surrender'
        }
        validation_utils.validate_lexeme(lexeme=lexeme)

def test_assertion_error_for_lexeme_3():
    with pytest.raises(AssertionError):
        lexeme = {
            'order' : '1',
            'headword' : 'bla',
            'breakBefore' : 'true',
            'POS' : 'N',
            'name' : 'surrender'
        }
        validation_utils.validate_lexeme(lexeme=lexeme)

def test_assertion_error_for_lexeme_4():
    with pytest.raises(AssertionError):
        lexeme = {
            'order' : '1',
            'headword' : 'true',
            'breakBefore' : 'a',
            'POS' : 'N',
            'name' : 'surrender'
        }
        validation_utils.validate_lexeme(lexeme=lexeme)

def test_new_lu_id():
    new_lu_id = lexicon_utils.get_next_lu_id(fn)
    assert new_lu_id == 18821

def test_new_lemma_id():
    new_lu_id = lexicon_utils.get_lemma_id(fn,
                                           lemma='a_new_lemma',
                                           pos='N')
    assert new_lu_id == 52179

def test_existing_lemma_id():
    new_lu_id = lexicon_utils.get_lemma_id(fn,
                                           lemma='surrender',
                                           pos='N')
    assert new_lu_id == 50823


def test_incorporated_fe():
    validation_utils.validate_incorporated_fe(fn_en=fn,
                                              frame_label='People_by_origin',
                                              incorporated_fe='Origin')

def test_error_incorporated_fe():
    with pytest.raises(AssertionError):
        validation_utils.validate_incorporated_fe(fn_en=fn,
                                                  frame_label='People_by_origin',
                                                  incorporated_fe='wrong_label')

def test_order():
    validation_utils.validate_order_attr(lexemes=[{'order': '1'},
                                                  {'order': '2'}])

def test_error_order():
    with pytest.raises(AssertionError):
        validation_utils.validate_order_attr([{'order': '1'},
                                             {'order': '1'}])


def test_incorporated_fe_lu_and_lexemes():
    validation_utils.validate_incorporate_fe_lu_and_lexemes(incorporated_fe='Origin',
                                                            lexemes=[{'incorporatedFE': 'Origin'},
                                                                     {}])

def test_error_incorporated_fe_lu_and_lexemes():
    with pytest.raises(AssertionError):
        validation_utils.validate_incorporate_fe_lu_and_lexemes(incorporated_fe='Origin',
                                                                lexemes=[{'incorporatedFE' : 'wrong_label'},
                                                                         {}])
test_assertion_error_for_status()
test_assertion_error_for_pos()
test_keyerror_for_frame()
test_assertion_error_for_lexeme_1()
test_assertion_error_for_lexeme_2()
test_assertion_error_for_lexeme_3()
test_assertion_error_for_lexeme_4()
test_new_lu_id()
test_new_lemma_id()
test_existing_lemma_id()
test_incorporated_fe()
test_error_incorporated_fe()
test_order()
test_error_order()
test_incorporated_fe_lu_and_lexemes()
test_error_incorporated_fe_lu_and_lexemes()

