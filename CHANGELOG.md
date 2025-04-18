# Changelog

## v2.0.0 (Unreleased)

- Added `SortedDictPydanticAnnotation`, `SortedListPydanticAnnotation`, and `SortedSetPydanticAnnotation` special annotation objects. These can be attached to sortedcontainers' original classes using `typing.Annotated` to enable Pydantic validation and serialization. See [approach 2](./README.md#2-use-the-annotation-pattern) in the README for further details.
- Added `AnnotatedSortedDict`, `AnnotatedSortedList`, and `AnnotatedSortedSet` type aliases that can also be used to enable Pydantic validation and serialization. See [approach 3](./README.md#3-use-the-wrapper-type-aliases) in the README for further details.
- Added support for setting a key function for custom sorting using the `Key` special annotation object with `typing.Annotated`. See the [relevant section](./README.md#specifying-a-key-function-with-key) in the README for futher details.
- Added new class `SortedKeyList`. This is a subclass of both `sortedcontainers.SortedKeyList` and `sortedcontainers_pydantic.SortedList`. When using `Key` with `sortedcontainers_pydantic.SortedList`, this class will be returned, which is analogous to the behavior with `sortedcontainers.SortedList` and `sortedcontainers.SortedKeyList`.
- Removed support for Python 3.8.

## v1.0.0 (2024-03-20)

Initial release! 🎉
