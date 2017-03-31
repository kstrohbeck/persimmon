from persimmon.utils import Zipper


def test_new_zipper_has_length_zero():
    zipper = Zipper()
    assert len(zipper) == 0


def test_new_zipper_has_index_zero():
    zipper = Zipper()
    assert zipper.index == 0


def test_new_zipper_is_at_end():
    zipper = Zipper()
    assert zipper.is_at_end


def test_index_sets_element_at_index():
    zipper = Zipper.from_list([1, 2, 3])
    zipper.index = 1
    assert zipper.index == 1


def test_cur_item_gets_element_at_index():
    zipper = Zipper.from_list([1, 2, 3])
    zipper.index = 1
    assert zipper.cur_item == 2


def test_append_increases_length_by_one():
    zipper = Zipper()
    zipper.append(True)
    assert len(zipper) == 1


def test_append_doesnt_change_index():
    zipper = Zipper()
    zipper.append(True)
    assert zipper.index == 0


def test_append_changes_if_at_end():
    zipper = Zipper()
    zipper.append(True)
    assert not zipper.is_at_end


def test_advance_increments_index():
    zipper = Zipper.from_list([1, 2, 3])
    zipper.advance()
    assert zipper.index == 1


def test_advance_doesnt_increment_index_at_end():
    zipper = Zipper()
    zipper.advance()
    assert zipper.index == 0


def test_delete_up_to_doesnt_delete_if_index_is_zero():
    zipper = Zipper.from_list([1, 2, 3])
    zipper.delete_up_to(2)
    assert zipper == Zipper.from_list([1, 2, 3])


def test_delete_up_to_deletes_up_to_index_if_it_is_first():
    zipper = Zipper.from_list([1, 2, 3])
    zipper.index = 1
    zipper.delete_up_to(2)
    assert zipper == Zipper.from_list([2, 3])


def test_delete_up_to_deletes_up_to_given_if_it_is_first():
    zipper = Zipper.from_list([1, 2, 3])
    zipper.index = 3
    zipper.delete_up_to(2)
    assert zipper == Zipper.from_list([3], 1)


def test_delete_up_to_deletes_up_to_length_if_it_is_first():
    zipper = Zipper.from_list([1, 2, 3])
    zipper.index = 3
    zipper.delete_up_to(4)
    assert zipper == Zipper()


def test_empty_zipper_is_equal_to_empty_zipper():
    zipper = Zipper()
    assert zipper == Zipper()


def test_zippers_are_equal_with_same_content_and_index():
    zipper = Zipper.from_list([1, 2, 3])
    assert zipper == Zipper.from_list([1, 2, 3])


def test_zippers_are_not_equal_with_different_index():
    zipper = Zipper.from_list([1, 2, 3])
    zipper.index = 1
    assert zipper != Zipper.from_list([1, 2, 3])


def test_eq_returns_false_against_non_zipper():
    zipper = Zipper()
    assert zipper != []
