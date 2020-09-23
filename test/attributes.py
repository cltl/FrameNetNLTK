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

def test_lu_name():
    lu_lemma, lu_pos = lexicon_utils.get_lemma_pos_from_lu_name(lu_name='a.b.c.n')
    assert all([lu_lemma == 'a.b.c',
                lu_pos == 'n'])

def test_lu_pos():
    with pytest.raises(AssertionError):
        validation_utils.validate_lu_pos(lu_pos='N', pos='A')

def test_assertion_error_for_lexeme_1():
    with pytest.raises(AssertionError):
        validation_utils.validate_lexeme(my_fn=fn, lexeme={'a' : 1}, lu_type='singleton')

def test_assertion_error_for_lexeme_2():
    with pytest.raises(ValueError):
        lexeme = {
            'order' : 'a',
            'headword' : 'true',
            'breakBefore' : 'true',
            'POS' : 'N',
            'name' : 'surrender'
        }
        validation_utils.validate_lexeme(my_fn=fn, lexeme=lexeme, lu_type='singleton')

def test_assertion_error_for_lexeme_3():
    with pytest.raises(AssertionError):
        lexeme = {
            'order' : '1',
            'headword' : 'bla',
            'breakBefore' : 'true',
            'POS' : 'N',
            'name' : 'surrender'
        }
        validation_utils.validate_lexeme(my_fn=fn, lexeme=lexeme, lu_type='singleton')

def test_assertion_error_for_lexeme_4():
    with pytest.raises(AssertionError):
        lexeme = {
            'order' : '1',
            'headword' : 'true',
            'breakBefore' : 'a',
            'POS' : 'N',
            'name' : 'surrender'
        }
        validation_utils.validate_lexeme(my_fn=fn, lexeme=lexeme, lu_type='singleton')


def test_assertion_error_for_lexeme_5():
    with pytest.raises(AssertionError):

        lexemes = [{
            'order' : '1',
            'headword' : 'true',
            'breakBefore' : 'a',
            'POS' : 'N',
            'name' : 'surrender',
            'lu_id' : '1'
        }]
        validation_utils.validate_lexemes(my_fn=fn,
                                          lexemes=lexemes,
                                          lu_type='singleton')
def test_new_lu_id():
    new_lu_id = lexicon_utils.get_next_lu_id()
    assert type(new_lu_id) == int
    assert len(str(new_lu_id)) == 13

def test_new_lemma_id():
    new_lu_id = lexicon_utils.get_lemma_id(fn,
                                           lemma='a_new_lemma',
                                           pos='N')
    assert new_lu_id == 52179


def test_assertion_error_type():
    with pytest.raises(AssertionError):
        validation_utils.validate_lu_type(lu_type='blabla')


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

def test_lu_id_found():
    lu_id, reason = lexicon_utils.get_luid(my_fn=fn,
                                           frame_label="Leadership",
                                           lemma="presidential",
                                           pos="A")
    assert lu_id == 12433

def test_lu_id_not_found():
    lu_id, reason = lexicon_utils.get_luid(my_fn=fn,
                                           frame_label="Appelations",
                                           lemma="presidential",
                                           pos="A")
    assert lu_id is None


def test_lu_type_singleton_num_lexemes():
    with pytest.raises(AssertionError):
        validation_utils.validate_num_lexemes(lexemes=[{}, {}],
                                              lu_type='singleton')

def test_lu_type_phrasal_num_lexemes():
    with pytest.raises(AssertionError):
        validation_utils.validate_num_lexemes(lexemes=[{}],
                                              lu_type='phrasal')

def test_lexemes_luname_singleton():
    with pytest.raises(AssertionError):
        validation_utils.validate_lexemes_vs_luname(lexemes=[{'name': 'house'}],
                                                    lu_type='singleton',
                                                    lu_lemma='houses')


def test_lexemes_luname_endocentric():
    with pytest.raises(AssertionError):
        validation_utils.validate_lexemes_vs_luname(lexemes=[{'name': 'president', 'order': '1'},
                                                             {'name': 'verkiezing', 'order': '2'}],
                                                    lu_type='endocentric compound',
                                                    lu_lemma='presidentsverkiezing')

def test_lexemes_luname_substring():
    with pytest.raises(AssertionError):
        validation_utils.validate_lexemes_vs_luname(lexemes=[{'name': 'rode', 'order': '1'},
                                                             {'name': 'borstje', 'order': '2'}],
                                                    lu_type='exocentric compound',
                                                    lu_lemma='roodborstje')

test_assertion_error_type()
test_assertion_error_for_status()
test_assertion_error_for_pos()
test_keyerror_for_frame()

test_lu_name()
test_lu_pos()

test_assertion_error_for_lexeme_1()
test_assertion_error_for_lexeme_2()
test_assertion_error_for_lexeme_3()
test_assertion_error_for_lexeme_4()
test_assertion_error_for_lexeme_5()

test_new_lu_id()
test_new_lemma_id()
test_existing_lemma_id()
test_incorporated_fe()
test_error_incorporated_fe()
test_order()
test_error_order()
test_incorporated_fe_lu_and_lexemes()
test_error_incorporated_fe_lu_and_lexemes()

test_lu_id_found()
test_lu_id_not_found()

test_lu_type_singleton_num_lexemes()
test_lu_type_phrasal_num_lexemes()
test_lexemes_luname_singleton()
test_lexemes_luname_substring()
