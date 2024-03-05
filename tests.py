from typing import Callable, Dict, Iterable, List, Set

from pydantic import BaseModel, TypeAdapter
import sortedcontainers

import sortedcontainers_pydantic


class ReusableIterable:
    """Utility iterable class that can be used multiple times without exhausting."""

    def __init__(self, iterable_factory: Callable[[], Iterable]):
        self.iterable_factory = iterable_factory

    def __iter__(self):
        return iter(self.iterable_factory())


def test_sorted_dict():
    ta = TypeAdapter(sortedcontainers_pydantic.SortedDict)

    expected = sortedcontainers.SortedDict({"c": 1, "a": 2, "b": 3})

    cases = [
        expected,
        {"c": 1, "a": 2, "b": 3},
        [("c", 1), ("a", 2), ("b", 3)],
        [("b", 3), ("c", 1), ("a", 2)],
        (("c", 1), ("a", 2), ("b", 3)),
        {("c", 1), ("a", 2), ("b", 3)},
        ReusableIterable(lambda: [("c", 1), ("a", 2), ("b", 3)]),
    ]

    for annotation in (
        sortedcontainers_pydantic.SortedDict,
        sortedcontainers_pydantic.SortedDict[str, int],
    ):
        ta = TypeAdapter(annotation)
        for case in cases:
            print(f"annotation: {annotation}, case: {case}")
            actual = ta.validate_python(case)
            assert isinstance(actual, sortedcontainers.SortedDict)
            assert actual == expected

        assert ta.dump_json(expected).decode() == '{"a":2,"b":3,"c":1}'

    assert (
        TypeAdapter(sortedcontainers_pydantic.SortedDict).json_schema()
        == TypeAdapter(dict).json_schema()
    )
    assert (
        TypeAdapter(sortedcontainers_pydantic.SortedDict[str, int]).json_schema()
        == TypeAdapter(Dict[str, int]).json_schema()
    )

    class MyModel(BaseModel):
        sorted_dict: sortedcontainers_pydantic.SortedDict

    class MyModelWithArg(BaseModel):
        sorted_dict: sortedcontainers_pydantic.SortedDict[str, int]

    for model in (MyModel, MyModelWithArg):
        for case in cases:
            print(f"model: {model}, case: {case}")
            instance = MyModel(sorted_dict=case)
            assert isinstance(instance.sorted_dict, sortedcontainers.SortedDict)
            assert instance.sorted_dict == expected
            assert instance.model_dump_json() == '{"sorted_dict":{"a":2,"b":3,"c":1}}'


def test_sorted_list():
    expected = sortedcontainers.SortedList([3, 2, 1])

    cases = [
        expected,
        [3, 2, 1],
        (3, 2, 1),
        {3, 2, 1},
        range(3, 0, -1),
        [2, 3, 1],
    ]

    for annotation in (
        sortedcontainers_pydantic.SortedList,
        sortedcontainers_pydantic.SortedList[int],
    ):
        ta = TypeAdapter(annotation)
        for case in cases:
            print(f"annotation: {annotation}, case: {case}")
            actual = ta.validate_python(case)
            assert isinstance(actual, sortedcontainers.SortedList)
            assert actual == expected

        assert ta.dump_json(expected).decode() == "[1,2,3]"

    assert (
        TypeAdapter(sortedcontainers_pydantic.SortedList).json_schema()
        == TypeAdapter(list).json_schema()
    )
    assert (
        TypeAdapter(sortedcontainers_pydantic.SortedList[int]).json_schema()
        == TypeAdapter(List[int]).json_schema()
    )

    class MyModel(BaseModel):
        sorted_list: sortedcontainers_pydantic.SortedList

    class MyModelWithArg(BaseModel):
        sorted_list: sortedcontainers_pydantic.SortedList[int]

    for model in (MyModel, MyModelWithArg):
        for case in cases:
            print(f"model: {model}, case: {case}")
            instance = MyModel(sorted_list=case)
            assert isinstance(instance.sorted_list, sortedcontainers.SortedList)
            assert instance.sorted_list == expected
            assert instance.model_dump_json() == '{"sorted_list":[1,2,3]}'


def test_sorted_set():
    expected = sortedcontainers.SortedSet([3, 2, 1])

    cases = [
        expected,
        [3, 2, 1],
        (3, 2, 1),
        {3, 2, 1},
        range(3, 0, -1),
        [2, 3, 1],
    ]

    for annotation in (
        sortedcontainers_pydantic.SortedSet,
        sortedcontainers_pydantic.SortedSet[int],
    ):
        ta = TypeAdapter(annotation)
        for case in cases:
            print(f"annotation: {annotation}, case: {case}")
            actual = ta.validate_python(case)
            assert isinstance(actual, sortedcontainers.SortedSet)
            assert actual == expected

        assert ta.dump_json(expected).decode() == "[1,2,3]"

    assert (
        TypeAdapter(sortedcontainers_pydantic.SortedSet).json_schema()
        == TypeAdapter(set).json_schema()
    )
    assert (
        TypeAdapter(sortedcontainers_pydantic.SortedSet[int]).json_schema()
        == TypeAdapter(Set[int]).json_schema()
    )

    class MyModel(BaseModel):
        sorted_set: sortedcontainers_pydantic.SortedSet

    class MyModelWithArg(BaseModel):
        sorted_set: sortedcontainers_pydantic.SortedSet[int]

    for model in (MyModel, MyModelWithArg):
        for case in cases:
            print(f"model: {model}, case: {case}")
            instance = MyModel(sorted_set=case)
            assert isinstance(instance.sorted_set, sortedcontainers.SortedSet)
            assert instance.sorted_set == expected
            assert instance.model_dump_json() == '{"sorted_set":[1,2,3]}'
