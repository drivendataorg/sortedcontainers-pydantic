from typing import Annotated, Callable, Dict, Iterable, List, Optional, Set

from pydantic import (
    AfterValidator,
    BaseModel,
    PlainSerializer,
    PlainValidator,
    SerializeAsAny,
    TypeAdapter,
)
import pytest
import sortedcontainers as sc

import sortedcontainers_pydantic as sc_p


def test_get_constructor():
    assert sc_p._get_constructor(sc.SortedDict) is sc.SortedDict
    assert sc_p._get_constructor(sc.SortedDict[str, int]) is sc.SortedDict
    assert sc_p._get_constructor(sc.SortedList) is sc.SortedList
    assert sc_p._get_constructor(sc.SortedList[int]) is sc.SortedList
    assert sc_p._get_constructor(sc.SortedSet) is sc.SortedSet
    assert sc_p._get_constructor(sc.SortedSet[int]) is sc.SortedSet
    assert sc_p._get_constructor(sc_p.SortedDict) is sc_p.SortedDict
    assert sc_p._get_constructor(sc_p.SortedDict[str, int]) is sc_p.SortedDict
    assert sc_p._get_constructor(sc_p.SortedList) is sc_p.SortedList
    assert sc_p._get_constructor(sc_p.SortedList[int]) is sc_p.SortedList
    assert sc_p._get_constructor(sc_p.SortedSet) is sc_p.SortedSet
    assert sc_p._get_constructor(sc_p.SortedSet[int]) is sc_p.SortedSet

    # Test with a custom subclass
    class CustomSortedDict(sc.SortedDict): ...

    assert sc_p._get_constructor(CustomSortedDict) is CustomSortedDict
    assert sc_p._get_constructor(CustomSortedDict[str, int]) is CustomSortedDict

    class CustomSCPSortedDict(sc_p.SortedDict): ...

    assert sc_p._get_constructor(CustomSCPSortedDict) is CustomSCPSortedDict
    assert sc_p._get_constructor(CustomSCPSortedDict[str, int]) is CustomSCPSortedDict

    # Test with subclasses and subclasses of subclasses
    for base in (
        sc.SortedDict,
        sc.SortedList,
        sc.SortedKeyList,
        sc.SortedSet,
        sc_p.SortedDict,
        sc_p.SortedList,
        sc_p.SortedKeyList,
        sc_p.SortedSet,
    ):

        class Child(base): ...

        class Grandchild(Child): ...

        assert sc_p._get_constructor(Child) is Child
        assert sc_p._get_constructor(Grandchild) is Grandchild
        assert sc_p._get_constructor(Grandchild[int]) is Grandchild


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
    expected = sc.SortedDict(lambda x: -ord(x), {"c": 1, "a": 2, "b": 3})

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
        ta = TypeAdapter(Annotated[annotation, sc_p.Key(lambda x: -ord(x))])

        assert ta.validate_python({"c": 1, "a": 2, "b": 3}) == expected
        assert tuple(ta.validate_python([("c", 1), ("a", 2), ("b", 3)]).keys()) == ("c", "b", "a")
        assert ta.validate_python({"c": 1.0, "a": 2.0, "b": 3.0}) == expected

        # Wrap in Optional
        ta = TypeAdapter(Optional[Annotated[annotation, sc_p.Key(lambda x: -ord(x))]])
        assert ta.validate_python({"c": 1, "a": 2, "b": 3}) == expected
        assert tuple(ta.validate_python([("c", 1), ("a", 2), ("b", 3)]).keys()) == ("c", "b", "a")
        assert ta.validate_python(None) is None

        # Wrap in list
        ta = TypeAdapter(list[Annotated[annotation, sc_p.Key(lambda x: -ord(x))]])
        assert ta.validate_python([{"c": 1, "a": 2, "b": 3}]) == [expected]


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

        assert ta.validate_python([3, 1, 2]) == expected
        assert tuple(ta.validate_python([3, 1, 2])) == (3, 2, 1)

        # Wrap in Optional
        ta = TypeAdapter(Optional[Annotated[annotation, sc_p.Key(lambda x: -x)]])
        assert ta.validate_python([3, 1, 2]) == expected
        assert ta.validate_python(None) is None

        # Wrap in list
        ta = TypeAdapter(list[Annotated[annotation, sc_p.Key(lambda x: -x)]])
        assert ta.validate_python([[3, 1, 2]]) == [expected]


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

        assert ta.validate_python([3, 1, 2]) == expected
        assert tuple(ta.validate_python([3, 1, 2])) == (3, 2, 1)

        # Wrap in Optional
        ta = TypeAdapter(Optional[Annotated[annotation, sc_p.Key(lambda x: -x)]])
        assert ta.validate_python([3, 1, 2]) == expected
        assert ta.validate_python(None) is None

        # Wrap in list
        ta = TypeAdapter(list[Annotated[annotation, sc_p.Key(lambda x: -x)]])
        assert ta.validate_python([[3, 1, 2]]) == [expected]


IntAsStr = Annotated[int, PlainSerializer(lambda x: str(x), return_type=str)]


def test_item_serializers():
    class Item(BaseModel):
        x: int

    class SubItem(Item):
        y: int

    sorted_dict = sc.SortedDict({"b": 2, "a": 1})
    sorted_list = sc.SortedList([2, 1])
    sorted_set = sc.SortedSet([2, 1])
    sorted_dict_of_sub_items = sc.SortedDict({"a": SubItem(x=1, y=2)})

    for annotation, value, expected_json, expected_python in (
        # sortedcontainers_pydantic subclasses
        (sc_p.SortedDict[str, IntAsStr], sorted_dict, '{"a":"1","b":"2"}', {"a": "1", "b": "2"}),
        (
            sc_p.SortedDict[IntAsStr, int],
            sc.SortedDict({2: 1, 1: 2}),
            '{"1":2,"2":1}',
            {"1": 2, "2": 1},
        ),
        (sc_p.SortedList[IntAsStr], sorted_list, '["1","2"]', ["1", "2"]),
        (sc_p.SortedSet[IntAsStr], sorted_set, '["1","2"]', ["1", "2"]),
        (sc_p.SortedKeyList[IntAsStr, int], sc.SortedKeyList([2, 1]), '["1","2"]', ["1", "2"]),
        # annotations
        (
            sc_p.AnnotatedSortedDict[str, IntAsStr],
            sorted_dict,
            '{"a":"1","b":"2"}',
            {"a": "1", "b": "2"},
        ),
        (sc_p.AnnotatedSortedList[IntAsStr], sorted_list, '["1","2"]', ["1", "2"]),
        (sc_p.AnnotatedSortedSet[IntAsStr], sorted_set, '["1","2"]', ["1", "2"]),
        # manual annotations
        (
            Annotated[sc.SortedDict[str, IntAsStr], sc_p.SortedDictPydanticAnnotation],
            sorted_dict,
            '{"a":"1","b":"2"}',
            {"a": "1", "b": "2"},
        ),
        (
            Annotated[sc.SortedList[IntAsStr], sc_p.SortedListPydanticAnnotation],
            sorted_list,
            '["1","2"]',
            ["1", "2"],
        ),
        (
            Annotated[sc.SortedSet[IntAsStr], sc_p.SortedSetPydanticAnnotation],
            sorted_set,
            '["1","2"]',
            ["1", "2"],
        ),
        # with key
        (
            Annotated[sc_p.SortedDict[str, IntAsStr], sc_p.Key(lambda x: -ord(x))],
            sc.SortedDict(lambda x: -ord(x), {"a": 1, "b": 2}),
            '{"b":"2","a":"1"}',
            {"b": "2", "a": "1"},
        ),
        (
            Annotated[sc_p.SortedList[IntAsStr], sc_p.Key(lambda x: -x)],
            sc.SortedKeyList([1, 2], key=lambda x: -x),
            '["2","1"]',
            ["2", "1"],
        ),
        (
            Annotated[sc_p.SortedSet[IntAsStr], sc_p.Key(lambda x: -x)],
            sc.SortedSet([1, 2], key=lambda x: -x),
            '["2","1"]',
            ["2", "1"],
        ),
        # model items are serialized as the declared type
        (
            sc_p.SortedDict[str, Item],
            sorted_dict_of_sub_items,
            '{"a":{"x":1}}',
            {"a": {"x": 1}},
        ),
        (
            sc_p.SortedDict[str, SerializeAsAny[Item]],
            sorted_dict_of_sub_items,
            '{"a":{"x":1,"y":2}}',
            {"a": {"x": 1, "y": 2}},
        ),
    ):
        print(f"annotation: {annotation}, value: {value}")
        ta = TypeAdapter(annotation)
        assert ta.dump_json(value).decode() == expected_json
        assert ta.dump_python(value) == expected_python


def test_serialization_json_schema():
    as_str = PlainSerializer(lambda x: str(list(x)), return_type=str)

    for annotation, reference in (
        # sortedcontainers_pydantic subclasses
        (sc_p.SortedDict, dict),
        (sc_p.SortedDict[str, IntAsStr], Dict[str, IntAsStr]),
        (sc_p.SortedList, list),
        (sc_p.SortedList[IntAsStr], List[IntAsStr]),
        (sc_p.SortedSet, set),
        (sc_p.SortedSet[IntAsStr], Set[IntAsStr]),
        # annotations
        (sc_p.AnnotatedSortedDict[str, IntAsStr], Dict[str, IntAsStr]),
        (sc_p.AnnotatedSortedList[IntAsStr], List[IntAsStr]),
        (sc_p.AnnotatedSortedSet[IntAsStr], Set[IntAsStr]),
        # manual annotations
        (
            Annotated[sc.SortedDict[str, IntAsStr], sc_p.SortedDictPydanticAnnotation],
            Dict[str, IntAsStr],
        ),
        (Annotated[sc.SortedList[IntAsStr], sc_p.SortedListPydanticAnnotation], List[IntAsStr]),
        (Annotated[sc.SortedSet[IntAsStr], sc_p.SortedSetPydanticAnnotation], Set[IntAsStr]),
        # wrapped
        (Optional[sc_p.SortedSet[IntAsStr]], Optional[Set[IntAsStr]]),
        (Annotated[sc_p.SortedSet[IntAsStr], sc_p.Key(lambda x: -x)], Set[IntAsStr]),
        # serializer replaced
        (Annotated[sc_p.SortedDict[str, int], as_str], Annotated[Dict[str, int], as_str]),
        (Annotated[sc_p.SortedList[int], as_str], Annotated[List[int], as_str]),
        (Annotated[sc_p.SortedSet[int], as_str], Annotated[Set[int], as_str]),
        (Annotated[sc_p.AnnotatedSortedSet[int], as_str], Annotated[Set[int], as_str]),
    ):
        print(f"annotation: {annotation}")
        assert TypeAdapter(annotation).json_schema(mode="serialization") == TypeAdapter(
            reference
        ).json_schema(mode="serialization")


def test_subclass_of_subclass():
    class ChildSortedDict(sc.SortedDict): ...

    class GrandchildSortedDict(ChildSortedDict): ...

    class ChildSortedList(sc.SortedList): ...

    class GrandchildSortedList(ChildSortedList): ...

    class ChildSortedKeyList(sc.SortedKeyList): ...

    class GrandchildSortedKeyList(ChildSortedKeyList): ...

    class ChildSortedSet(sc.SortedSet): ...

    class GrandchildSortedSet(ChildSortedSet): ...

    class ChildSCPSortedDict(sc_p.SortedDict): ...

    class GrandchildSCPSortedDict(ChildSCPSortedDict): ...

    class ChildSCPSortedKeyList(sc_p.SortedKeyList): ...

    class GrandchildSCPSortedKeyList(ChildSCPSortedKeyList): ...

    class ChildSCPSortedSet(sc_p.SortedSet): ...

    class GrandchildSCPSortedSet(ChildSCPSortedSet): ...

    def reverse(x):
        return -ord(x)

    for annotation, case, expected_type, expected in (
        # annotation
        (
            Annotated[GrandchildSortedDict, sc_p.SortedDictPydanticAnnotation],
            {"c": 1, "a": 2, "b": 3},
            GrandchildSortedDict,
            ("a", "b", "c"),
        ),
        (
            Annotated[GrandchildSortedList, sc_p.SortedListPydanticAnnotation],
            ["c", "a", "b"],
            GrandchildSortedList,
            ("a", "b", "c"),
        ),
        (
            Annotated[GrandchildSortedSet, sc_p.SortedSetPydanticAnnotation],
            ["c", "a", "b"],
            GrandchildSortedSet,
            ("a", "b", "c"),
        ),
        # annotation with key
        (
            Annotated[GrandchildSortedDict, sc_p.SortedDictPydanticAnnotation, sc_p.Key(reverse)],
            {"c": 1, "a": 2, "b": 3},
            GrandchildSortedDict,
            ("c", "b", "a"),
        ),
        (
            Annotated[
                GrandchildSortedKeyList, sc_p.SortedListPydanticAnnotation, sc_p.Key(reverse)
            ],
            ["c", "a", "b"],
            GrandchildSortedKeyList,
            ("c", "b", "a"),
        ),
        (
            Annotated[GrandchildSortedSet, sc_p.SortedSetPydanticAnnotation, sc_p.Key(reverse)],
            ["c", "a", "b"],
            GrandchildSortedSet,
            ("c", "b", "a"),
        ),
        # sortedcontainers_pydantic subclass with key
        (
            Annotated[GrandchildSCPSortedDict, sc_p.Key(reverse)],
            {"c": 1, "a": 2, "b": 3},
            GrandchildSCPSortedDict,
            ("c", "b", "a"),
        ),
        (
            Annotated[GrandchildSCPSortedKeyList, sc_p.Key(reverse)],
            ["c", "a", "b"],
            GrandchildSCPSortedKeyList,
            ("c", "b", "a"),
        ),
        (
            Annotated[GrandchildSCPSortedSet, sc_p.Key(reverse)],
            ["c", "a", "b"],
            GrandchildSCPSortedSet,
            ("c", "b", "a"),
        ),
    ):
        print(f"annotation: {annotation}, case: {case}")
        actual = TypeAdapter(annotation).validate_python(case)
        assert type(actual) is expected_type
        assert tuple(actual) == expected


def test_annotation_with_bad_source_type():
    for annotation in (
        sc_p.SortedDictPydanticAnnotation,
        sc_p.SortedListPydanticAnnotation,
        sc_p.SortedSetPydanticAnnotation,
    ):
        with pytest.raises(sc_p.UnsupportedSourceTypeError):
            TypeAdapter(Annotated[list, annotation])
        # Source type whose origin is not a class
        with pytest.raises(sc_p.UnsupportedSourceTypeError):
            TypeAdapter(Annotated[Optional[sc.SortedList], annotation])


def test_key_with_bad_source_type():
    with pytest.raises(sc_p.UnsupportedSourceTypeError):
        TypeAdapter(Annotated[dict, sc_p.Key(lambda x: x)])


def test_key_orders_models_without_natural_order():
    class Item(BaseModel):
        model_config = {"frozen": True}
        x: int

    def key(item):
        return item.x

    for annotation in (
        sc_p.SortedList[Item],
        sc_p.AnnotatedSortedList[Item],
        sc_p.SortedKeyList[Item, int],
        sc_p.SortedSet[Item],
        sc_p.AnnotatedSortedSet[Item],
    ):
        adapter = TypeAdapter(Annotated[annotation, sc_p.Key(key)])
        for value in ([{"x": 2}, {"x": 1}], [Item(x=2), Item(x=1)]):
            result = adapter.validate_python(value)
            assert [item.x for item in result] == [1, 2]
            assert result.key is key
            assert adapter.dump_json(result) == b'[{"x":1},{"x":2}]'
        result = adapter.validate_json('[{"x":2},{"x":1}]')
        assert [item.x for item in result] == [1, 2]

    for annotation in (sc_p.SortedDict[Item, str], sc_p.AnnotatedSortedDict[Item, str]):
        adapter = TypeAdapter(Annotated[annotation, sc_p.Key(key)])
        result = adapter.validate_python({Item(x=2): "two", Item(x=1): "one"})
        assert [item.x for item in result] == [1, 2]
        assert list(result.values()) == ["one", "two"]


def test_key_replaces_existing_instance_key_without_touching_nested_containers():
    def reverse(value):
        return -value

    for annotation, value in (
        (sc_p.SortedList, sc_p.SortedList([1, 2])),
        (sc_p.SortedSet, sc_p.SortedSet([1, 2])),
        (sc_p.SortedDict, sc_p.SortedDict({1: "one", 2: "two"})),
    ):
        result = TypeAdapter(Annotated[annotation, sc_p.Key(reverse)]).validate_python(value)
        assert list(result) == [2, 1]
        assert result.key is reverse
        assert list(value) == [1, 2]

    adapter = TypeAdapter(Annotated[sc_p.SortedList[sc_p.SortedList[int]], sc_p.Key(len)])
    result = adapter.validate_python([[3, 1], [2]])
    assert [list(item) for item in result] == [[2], [1, 3]]


def test_key_preserves_validation_wrappers_and_last_key_wins():
    calls = []

    def observe(value):
        assert isinstance(value, sc.SortedList)
        calls.append(list(value))
        return value

    reverse = sc_p.Key(lambda value: -value)
    annotation = Annotated[sc_p.SortedList[int], AfterValidator(observe), reverse]
    result = TypeAdapter(annotation).validate_python(["1", "2"])
    assert list(result) == [2, 1]
    assert calls == [[2, 1]]
    adapter = TypeAdapter(Annotated[annotation, sc_p.Key(lambda value: value)])
    assert list(adapter.validate_python([2, 1])) == [1, 2]
    adapter = TypeAdapter(
        Annotated[sc_p.SortedList[int], PlainValidator(lambda value: value), reverse]
    )
    assert list(adapter.validate_python([1, 2])) == [2, 1]
