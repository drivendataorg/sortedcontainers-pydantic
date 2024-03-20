from typing import Tuple

from pydantic import BaseModel

from sortedcontainers_pydantic import SortedDict, SortedList, SortedSet


class MyModel(BaseModel):
    sorted_dict: SortedDict[str, int]
    sorted_list: SortedList[float]
    sorted_set: SortedSet[Tuple[int, int]]


m = MyModel(
    sorted_dict={"carol": 2, "alice": 3, "bob": 1},
    sorted_list=[3.0, 2.0, 1.0],
    sorted_set={(2, 9), (3, 5), (1, 3)},
)
print(repr(m))
#> MyModel(sorted_dict=SortedDict({'alpha': 3, 'bravo': 1, 'charlie': 2}), sorted_list=SortedList([1.0, 2.0, 3.0]), sorted_set=SortedSet([(1, 3), (2, 9), (3, 5)]))
print(m.model_dump_json())
#> {"sorted_dict":{"alpha":3,"bravo":1,"charlie":2},"sorted_list":[1.0,2.0,3.0],"sorted_set":[[1,3],[2,9],[3,5]]}

m2 = MyModel.model_validate_json(m.model_dump_json())
assert m == m2
print(repr(m2))
#> MyModel(sorted_dict=SortedDict({'alpha': 3, 'bravo': 1, 'charlie': 2}), sorted_list=SortedList([1.0, 2.0, 3.0]), sorted_set=SortedSet([(1, 3), (2, 9), (3, 5)]))
