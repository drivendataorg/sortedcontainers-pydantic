from typing import Annotated, Callable, Dict, Iterable, List, Optional, Set

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
        # sortedcontainers_pydantic subclass
        sortedcontainers_pydantic.SortedDict,
        sortedcontainers_pydantic.SortedDict[str, int],
        Optional[sortedcontainers_pydantic.SortedDict],
        Optional[sortedcontainers_pydantic.SortedDict[str, int]],
        # annotation
        sortedcontainers_pydantic.AnnotatedSortedDict,
        sortedcontainers_pydantic.AnnotatedSortedDict[str, int],
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
    assert (
        TypeAdapter(Optional[sortedcontainers_pydantic.SortedDict]).json_schema()
        == TypeAdapter(Optional[dict]).json_schema()
    )
    assert (
        TypeAdapter(Optional[sortedcontainers_pydantic.SortedDict[str, int]]).json_schema()
        == TypeAdapter(Optional[Dict[str, int]]).json_schema()
    )

    class MyModel(BaseModel):
        sorted_dict: sortedcontainers_pydantic.SortedDict

    class MyModelWithArg(BaseModel):
        sorted_dict: sortedcontainers_pydantic.SortedDict[str, int]

    class MyModelWithOptional(BaseModel):
        sorted_dict: Optional[sortedcontainers_pydantic.SortedDict]

    class MyModelWithOptionalWithArg(BaseModel):
        sorted_dict: Optional[sortedcontainers_pydantic.SortedDict[str, int]]

    class MyModelWithAnnotated(BaseModel):
        sorted_dict: sortedcontainers_pydantic.AnnotatedSortedDict

    class MyModelWithAnnotatedWithArg(BaseModel):
        sorted_dict: sortedcontainers_pydantic.AnnotatedSortedDict[str, int]

    for model in (
        MyModel,
        MyModelWithArg,
        MyModelWithOptional,
        MyModelWithOptionalWithArg,
        MyModelWithAnnotated,
        MyModelWithAnnotatedWithArg,
    ):
        for case in cases:
            print(f"model: {model}, case: {case}")
            instance = MyModel(sorted_dict=case)
            assert isinstance(instance.sorted_dict, sortedcontainers.SortedDict)
            assert instance.sorted_dict == expected
            assert instance.model_dump_json() == '{"sorted_dict":{"a":2,"b":3,"c":1}}'


def test_sorted_dict_with_key():
    expected = sortedcontainers.SortedDict({"c": 1, "a": 2, "b": 3}, key=lambda x: -x)

    annotations = (
        # sortedcontainers_pydantic subclass
        sortedcontainers_pydantic.SortedDict,
        sortedcontainers_pydantic.SortedDict[str, int],
        Optional[sortedcontainers_pydantic.SortedDict],
        Optional[sortedcontainers_pydantic.SortedDict[str, int]],
        # annotation
        sortedcontainers_pydantic.AnnotatedSortedDict,
        sortedcontainers_pydantic.AnnotatedSortedDict[str, int],
    )

    for annotation in annotations:
        ta = TypeAdapter(Annotated[annotation, sortedcontainers_pydantic.Key(lambda x: -x)])

        ta.validate_python({"c": 1, "a": 2, "b": 3}) == expected
        tuple(ta.validate_python([("c", 1), ("a", 2), ("b", 3)]).keys()) == ("c", "b", "a")


def test_sorted_list():
    expected = sortedcontainers.SortedList([3, 1, 2])

    cases = [
        expected,
        [1, 2, 3],
        [3, 2, 1],
        [3, 1, 2],
        (3, 1, 2),
        {3, 1, 2},
        range(3, 0, -1),
        [2, 3, 1],
    ]

    for annotation in (
        # sortedcontainers_pydantic subclasses
        sortedcontainers_pydantic.SortedList,
        sortedcontainers_pydantic.SortedList[int],
        sortedcontainers_pydantic.SortedKeyList,
        sortedcontainers_pydantic.SortedKeyList[int],
        # annotations
        sortedcontainers_pydantic.AnnotatedSortedList,
        sortedcontainers_pydantic.AnnotatedSortedList[int],
        sortedcontainers_pydantic.AnnotatedSortedKeyList,
        sortedcontainers_pydantic.AnnotatedSortedKeyList[int],
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
    assert (
        TypeAdapter(sortedcontainers_pydantic.SortedKeyList).json_schema()
        == TypeAdapter(list).json_schema()
    )
    assert (
        TypeAdapter(sortedcontainers_pydantic.SortedKeyList[int]).json_schema()
        == TypeAdapter(List[int]).json_schema()
    )

    class MyModel(BaseModel):
        sorted_list: sortedcontainers_pydantic.SortedList

    class MyModelWithArg(BaseModel):
        sorted_list: sortedcontainers_pydantic.SortedList[int]

    class MyModelWithAnnotated(BaseModel):
        sorted_list: sortedcontainers_pydantic.AnnotatedSortedList

    class MyModelWithAnnotatedWithArg(BaseModel):
        sorted_list: sortedcontainers_pydantic.AnnotatedSortedList[int]

    for model in (MyModel, MyModelWithArg, MyModelWithAnnotated, MyModelWithAnnotatedWithArg):
        for case in cases:
            print(f"model: {model}, case: {case}")
            instance = MyModel(sorted_list=case)
            assert isinstance(instance.sorted_list, sortedcontainers.SortedList)
            assert instance.sorted_list == expected
            assert instance.model_dump_json() == '{"sorted_list":[1,2,3]}'


def test_sorted_list_with_key():
    expected = sortedcontainers.SortedList([3, 1, 2], key=lambda x: -x)

    annotations = (
        # sortedcontainers_pydantic subclass
        sortedcontainers_pydantic.SortedList,
        sortedcontainers_pydantic.SortedList[int],
        sortedcontainers_pydantic.SortedKeyList,
        sortedcontainers_pydantic.SortedKeyList[int],
        # annotation
        sortedcontainers_pydantic.AnnotatedSortedList,
        sortedcontainers_pydantic.AnnotatedSortedList[int],
        sortedcontainers_pydantic.AnnotatedSortedKeyList,
        sortedcontainers_pydantic.AnnotatedSortedKeyList[int],
    )

    for annotation in annotations:
        ta = TypeAdapter(Annotated[annotation, sortedcontainers_pydantic.Key(lambda x: -x)])

        ta.validate_python([3, 1, 2]) == expected
        tuple(ta.validate_python([3, 1, 2])) == (3, 2, 1)


def test_sorted_set():
    expected = sortedcontainers.SortedSet([3, 1, 2])

    cases = [
        expected,
        [3, 1, 2],
        [1, 2, 3],
        [3, 2, 1],
        (3, 1, 2),
        {3, 1, 2},
        range(3, 0, -1),
        [2, 3, 1],
    ]

    for annotation in (
        # sortedcontainers_pydantic subclass
        sortedcontainers_pydantic.SortedSet,
        sortedcontainers_pydantic.SortedSet[int],
        # annotation
        sortedcontainers_pydantic.AnnotatedSortedSet,
        sortedcontainers_pydantic.AnnotatedSortedSet[int],
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

    class MyModelWithAnnotated(BaseModel):
        sorted_set: sortedcontainers_pydantic.AnnotatedSortedSet

    class MyModelWithAnnotatedWithArg(BaseModel):
        sorted_set: sortedcontainers_pydantic.AnnotatedSortedSet[int]

    for model in (MyModel, MyModelWithArg, MyModelWithAnnotated, MyModelWithAnnotatedWithArg):
        for case in cases:
            print(f"model: {model}, case: {case}")
            instance = MyModel(sorted_set=case)
            assert isinstance(instance.sorted_set, sortedcontainers.SortedSet)
            assert instance.sorted_set == expected
            assert instance.model_dump_json() == '{"sorted_set":[1,2,3]}'


def test_sorted_set_with_key():
    expected = sortedcontainers.SortedSet([3, 1, 2], key=lambda x: -x)

    annotations = (
        # sortedcontainers_pydantic subclass
        sortedcontainers_pydantic.SortedSet,
        sortedcontainers_pydantic.SortedSet[int],
        # annotation
        sortedcontainers_pydantic.AnnotatedSortedSet,
        sortedcontainers_pydantic.AnnotatedSortedSet[int],
    )

    for annotation in annotations:
        ta = TypeAdapter(Annotated[annotation, sortedcontainers_pydantic.Key(lambda x: -x)])

        ta.validate_python([3, 1, 2]) == expected
        tuple(ta.validate_python([3, 1, 2])) == (3, 2, 1)
