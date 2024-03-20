# sortedcontainers-pydantic

[![PyPI](https://img.shields.io/pypi/v/sortedcontainers-pydantic.svg)](https://pypi.org/project/sortedcontainers-pydantic/)
[![Supported Python versions](https://img.shields.io/pypi/pyversions/sortedcontainers-pydantic)](https://pypi.org/project/sortedcontainers-pydantic/)
[![tests](https://github.com/drivendataorg/sortedcontainers-pydantic/actions/workflows/tests.yml/badge.svg?branch=main)](https://github.com/drivendataorg/sortedcontainers-pydantic/actions/workflows/tests.yml?query=branch%3Amain)
[![codecov](https://codecov.io/gh/drivendataorg/sortedcontainers-pydantic/branch/main/graph/badge.svg)](https://codecov.io/gh/drivendataorg/sortedcontainers-pydantic)

This package adds [Pydantic](https://docs.pydantic.dev/latest/) support to [sortedcontainers](https://github.com/grantjenks/python-sortedcontainers/), a fast pure-Python library for sorted mutable collections. 

It implements [Pydantic's special methods](https://docs.pydantic.dev/latest/concepts/types/#customizing-validation-with-__get_pydantic_core_schema__) on subclasses of sortedcontainer's `SortedDict`, `SortedList`, and `SortedSet` classes so that you can use them with Pydantic's models, validation, and serialization. To use, simply import the respective class of the same name from `sortedcontainers_pydantic` instead of from `sortedcontainers`. Only Pydantic V2 is supported.

```python
from pydantic import BaseModel, TypeAdapter
from sortedcontainers_pydantic import SortedList

class MyModel(BaseModel):
    sorted_list: SortedList[int]

MyModel(sorted_list=[3, 1, 2])
#> MyModel(sorted_list=SortedList([1, 2, 3]))

MyModel.model_validate_json('{"sorted_list": [3, 1, 2]}')
#> MyModel(sorted_list=SortedList([1, 2, 3]))

MyModel(sorted_list=[3, 1, 2]).model_dump_json()
#> '{"sorted_list":[1,2,3]}'

TypeAdapter(SortedList).validate_python([3, 1, 2])
#> SortedList([1, 2, 3])

TypeAdapter(SortedList).validate_json("[3, 1, 2]")
#> SortedList([1, 2, 3])
```

<sup>Reproducible example created by [reprexlite](https://github.com/jayqi/reprexlite) v0.5.0</sup>

## Installation

sortedcontainers-pydantic is available on [PyPI](https://pypi.org/project/sortedcontainers-pydantic/). You can install it with 

```bash
pip install sortedcontainers-pydantic
```
