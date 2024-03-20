from typing import TYPE_CHECKING

from pydantic import BaseModel

from sortedcontainers_pydantic import SortedDict, SortedList, SortedSet


class MyModel(BaseModel):
    dct: SortedDict[str, int] = SortedDict()
    lst: SortedList[int] = SortedList()
    st: SortedSet[int] = SortedSet()


if TYPE_CHECKING:
    m = MyModel()

    reveal_type(m.dct)  # noqa: F821
    reveal_type(m.lst)  # noqa: F821
    reveal_type(m.st)  # noqa: F821

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
