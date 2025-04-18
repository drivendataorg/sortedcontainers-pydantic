from typing import TYPE_CHECKING, Annotated

from pydantic import BaseModel

from sortedcontainers_pydantic import (
    AnnotatedSortedDict,
    AnnotatedSortedList,
    AnnotatedSortedSet,
    Key,
    SortedDict,
    SortedList,
    SortedSet,
)


class MyModel(BaseModel):
    # sortedcontainers_pydantic classes
    dct: SortedDict[str, int] = SortedDict()
    lst: SortedList[int] = SortedList()
    st: SortedSet[int] = SortedSet()

    # sortedcontainers_pydantic classes with key
    dct_key: Annotated[SortedDict[str, int], Key(lambda x: -x)] = SortedDict()
    lst_key: Annotated[SortedList[int], Key(lambda x: -x)] = SortedList()
    st_key: Annotated[SortedSet[int], Key(lambda x: -x)] = SortedSet()

    # annotations
    dct_annot: AnnotatedSortedDict[str, int] = SortedDict()
    lst_annot: AnnotatedSortedList[int] = SortedList()
    st_annot: AnnotatedSortedSet[int] = SortedSet()

    # annotations with key
    dct_annot_key: Annotated[AnnotatedSortedDict[str, int], Key(lambda x: -x)] = SortedDict()
    lst_annot_key: Annotated[AnnotatedSortedList[int], Key(lambda x: -x)] = SortedList()
    st_annot_key: Annotated[AnnotatedSortedSet[int], Key(lambda x: -x)] = SortedSet()


if TYPE_CHECKING:
    m = MyModel()

    reveal_type(m.dct)  # noqa: F821
    reveal_type(m.lst)  # noqa: F821
    reveal_type(m.st)  # noqa: F821

    reveal_type(m.dct_key)  # noqa: F821
    reveal_type(m.lst_key)  # noqa: F821
    reveal_type(m.st_key)  # noqa: F821

    reveal_type(m.dct_annot)  # noqa: F821
    reveal_type(m.lst_annot)  # noqa: F821
    reveal_type(m.st_annot)  # noqa: F821

    reveal_type(m.dct_annot_key)  # noqa: F821
    reveal_type(m.lst_annot_key)  # noqa: F821
    reveal_type(m.st_annot_key)  # noqa: F821

MyModel(dct={"c": 1, "a": 2, "b": 3})
MyModel(dct=[("c", 1), ("a", 2), ("b", 3)])
MyModel(dct=(pair for pair in [("c", 1), ("a", 2), ("b", 3)]))

MyModel(lst=[3, 1, 2])
MyModel(lst=(3, 1, 2))
MyModel(lst={3, 1, 2})
MyModel(lst=(i for i in [3, 1, 2]))

MyModel(st=[3, 1, 2])
MyModel(st=(3, 1, 2))
MyModel(st={3, 1, 2})
MyModel(st=(i for i in [3, 1, 2]))
