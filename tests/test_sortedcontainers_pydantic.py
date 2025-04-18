from typing import Annotated, Callable, Dict, Iterable, List, Optional, Set

from pydantic import BaseModel, TypeAdapter
import pytest
import sortedcontainers as sc

import sortedcontainers_pydantic as sc_p


def test_get_constructor():
    sc_p._get_constructor(sc.SortedDict) == sc.SortedDict
    sc_p._get_constructor(sc.SortedDict[str, int]) == sc.SortedDict
    sc_p._get_constructor(sc.SortedList) == sc.SortedList
    sc_p._get_constructor(sc.SortedList[int]) == sc.SortedList
    sc_p._get_constructor(sc.SortedSet) == sc.SortedSet
    sc_p._get_constructor(sc.SortedSet[int]) == sc.SortedSet
    sc_p._get_constructor(sc_p.SortedDict) == sc.SortedDict
    sc_p._get_constructor(sc_p.SortedDict[str, int]) == sc.SortedDict
    sc_p._get_constructor(sc_p.SortedList) == sc.SortedList
    sc_p._get_constructor(sc_p.SortedList[int]) == sc.SortedList
    sc_p._get_constructor(sc_p.SortedSet) == sc.SortedSet
    sc_p._get_constructor(sc_p.SortedSet[int]) == sc.SortedSet

    # Test with a custom subclass
    class CustomSortedDict(sc.SortedDict): ...

    sc_p._get_constructor(CustomSortedDict) == CustomSortedDict
    sc_p._get_constructor(CustomSortedDict[str, int]) == CustomSortedDict

    class CustomSCPSortedDict(sc_p.SortedDict): ...

    sc_p._get_constructor(CustomSCPSortedDict) == CustomSCPSortedDict
    sc_p._get_constructor(CustomSCPSortedDict[str, int]) == CustomSCPSortedDict


class ReusableIterable:
    """Utility iterable class that can be used multiple times without exhausting."""

    def __init__(self, iterable_factory: Callable[[], Iterable]):
        self.iterable_factory = iterable_factory

    def __iter__(self):
        return iter(self.iterable_factory())


def test_sorted_dict():
    expected = sc.SortedDict({"c": 1, "a": 2, "b": 3})

    base_cases = [
        expected,
        {"c": 1, "a": 2, "b": 3},
        [("c", 1), ("a", 2), ("b", 3)],
        [("b", 3), ("c", 1), ("a", 2)],
        (("c", 1), ("a", 2), ("b", 3)),
        {("c", 1), ("a", 2), ("b", 3)},
        ReusableIterable(lambda: [("c", 1), ("a", 2), ("b", 3)]),
    ]
    coercion_cases = [
        sc.SortedDict([("c", 1.0), ("a", 2.0), ("b", 3.0)]),
        {"c": 1.0, "a": 2.0, "b": 3.0},
    ]

    for annotation, coerces in (
        # sortedcontainers_pydantic subclass
        (sc_p.SortedDict, False),
        (sc_p.SortedDict[str, int], True),
        # annotation
        (sc_p.AnnotatedSortedDict, False),
        (sc_p.AnnotatedSortedDict[str, int], True),
        # manual annotation
        (Annotated[sc.SortedDict, sc_p.SortedDictPydanticAnnotation], False),
        (Annotated[sc.SortedDict[str, int], sc_p.SortedDictPydanticAnnotation], True),
    ):
        ta = TypeAdapter(annotation)
        cases = base_cases + (coercion_cases if coerces else [])
        for case in cases:
            print(f"annotation: {annotation}, case: {case}")
            actual = ta.validate_python(case)
            assert isinstance(actual, sc.SortedDict)
            assert actual == expected
        assert ta.dump_json(expected).decode() == '{"a":2,"b":3,"c":1}'

        # Works inside Optional
        ta = TypeAdapter(Optional[annotation])
        for case in cases:
            print(f"annotation: {annotation}, case: {case}")
            actual = ta.validate_python(case)
            assert isinstance(actual, sc.SortedDict)
            assert actual == expected
            assert ta.validate_python(None) is None
        assert ta.dump_json(expected).decode() == '{"a":2,"b":3,"c":1}'

        # Works inside list
        ta = TypeAdapter(list[annotation])
        for case in cases:
            case = [case]
            print(f"annotation: {annotation}, case: {case}")
            actual = ta.validate_python(case)
            assert isinstance(actual, list)
            assert isinstance(actual[0], sc.SortedDict)
            assert actual == [expected]
        assert ta.dump_json([expected]).decode() == '[{"a":2,"b":3,"c":1}]'

    assert TypeAdapter(sc_p.SortedDict).json_schema() == TypeAdapter(dict).json_schema()
    assert (
        TypeAdapter(sc_p.SortedDict[str, int]).json_schema()
        == TypeAdapter(Dict[str, int]).json_schema()
    )
    assert (
        TypeAdapter(Optional[sc_p.SortedDict]).json_schema()
        == TypeAdapter(Optional[dict]).json_schema()
    )
    assert (
        TypeAdapter(Optional[sc_p.SortedDict[str, int]]).json_schema()
        == TypeAdapter(Optional[Dict[str, int]]).json_schema()
    )

    class MyModel(BaseModel):
        sorted_dict: sc_p.SortedDict

    class MyModelWithArg(BaseModel):
        sorted_dict: sc_p.SortedDict[str, int]

    class MyModelWithOptional(BaseModel):
        sorted_dict: Optional[sc_p.SortedDict]

    class MyModelWithOptionalWithArg(BaseModel):
        sorted_dict: Optional[sc_p.SortedDict[str, int]]

    class MyModelWithAnnotated(BaseModel):
        sorted_dict: sc_p.AnnotatedSortedDict

    class MyModelWithAnnotatedWithArg(BaseModel):
        sorted_dict: sc_p.AnnotatedSortedDict[str, int]

    class MyModelManualAnnotation(BaseModel):
        sorted_dict: Annotated[sc.SortedDict, sc_p.SortedDictPydanticAnnotation]

    class MyModelManualAnnotationWithArg(BaseModel):
        sorted_dict: Annotated[sc.SortedDict[str, int], sc_p.SortedDictPydanticAnnotation]

    for model, coerces in (
        (MyModel, False),
        (MyModelWithArg, True),
        (MyModelWithOptional, False),
        (MyModelWithOptionalWithArg, True),
        (MyModelWithAnnotated, False),
        (MyModelWithAnnotatedWithArg, True),
        (MyModelManualAnnotation, False),
        (MyModelManualAnnotationWithArg, True),
    ):
        cases = base_cases + (coercion_cases if coerces else [])
        for case in cases:
            print(f"model: {model}, case: {case}")
            instance = model(sorted_dict=case)
            assert isinstance(instance.sorted_dict, sc.SortedDict)
            assert instance.sorted_dict == expected
            assert instance.model_dump_json() == '{"sorted_dict":{"a":2,"b":3,"c":1}}'


def test_sorted_dict_with_key():
    expected = sc.SortedDict({"c": 1, "a": 2, "b": 3}, key=lambda x: -x)

    annotations = (
        # sortedcontainers_pydantic subclass
        sc_p.SortedDict,
        sc_p.SortedDict[str, int],
        # annotation
        sc_p.AnnotatedSortedDict,
        sc_p.AnnotatedSortedDict[str, int],
        # manual annotation
        Annotated[sc.SortedDict, sc_p.SortedDictPydanticAnnotation],
        Annotated[sc.SortedDict[str, int], sc_p.SortedDictPydanticAnnotation],
    )

    for annotation in annotations:
        ta = TypeAdapter(Annotated[annotation, sc_p.Key(lambda x: -x)])

        ta.validate_python({"c": 1, "a": 2, "b": 3}) == expected
        tuple(ta.validate_python([("c", 1), ("a", 2), ("b", 3)]).keys()) == ("c", "b", "a")
        ta.validate_python({"c": 1.0, "a": 2.0, "b": 3.0}) == expected

        # Wrap in Optional
        ta = TypeAdapter(Optional[Annotated[annotation, sc_p.Key(lambda x: -x)]])
        ta.validate_python({"c": 1, "a": 2, "b": 3}) == expected
        tuple(ta.validate_python([("c", 1), ("a", 2), ("b", 3)]).keys()) == ("c", "b", "a")
        assert ta.validate_python(None) is None

        # Wrap in list
        ta = TypeAdapter(list[Annotated[annotation, sc_p.Key(lambda x: -x)]])
        ta.validate_python([{"c": 1, "a": 2, "b": 3}]) == [expected]


def test_sorted_list():
    expected = sc.SortedList([3, 1, 2])

    base_cases = [
        expected,
        [1, 2, 3],
        [3, 2, 1],
        [3, 1, 2],
        (3, 1, 2),
        {3, 1, 2},
        range(3, 0, -1),
        [2, 3, 1],
    ]
    coercion_cases = [
        sc.SortedList([3.0, 1.0, 2.0]),
        [2.0, 3.0, 1.0],
    ]

    for annotation, coerces in (
        # sortedcontainers_pydantic subclasses
        (sc_p.SortedList, False),
        (sc_p.SortedList[int], True),
        # annotations
        (sc_p.AnnotatedSortedList, False),
        (sc_p.AnnotatedSortedList[int], True),
        # manual annotation
        (Annotated[sc.SortedList, sc_p.SortedListPydanticAnnotation], False),
        (Annotated[sc.SortedList[int], sc_p.SortedListPydanticAnnotation], True),
    ):
        ta = TypeAdapter(annotation)
        cases = base_cases + (coercion_cases if coerces else [])
        for case in cases:
            print(f"annotation: {annotation}, case: {case}")
            actual = ta.validate_python(case)
            assert isinstance(actual, sc.SortedList)
            assert actual == expected
        assert ta.dump_json(expected).decode() == "[1,2,3]"

        # Works inside Optional
        ta = TypeAdapter(Optional[annotation])
        for case in cases:
            print(f"annotation: {annotation}, case: {case}")
            actual = ta.validate_python(case)
            assert isinstance(actual, sc.SortedList)
            assert actual == expected
            assert ta.validate_python(None) is None
        assert ta.dump_json(expected).decode() == "[1,2,3]"

        # Works inside list
        ta = TypeAdapter(list[annotation])
        for case in cases:
            case = [case]
            print(f"annotation: {annotation}, case: {case}")
            actual = ta.validate_python(case)
            assert isinstance(actual, list)
            assert isinstance(actual[0], sc.SortedList)
            assert actual == [expected]
        assert ta.dump_json([expected]).decode() == "[[1,2,3]]"

    assert TypeAdapter(sc_p.SortedList).json_schema() == TypeAdapter(list).json_schema()
    assert TypeAdapter(sc_p.SortedList[int]).json_schema() == TypeAdapter(List[int]).json_schema()
    assert (
        TypeAdapter(Optional[sc_p.SortedList]).json_schema()
        == TypeAdapter(Optional[list]).json_schema()
    )
    assert (
        TypeAdapter(Optional[sc_p.SortedList[int]]).json_schema()
        == TypeAdapter(Optional[List[int]]).json_schema()
    )

    class MyModel(BaseModel):
        sorted_list: sc_p.SortedList

    class MyModelWithArg(BaseModel):
        sorted_list: sc_p.SortedList[int]

    class MyModelWithAnnotated(BaseModel):
        sorted_list: sc_p.AnnotatedSortedList

    class MyModelWithAnnotatedWithArg(BaseModel):
        sorted_list: sc_p.AnnotatedSortedList[int]

    class MyModelManualAnnotation(BaseModel):
        sorted_list: Annotated[sc.SortedList, sc_p.SortedListPydanticAnnotation]

    class MyModelManualAnnotationWithArg(BaseModel):
        sorted_list: Annotated[sc.SortedList[int], sc_p.SortedListPydanticAnnotation]

    for model, coerces in (
        (MyModel, False),
        (MyModelWithArg, True),
        (MyModelWithAnnotated, False),
        (MyModelWithAnnotatedWithArg, True),
        (MyModelManualAnnotation, False),
        (MyModelManualAnnotationWithArg, True),
    ):
        cases = base_cases + (coercion_cases if coerces else [])
        for case in cases:
            print(f"model: {model}, case: {case}")
            instance = model(sorted_list=case)
            assert isinstance(instance.sorted_list, sc.SortedList)
            assert instance.sorted_list == expected
            assert instance.model_dump_json() == '{"sorted_list":[1,2,3]}'


def test_sorted_list_with_key():
    expected = sc.SortedList([3, 1, 2], key=lambda x: -x)

    annotations = (
        # sortedcontainers_pydantic subclass
        sc_p.SortedList,
        sc_p.SortedList[int],
        # annotation
        sc_p.AnnotatedSortedList,
        sc_p.AnnotatedSortedList[int],
        # manual annotation
        Annotated[sc.SortedList, sc_p.SortedListPydanticAnnotation],
        Annotated[sc.SortedList[int], sc_p.SortedListPydanticAnnotation],
    )

    for annotation in annotations:
        ta = TypeAdapter(Annotated[annotation, sc_p.Key(lambda x: -x)])

        ta.validate_python([3, 1, 2]) == expected
        tuple(ta.validate_python([3, 1, 2])) == (3, 2, 1)

        # Wrap in Optional
        ta = TypeAdapter(Optional[Annotated[annotation, sc_p.Key(lambda x: -x)]])
        ta.validate_python([3, 1, 2]) == expected
        assert ta.validate_python(None) is None

        # Wrap in list
        ta = TypeAdapter(list[Annotated[annotation, sc_p.Key(lambda x: -x)]])
        ta.validate_python([[3, 1, 2]]) == [expected]


def test_sorted_set():
    expected = sc.SortedSet([3, 1, 2])

    base_cases = [
        expected,
        [3, 1, 2],
        [1, 2, 3],
        [3, 2, 1],
        (3, 1, 2),
        {3, 1, 2},
        range(3, 0, -1),
        [2, 3, 1],
    ]
    coercion_cases = [
        sc.SortedSet([3.0, 1.0, 2.0]),
        [2.0, 3.0, 1.0],
    ]

    for annotation, coerces in (
        # sortedcontainers_pydantic subclass
        (sc_p.SortedSet, False),
        (sc_p.SortedSet[int], True),
        # annotation
        (sc_p.AnnotatedSortedSet, False),
        (sc_p.AnnotatedSortedSet[int], True),
        # manual annotation
        (Annotated[sc.SortedSet, sc_p.SortedSetPydanticAnnotation], False),
        (Annotated[sc.SortedSet[int], sc_p.SortedSetPydanticAnnotation], True),
    ):
        ta = TypeAdapter(annotation)
        cases = base_cases + (coercion_cases if coerces else [])
        for case in cases:
            print(f"annotation: {annotation}, case: {case}")
            actual = ta.validate_python(case)
            assert isinstance(actual, sc.SortedSet)
            assert actual == expected
        assert ta.dump_json(expected).decode() == "[1,2,3]"

        # Works inside Optional
        ta = TypeAdapter(Optional[annotation])
        for case in cases:
            print(f"annotation: {annotation}, case: {case}")
            actual = ta.validate_python(case)
            assert isinstance(actual, sc.SortedSet)
            assert actual == expected
            assert ta.validate_python(None) is None
        assert ta.dump_json(expected).decode() == "[1,2,3]"

        # Works inside list
        ta = TypeAdapter(list[annotation])
        for case in cases:
            case = [case]
            print(f"annotation: {annotation}, case: {case}")
            actual = ta.validate_python(case)
            assert isinstance(actual, list)
            assert isinstance(actual[0], sc.SortedSet)
            assert actual == [expected]
        assert ta.dump_json([expected]).decode() == "[[1,2,3]]"

    assert TypeAdapter(sc_p.SortedSet).json_schema() == TypeAdapter(set).json_schema()
    assert TypeAdapter(sc_p.SortedSet[int]).json_schema() == TypeAdapter(Set[int]).json_schema()
    assert (
        TypeAdapter(Optional[sc_p.SortedSet]).json_schema()
        == TypeAdapter(Optional[set]).json_schema()
    )
    assert (
        TypeAdapter(Optional[sc_p.SortedSet[int]]).json_schema()
        == TypeAdapter(Optional[Set[int]]).json_schema()
    )

    class MyModel(BaseModel):
        sorted_set: sc_p.SortedSet

    class MyModelWithArg(BaseModel):
        sorted_set: sc_p.SortedSet[int]

    class MyModelWithAnnotated(BaseModel):
        sorted_set: sc_p.AnnotatedSortedSet

    class MyModelWithAnnotatedWithArg(BaseModel):
        sorted_set: sc_p.AnnotatedSortedSet[int]

    class MyModelManualAnnotation(BaseModel):
        sorted_set: Annotated[sc.SortedSet, sc_p.SortedSetPydanticAnnotation]

    class MyModelManualAnnotationWithArg(BaseModel):
        sorted_set: Annotated[sc.SortedSet[int], sc_p.SortedSetPydanticAnnotation]

    for model, coerces in (
        (MyModel, False),
        (MyModelWithArg, True),
        (MyModelWithAnnotated, False),
        (MyModelWithAnnotatedWithArg, True),
        (MyModelManualAnnotation, False),
        (MyModelManualAnnotationWithArg, True),
    ):
        cases = base_cases + (coercion_cases if coerces else [])
        for case in cases:
            print(f"model: {model}, case: {case}")
            instance = model(sorted_set=case)
            assert isinstance(instance.sorted_set, sc.SortedSet)
            assert instance.sorted_set == expected
            assert instance.model_dump_json() == '{"sorted_set":[1,2,3]}'


def test_sorted_set_with_key():
    expected = sc.SortedSet([3, 1, 2], key=lambda x: -x)

    annotations = (
        # sortedcontainers_pydantic subclass
        sc_p.SortedSet,
        sc_p.SortedSet[int],
        # annotation
        sc_p.AnnotatedSortedSet,
        sc_p.AnnotatedSortedSet[int],
        # manual annotation
        Annotated[sc.SortedSet, sc_p.SortedSetPydanticAnnotation],
        Annotated[sc.SortedSet[int], sc_p.SortedSetPydanticAnnotation],
    )

    for annotation in annotations:
        ta = TypeAdapter(Annotated[annotation, sc_p.Key(lambda x: -x)])

        ta.validate_python([3, 1, 2]) == expected
        tuple(ta.validate_python([3, 1, 2])) == (3, 2, 1)

        # Wrap in Optional
        ta = TypeAdapter(Optional[Annotated[annotation, sc_p.Key(lambda x: -x)]])
        ta.validate_python([3, 1, 2]) == expected
        assert ta.validate_python(None) is None

        # Wrap in list
        ta = TypeAdapter(list[Annotated[annotation, sc_p.Key(lambda x: -x)]])
        ta.validate_python([[3, 1, 2]]) == [expected]


def test_annotation_with_bad_source_type():
    for annotation in (
        sc_p.SortedDictPydanticAnnotation,
        sc_p.SortedListPydanticAnnotation,
        sc_p.SortedSetPydanticAnnotation,
    ):
        with pytest.raises(sc_p.UnsupportedSourceTypeError):
            TypeAdapter(Annotated[list, annotation])


def test_key_with_bad_source_type():
    with pytest.raises(sc_p.UnsupportedSourceTypeError):
        TypeAdapter(Annotated[dict, sc_p.Key(lambda x: x)])
