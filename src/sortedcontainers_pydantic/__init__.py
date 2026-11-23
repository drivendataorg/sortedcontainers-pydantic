from dataclasses import dataclass
from functools import partial
import importlib.metadata
from typing import (
    TYPE_CHECKING,
    Annotated,
    Any,
    Callable,
    Dict,
    Hashable,
    Iterable,
    List,
    Mapping,
    Optional,
    Set,
    Tuple,
    TypeVar,
    get_args,
    get_origin,
)

from pydantic import (
    GetCoreSchemaHandler,
    GetJsonSchemaHandler,
)
from pydantic.json_schema import JsonSchemaValue
from pydantic_core import core_schema
import sortedcontainers

if TYPE_CHECKING:
    from _typeshed import SupportsRichComparison


__version__ = importlib.metadata.version("sortedcontainers-pydantic")

__all__ = [
    "SortedDict",
    "SortedList",
    "SortedSet",
    "SortedKeyList",
    "SortedDictPydanticAnnotation",
    "SortedListPydanticAnnotation",
    "SortedSetPydanticAnnotation",
    "AnnotatedSortedDict",
    "AnnotatedSortedList",
    "AnnotatedSortedSet",
    "Key",
    "UnsupportedSourceTypeError",
]

_KT = TypeVar("_KT", bound=Hashable)  # Key type.
_VT = TypeVar("_VT")  # Value type.
_T = TypeVar("_T")
_OrderableT = TypeVar("_OrderableT", bound="SupportsRichComparison")
_HashableT = TypeVar("_HashableT", bound=Hashable)


class _UnsupportedSourceTypeError(Exception):
    def __init__(self, parsed: Any):
        self.parsed = parsed


class UnsupportedSourceTypeError(TypeError):
    pass


class _KeyMarker:
    """Marker that Key attaches to the source type to pass the key function to the
    sortedcontainers class schema.
    """

    def __init__(self, key: Callable[[Any], "SupportsRichComparison"]):
        self.key = key

    def __get_pydantic_core_schema__(
        self, source_type: Any, handler: GetCoreSchemaHandler
    ) -> core_schema.CoreSchema:
        # Reached when the source type's own class generates the schema, e.g.,
        # Annotated[SortedList[int], Key(...)]
        cls = _get_constructor(source_type)
        if issubclass(
            cls,
            (
                SortedDictPydanticAnnotation,
                SortedListPydanticAnnotation,
                SortedSetPydanticAnnotation,
            ),
        ):
            return cls.__get_pydantic_core_schema__(Annotated[source_type, self], handler)  # type: ignore[no-any-return]
        return handler(source_type)


def _split_key(
    source_type: Any,
) -> Tuple[Any, Optional[Callable[[Any], "SupportsRichComparison"]]]:
    """Split a source type with a _KeyMarker into the unmarked source type and the key function."""
    if get_origin(source_type) is Annotated:
        tp, *metadata = get_args(source_type)
        if len(metadata) == 1 and isinstance(metadata[0], _KeyMarker):
            return tp, metadata[0].key
    return source_type, None


def _with_key(cls: Any, key: Optional[Callable[[Any], "SupportsRichComparison"]]) -> Any:
    """Get a constructor for the given sortedcontainers class that uses the given key function."""
    if key is None:
        return cls
    # sortedcontainers.SortedList has magic behavior where the SortedList constructor returns
    # SortedKeyList if given a key. We match that behavior for our SortedList.
    if cls is SortedList:
        cls = SortedKeyList
    # SortedDict takes the key function as its first positional argument and treats keyword
    # arguments as items.
    if issubclass(cls, sortedcontainers.SortedDict):
        return partial(cls, key)
    return partial(cls, key=key)


def _get_constructor(tp: Any) -> Any:
    """Get the relevant class constructor for the given type annotation, e.g., SortedList from
    SortedList[int] or appropriate subclass.
    """
    # Parse the annotation to get the relevant source type, e.g., SortedList form SortedList[int]
    origin = get_origin(tp)
    if origin is None:
        parsed = tp
    else:
        parsed = origin

    if isinstance(parsed, type) and issubclass(
        parsed,
        (sortedcontainers.SortedList, sortedcontainers.SortedDict, sortedcontainers.SortedSet),
    ):
        return parsed
    else:
        raise _UnsupportedSourceTypeError(parsed)


class SortedDictPydanticAnnotation:
    @classmethod
    def __get_pydantic_core_schema__(
        cls, source_type: Any, handler: GetCoreSchemaHandler
    ) -> core_schema.CoreSchema:
        """
        Returns pydantic_core.CoreSchema that defines how Pydantic should validate and
        serialize this class.

        - Validating from JSON: Validate as an iterable and pass to SortedList
          constructor
        - Validating from Python:
            - If it's already a SortedList, do nothing
            - If it's an iterable, pass to SortedList constructor
        - Serialization: Convert to a list
        """
        source_type, key = _split_key(source_type)
        if cls is SortedDictPydanticAnnotation:
            # Used as annotation, i.e., Annotated[..., SortedDictPydanticAnnotation]
            try:
                cls = _get_constructor(source_type)
            except _UnsupportedSourceTypeError as e:
                msg = (
                    "Expected subclass of sortedcontainers.SortedDict, "
                    f"got '{e.parsed}' parsed from annotation '{source_type}'."
                )
                raise UnsupportedSourceTypeError(msg) from e

        constructor = _with_key(cls, key)

        # Schema for when the input is already an instance of this class
        instance_schema = core_schema.is_instance_schema(cls)

        # Get schema for Iterable type based on source type has arguments
        args = get_args(source_type)
        if args:
            mapping_t_schema = handler.generate_schema(Mapping[args[0], args[1]])  # type: ignore[valid-type]
            iterable_of_pairs_t_schema = handler.generate_schema(Iterable[Tuple[args[0], args[1]]])  # type: ignore[valid-type]
            dict_t_schema = handler.generate_schema(Dict[args[0], args[1]])  # type: ignore[valid-type]
        else:
            mapping_t_schema = handler.generate_schema(Mapping)
            iterable_of_pairs_t_schema = handler.generate_schema(Iterable[Tuple[Any, Any]])
            dict_t_schema = handler.generate_schema(Dict)

        # Schema for when the input is a mapping
        from_mapping_schema = core_schema.no_info_after_validator_function(
            function=constructor, schema=mapping_t_schema
        )

        # Schema for when the input is an iterable of pairs
        from_iterable_of_pairs_schema = core_schema.no_info_after_validator_function(
            function=constructor, schema=iterable_of_pairs_t_schema
        )

        # Union the schemas
        # Only include instance_schema if there are no type arguments or key function
        # Otherwise an existing instance with wrong argument types or key function won't be coerced
        if args or key is not None:
            python_schema = core_schema.union_schema(
                [from_mapping_schema, from_iterable_of_pairs_schema]
            )
        else:
            python_schema = core_schema.union_schema(
                [instance_schema, from_mapping_schema, from_iterable_of_pairs_schema]
            )

        # Serializer that converts an instance to a dict, using the schema for the key and value
        # types to serialize the contents
        as_dict_serializer = core_schema.plain_serializer_function_ser_schema(
            dict, return_schema=dict_t_schema
        )

        return core_schema.json_or_python_schema(
            json_schema=from_mapping_schema,
            python_schema=python_schema,
            serialization=as_dict_serializer,
        )


class SortedDict(sortedcontainers.SortedDict[_KT, _VT], SortedDictPydanticAnnotation):
    pass


AnnotatedSortedDict = Annotated[
    sortedcontainers.SortedDict[_KT, _VT], SortedDictPydanticAnnotation
]


class SortedListPydanticAnnotation:
    @classmethod
    def __get_pydantic_core_schema__(
        cls, source_type: Any, handler: GetCoreSchemaHandler
    ) -> core_schema.CoreSchema:
        """
        Returns pydantic_core.CoreSchema that defines how Pydantic should validate and
        serialize this class.

        - Validating from JSON: Validate as an iterable and pass to SortedList
          constructor
        - Validating from Python:
            - If it's already a SortedList, do nothing
            - If it's an iterable, pass to SortedList constructor
        - Serialization: Convert to a list
        """
        source_type, key = _split_key(source_type)
        if cls is SortedListPydanticAnnotation:
            # Used as annotation, e.g., Annotated[..., SortedListPydanticAnnotation]
            try:
                cls = _get_constructor(source_type)
            except _UnsupportedSourceTypeError as e:
                msg = (
                    "Expected subclass of sortedcontainers.SortedList, "
                    f"got '{e.parsed}' parsed from annotation '{source_type}'."
                )
                raise UnsupportedSourceTypeError(msg) from e

        constructor = _with_key(cls, key)

        # Schema for when the input is already an instance of this class
        instance_schema = core_schema.is_instance_schema(cls)

        # Get schema for Iterable type based on source type has arguments
        args = get_args(source_type)
        if args:
            iterable_t_schema = handler.generate_schema(Iterable[args[0]])  # type: ignore[valid-type]
            list_t_schema = handler.generate_schema(List[args[0]])  # type: ignore[valid-type]
        else:
            iterable_t_schema = handler.generate_schema(Iterable)
            list_t_schema = handler.generate_schema(List)

        # Schema for when the input is an iterable
        from_iterable_schema = core_schema.no_info_after_validator_function(
            function=constructor, schema=iterable_t_schema
        )

        # Union of the two schemas
        # Only include instance_schema if there are no type arguments or key function
        # Otherwise an existing instance with wrong argument types or key function won't be coerced
        python_schema: core_schema.CoreSchema
        if args or key is not None:
            python_schema = from_iterable_schema
        else:
            python_schema = core_schema.union_schema([instance_schema, from_iterable_schema])

        # Serializer that converts an instance to a list, using the schema for the item type to
        # serialize the items
        as_list_serializer = core_schema.plain_serializer_function_ser_schema(
            list, return_schema=list_t_schema
        )

        return core_schema.json_or_python_schema(
            json_schema=from_iterable_schema,
            python_schema=python_schema,
            serialization=as_list_serializer,
        )


class SortedList(sortedcontainers.SortedList[_T], SortedListPydanticAnnotation):
    pass


class SortedKeyList(sortedcontainers.SortedKeyList[_T, _OrderableT], SortedList[_T]):
    pass


AnnotatedSortedList = Annotated[sortedcontainers.SortedList[_T], SortedListPydanticAnnotation]

# Don't define AnnotatedSortedKeyList
# We generally don't expect people to directly use SortedKeyList in a field definition
# They should use SortedList instead


class _UniqueItems:
    """Annotation that adds `uniqueItems: true` to an array JSON schema."""

    @classmethod
    def __get_pydantic_json_schema__(
        cls, schema: core_schema.CoreSchema, handler: GetJsonSchemaHandler
    ) -> JsonSchemaValue:
        json_schema = handler(schema)
        json_schema["uniqueItems"] = True
        return json_schema


class SortedSetPydanticAnnotation:
    @classmethod
    def __get_pydantic_core_schema__(
        cls, source_type: Any, handler: GetCoreSchemaHandler
    ) -> core_schema.CoreSchema:
        """
        Returns pydantic_core.CoreSchema that defines how Pydantic should validate and
        serialize this class.

        - Validating from JSON: Validate as an iterable and pass to SortedSet
          constructor
        - Validating from Python:
            - If it's already a SortedSet, do nothing
            - If it's a set, parse as a set and pass to SortedSet constructor
            - If it's an iterable, pass to SortedSet constructor
        - Serialization: Convert to a list
        """
        source_type, key = _split_key(source_type)
        if cls is SortedSetPydanticAnnotation:
            # Used as annotation, i.e., Annotated[..., SortedSetPydanticAnnotation]
            try:
                cls = _get_constructor(source_type)
            except _UnsupportedSourceTypeError as e:
                msg = (
                    "Expected subclass of sortedcontainers.SortedSet, "
                    f"got '{e.parsed}' parsed from annotation '{source_type}'."
                )
                raise UnsupportedSourceTypeError(msg) from e

        constructor = _with_key(cls, key)

        # Schema for when the input is already an instance of this class
        instance_schema = core_schema.is_instance_schema(cls)

        # Get schema for Iterable type based on source type has arguments
        args = get_args(source_type)
        if args:
            set_t_schema = handler.generate_schema(Set[args[0]])  # type: ignore[valid-type]
            iterable_t_schema = handler.generate_schema(Iterable[args[0]])  # type: ignore[valid-type]
            list_t_schema = handler.generate_schema(Annotated[List[args[0]], _UniqueItems])  # type: ignore[valid-type]
        else:
            set_t_schema = handler.generate_schema(Set)
            iterable_t_schema = handler.generate_schema(Iterable)
            list_t_schema = handler.generate_schema(Annotated[List, _UniqueItems])

        # Schema for when the input is a set
        from_set_schema = core_schema.no_info_after_validator_function(
            function=constructor, schema=set_t_schema
        )

        # Schema for when the input is an iterable
        from_iterable_schema = core_schema.no_info_after_validator_function(
            function=constructor, schema=iterable_t_schema
        )

        # Union of the schemas
        # Only include instance_schema if there are no type arguments or key function
        # Otherwise an existing instance with wrong argument types or key function won't be coerced
        if args or key is not None:
            python_schema = core_schema.union_schema([from_set_schema, from_iterable_schema])
        else:
            python_schema = core_schema.union_schema(
                [instance_schema, from_set_schema, from_iterable_schema]
            )

        # Serializer that converts an instance to a list, using the schema for the item type to
        # serialize the items
        as_list_serializer = core_schema.plain_serializer_function_ser_schema(
            list, return_schema=list_t_schema
        )

        return core_schema.json_or_python_schema(
            json_schema=from_set_schema,
            python_schema=python_schema,
            serialization=as_list_serializer,
        )


class SortedSet(sortedcontainers.SortedSet[_HashableT], SortedSetPydanticAnnotation):
    pass


AnnotatedSortedSet = Annotated[sortedcontainers.SortedSet[_HashableT], SortedSetPydanticAnnotation]


@dataclass(frozen=True)
class Key:
    key: Callable[[Any], "SupportsRichComparison"]

    def __get_pydantic_core_schema__(
        self, source_type: Any, handler: GetCoreSchemaHandler
    ) -> core_schema.CoreSchema:
        if get_origin(source_type) is Annotated and isinstance(
            get_args(source_type)[-1], _KeyMarker
        ):
            # A Key further out applies to the same container
            return handler(source_type)
        try:
            constructor = _get_constructor(source_type)
        except _UnsupportedSourceTypeError as e:
            msg = (
                "Expected subclass of a sortedcontainers or sortedcontainers_pydantic class, "
                f"got '{e.parsed}' parsed from annotation '{source_type}'."
            )
            raise UnsupportedSourceTypeError(msg) from e
        keyed_constructor = _with_key(constructor, self.key)

        def ensure_keyed(value: Any) -> Any:
            # The container is built with the key function unless an annotation before Key
            # replaced it
            if isinstance(value, constructor) and value.key is self.key:
                return value
            return keyed_constructor(value)

        return core_schema.no_info_after_validator_function(
            function=ensure_keyed, schema=handler(Annotated[source_type, _KeyMarker(self.key)])
        )
