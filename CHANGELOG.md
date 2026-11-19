# Changelog

## v2.1.0 (Unreleased)

- Fixed `Key` validation for items that are only orderable by the key function, such as Pydantic models. Containers now use the key during construction.

- Removed support for Python 3.9.
- Added support for Python 3.14 and 3.15.
- Removed the `tests` optional dependency extra, which only listed pytest.
- Changed the source distribution to contain only the package source, `pyproject.toml`, README, and LICENSE. It previously also included tests and other repository files. This is a result of changing the build backend from hatchling to uv_build.
- Fixed `Key` with `SortedDict` so that the key function is used to sort keys. It was previously added to the dictionary as an item with key `"key"`.
- Fixed the special annotation objects and `Key` to support subclasses at any depth below the sortedcontainers classes. Previously, only direct subclasses were supported.
- Fixed serialization to use the declared item types, consistent with `list[T]` and `dict[K, V]`, so serializers attached to item types now apply. As a result, fields only on a subclass of a declared model item type are no longer included (annotate the item type with `SerializeAsAny`, e.g., `SortedList[SerializeAsAny[Base]]`, to keep them), and items that don't match the declared type emit Pydantic's serializer warning.

## v2.0.0 (2025-04-18)

- Added `SortedDictPydanticAnnotation`, `SortedListPydanticAnnotation`, and `SortedSetPydanticAnnotation` special annotation objects. These can be attached to sortedcontainers' original classes using `typing.Annotated` to enable Pydantic validation and serialization. See [approach 2](./README.md#2-use-the-annotation-pattern) in the README for further details.
- Added `AnnotatedSortedDict`, `AnnotatedSortedList`, and `AnnotatedSortedSet` type aliases that can also be used to enable Pydantic validation and serialization. See [approach 3](./README.md#3-use-the-wrapper-type-aliases) in the README for further details.
- Added support for setting a key function for custom sorting using the `Key` special annotation object with `typing.Annotated`. See the [relevant section](./README.md#specifying-a-key-function-with-key) in the README for futher details.
- Added new class `SortedKeyList`. This is a subclass of both `sortedcontainers.SortedKeyList` and `sortedcontainers_pydantic.SortedList`. When using `Key` with `sortedcontainers_pydantic.SortedList`, this class will be returned, which is analogous to the behavior with `sortedcontainers.SortedList` and `sortedcontainers.SortedKeyList`.
- Removed support for Python 3.8.

## v1.0.0 (2024-03-20)

Initial release! 🎉
