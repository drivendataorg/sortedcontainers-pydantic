from pydantic import TypeAdapter
import sortedcontainers

import sortedcontainers_pydantic


def test_sorted_dict():
    ta = TypeAdapter(sortedcontainers_pydantic.SortedDict)

    expected = sortedcontainers.SortedDict({"c": 1, "a": 2, "b": 3})

    assert ta.validate_python(expected) == expected
    assert ta.validate_python({"c": 1, "a": 2, "b": 3}) == expected
    assert ta.validate_python({"b": 3, "c": 1, "a": 2}) == expected
    assert ta.validate_python([("c", 1), ("a", 2), ("b", 3)]) == expected
    assert ta.validate_python([("b", 3), ("c", 1), ("a", 2)]) == expected
    assert ta.validate_python(pair for pair in [("c", 1), ("a", 2), ("b", 3)]) == expected

    assert ta.json_schema() == TypeAdapter(dict).json_schema()


def test_sorted_list():
    ta = TypeAdapter(sortedcontainers_pydantic.SortedList)

    expected = sortedcontainers.SortedList([3, 2, 1])

    assert ta.validate_python(expected) == expected
    assert ta.validate_python([3, 2, 1]) == expected
    assert ta.validate_python((3, 2, 1)) == expected
    assert ta.validate_python({3, 2, 1}) == expected
    assert ta.validate_python(i for i in (3, 2, 1)) == expected
    assert ta.validate_python([2, 3, 1]) == expected

    assert ta.json_schema() == TypeAdapter(list).json_schema()


def test_sorted_set():
    ta = TypeAdapter(sortedcontainers_pydantic.SortedSet)

    expected = sortedcontainers.SortedSet([3, 2, 1])

    assert ta.validate_python(expected) == expected
    assert ta.validate_python([3, 2, 1]) == expected
    assert ta.validate_python((3, 2, 1)) == expected
    assert ta.validate_python({3, 2, 1}) == expected
    assert ta.validate_python(i for i in (3, 2, 1)) == expected
    assert ta.validate_python([2, 3, 1]) == expected

    assert ta.json_schema() == TypeAdapter(set).json_schema()
