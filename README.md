# sortedcontainers-pydantic

[![PyPI](https://img.shields.io/pypi/v/sortedcontainers-pydantic.svg)](https://pypi.org/project/sortedcontainers-pydantic/)
[![conda-forge feedstock](https://img.shields.io/conda/vn/conda-forge/sortedcontainers-pydantic.svg)](https://github.com/conda-forge/sortedcontainers-pydantic-feedstock)
[![Supported Python versions](https://img.shields.io/pypi/pyversions/sortedcontainers-pydantic)](https://pypi.org/project/sortedcontainers-pydantic/)
[![tests](https://github.com/drivendataorg/sortedcontainers-pydantic/actions/workflows/tests.yml/badge.svg?branch=main)](https://github.com/drivendataorg/sortedcontainers-pydantic/actions/workflows/tests.yml?query=branch%3Amain)
[![codecov](https://codecov.io/gh/drivendataorg/sortedcontainers-pydantic/branch/main/graph/badge.svg)](https://codecov.io/gh/drivendataorg/sortedcontainers-pydantic)

This package extends [sortedcontainers](https://github.com/grantjenks/python-sortedcontainers/), a fast pure-Python library for sorted mutable collections, to work with [Pydantic](https://docs.pydantic.dev/latest/)'s models, validation, and serialization.

The easiest way to get started is to simply import `SortedDict`, `SortedList`, or `SortedSet` from `sortedcontainers_pydantic` instead of from `sortedcontainers`.

```python
from pydantic import BaseModel, TypeAdapter
from sortedcontainers_pydantic import SortedList

class MyModel(BaseModel):
    sorted_list: SortedList[int]

MyModel(sorted_list=[3.0, 1.0, 2.0])
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

<sup>Reproducible example created by [reprexlite](https://github.com/jayqi/reprexlite) v1.0.0</sup>

For additional alternative ways to declare types from this library, see the ["Usage approaches"](#usage-approaches) section below.

This library also supports key functions to customize sorting behavior. See the ["Specifying a key function with `Key`"](#specifying-a-key-function-with-key) section for further details.

## Installation

sortedcontainers-pydantic is available on [PyPI](https://pypi.org/project/sortedcontainers-pydantic/). You can install it with

```bash
pip install sortedcontainers-pydantic
```

It is also available on [conda-forge](https://github.com/conda-forge/sortedcontainers-pydantic-feedstock). You can install it with

```bash
conda install sortedcontainers-pydantic --channel conda-forge
```

## Usage approaches

There are three different ways you can use `sortedcontainers-pydantic`.

### 1. Import from sortedcontainers_pydantic

The library has subclasses of sortedcontainers's `SortedDict`, `SortedList`, and `SortedSet` with [Pydantic's special methods](https://docs.pydantic.dev/latest/concepts/types/#customizing-validation-with-__get_pydantic_core_schema__) that enable validation and serialization. To use them, simply import classes of the same name from `sortedcontainers_pydantic`.

```python
from pydantic import BaseModel
from sortedcontainers_pydantic import SortedList

class MyModel(BaseModel):
    sorted_list: SortedList[int]

MyModel(sorted_list=[3.0, 1.0, 2.0])
#> MyModel(sorted_list=SortedList([1, 2, 3]))

MyModel.model_validate_json('{"sorted_list": [3, 1, 2]}')
#> MyModel(sorted_list=SortedList([1, 2, 3]))
```

### 2. Use the annotation pattern

_New in sortedcontainers-pydantic v2.0.0_

The library has special annotation objects `SortedDictPydanticAnnotation`, `SortedListPydanticAnnotation`, and `SortedSetPydanticAnnotation` that can be attached to sortedcontainers's `SortedDict`, `SortedList`, and `SortedSet`, respectively, using `typing.Annotated`. This implements the [annotated pattern](https://docs.pydantic.dev/latest/concepts/types/#handling-third-party-types) supported by Pydantic.

```python
from typing import Annotated

from pydantic import BaseModel
from sortedcontainers import SortedList
from sortedcontainers_pydantic import SortedListPydanticAnnotation

class MyModel(BaseModel):
    sorted_list: Annotated[SortedList[int], SortedListPydanticAnnotation]

MyModel(sorted_list=[3.0, 1.0, 2.0])
#> MyModel(sorted_list=SortedList([1, 2, 3]))
```

Unlike approach 1, the type being used is the original class from sortedcontainers and not a subclass.

### 3. Use the wrapper type aliases

_New in sortedcontainers-pydantic v2.0.0_

You can also use the wrapper types `AnnotatedSortedDict`, `AnnotatedSortedList`, or `AnnotatedSortedSet`. These are simply type aliases implementing approach 2.

```python
from pydantic import BaseModel
from sortedcontainers_pydantic import AnnotatedSortedList

AnnotatedSortedList
#> typing.Annotated[sortedcontainers.sortedlist.SortedList[~_T], <class 'sortedcontainers_pydantic.SortedListPydanticAnnotation'>]

class MyModel(BaseModel):
    sorted_list: AnnotatedSortedList[int]

MyModel(sorted_list=[3.0, 1.0, 2.0])
#> MyModel(sorted_list=SortedList([1, 2, 3]))
```

## Specifying a key function with `Key`

_New in sortedcontainers-pydantic v2.0.0_

You can specify a key function to control sorting. The key should be a callable that takes a single argument. It will be run on every element to generate a key for making comparisons. To specify a key, instantiate the `Key` special annotation object wrapping it, and attach it with `typing.Annotated`. This works with any of the three approaches.

### Example using `Key` with approach 1

```python
from typing import Annotated

from pydantic import BaseModel
from sortedcontainers_pydantic import Key, SortedList

class MyModel(BaseModel):
    sorted_list: Annotated[SortedList[int], Key(lambda x: -x)]

MyModel(sorted_list=[3.0, 1.0, 2.0])
#> MyModel(sorted_list=SortedKeyList([3, 2, 1], key=<function MyModel.<lambda> at 0x10ae058a0>))
```

### Example using `Key` with approach 2

```python
from typing import Annotated

from pydantic import BaseModel
from sortedcontainers import SortedList
from sortedcontainers_pydantic import Key, SortedListPydanticAnnotation

class MyModel(BaseModel):
    sorted_list: Annotated[SortedList[int], SortedListPydanticAnnotation, Key(lambda x: -x)]

MyModel(sorted_list=[3.0, 1.0, 2.0])
#> MyModel(sorted_list=SortedKeyList([3, 2, 1], key=<function MyModel.<lambda> at 0x10aa4a520>))
```

### Example using `Key` with approach 3

```python
from typing import Annotated

from pydantic import BaseModel
from sortedcontainers_pydantic import AnnotatedSortedList, Key

class MyModel(BaseModel):
    sorted_list: Annotated[AnnotatedSortedList[int], Key(lambda x: -x)]

MyModel(sorted_list=[3.0, 1.0, 2.0])
#> MyModel(sorted_list=SortedKeyList([3, 2, 1], key=<function MyModel.<lambda> at 0x10ca65080>))
```

---

<sup>Reproducible examples created by [reprexlite](https://github.com/jayqi/reprexlite) v1.0.0</sup>
