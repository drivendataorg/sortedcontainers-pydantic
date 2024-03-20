from typing import (
    TYPE_CHECKING,
    Any,
    Generic,
    Hashable,
    Iterable,
    Mapping,
    Set,
    Tuple,
    TypeVar,
    get_args,
)

from pydantic import (
    GetCoreSchemaHandler,
)
from pydantic_core import core_schema
import sortedcontainers

__version__ = "1.0.0"

_KT = TypeVar("_KT", bound=Hashable)  # Key type.
_VT = TypeVar("_VT")  # Value type.
_T = TypeVar("_T")
_HashableT = TypeVar("_HashableT", bound=Hashable)

# sortedcontainers is not type annotated directed so we need this hack to declare the parent
# classes as generics for Python 3.8.
# https://mypy.readthedocs.io/en/stable/runtime_troubles.html#using-classes-that-are-generic-in-stubs-but-not-at-runtime
if TYPE_CHECKING:

    class _SortedDict(sortedcontainers.SortedDict[_KT, _VT]): ...

    class _SortedList(sortedcontainers.SortedList[_T]): ...

    class _SortedSet(sortedcontainers.SortedSet[_HashableT]): ...

else:

    class _SortedDict(Generic[_KT, _VT], sortedcontainers.SortedDict): ...

    class _SortedList(Generic[_T], sortedcontainers.SortedList): ...

    class _SortedSet(Generic[_HashableT], sortedcontainers.SortedSet): ...


class SortedDict(_SortedDict[_KT, _VT]):
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
        # Schema for when the input is already an instance of this class
        instance_schema = core_schema.is_instance_schema(cls)

        # Get schema for Iterable type based on source type has arguments
        args = get_args(source_type)
        if args:
            mapping_t_schema = handler.generate_schema(Mapping[args[0], args[1]])  # type: ignore
            iterable_of_pairs_t_schema = handler.generate_schema(Iterable[Tuple[args[0], args[1]]])  # type: ignore
        else:
            mapping_t_schema = handler.generate_schema(Mapping)
            iterable_of_pairs_t_schema = handler.generate_schema(Iterable[Tuple[Any, Any]])

        # Schema for when the input is a mapping
        from_mapping_schema = core_schema.no_info_after_validator_function(
            function=cls, schema=mapping_t_schema
        )

        # Schema for when the input is an iterable of pairs
        from_iterable_of_pairs_schema = core_schema.no_info_after_validator_function(
            function=cls, schema=iterable_of_pairs_t_schema
        )

        # Union of the two schemas
        python_schema = core_schema.union_schema(
            [
                instance_schema,
                from_mapping_schema,
                from_iterable_of_pairs_schema,
            ]
        )

        # Serializer that converts an instance to a dict
        as_dict_serializer = core_schema.plain_serializer_function_ser_schema(dict)

        return core_schema.json_or_python_schema(
            json_schema=from_mapping_schema,
            python_schema=python_schema,
            serialization=as_dict_serializer,
        )


class SortedList(_SortedList[_T]):
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
        # Schema for when the input is already an instance of this class
        instance_schema = core_schema.is_instance_schema(cls)

        # Get schema for Iterable type based on source type has arguments
        args = get_args(source_type)
        if args:
            iterable_t_schema = handler.generate_schema(Iterable[args[0]])  # type: ignore
        else:
            iterable_t_schema = handler.generate_schema(Iterable)

        # Schema for when the input is an iterable
        from_iterable_schema = core_schema.no_info_after_validator_function(
            function=cls, schema=iterable_t_schema
        )

        # Union of the two schemas
        python_schema = core_schema.union_schema(
            [
                instance_schema,
                from_iterable_schema,
            ]
        )

        # Serializer that converts an instance to a list
        as_list_serializer = core_schema.plain_serializer_function_ser_schema(list)

        return core_schema.json_or_python_schema(
            json_schema=from_iterable_schema,
            python_schema=python_schema,
            serialization=as_list_serializer,
        )


class SortedSet(_SortedSet[_HashableT]):
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
        # Schema for when the input is already an instance of this class
        instance_schema = core_schema.is_instance_schema(cls)

        # Get schema for Iterable type based on source type has arguments
        args = get_args(source_type)
        if args:
            set_t_schema = handler.generate_schema(Set[args[0]])  # type: ignore
            iterable_t_schema = handler.generate_schema(Iterable[args[0]])  # type: ignore
        else:
            set_t_schema = handler.generate_schema(Set)
            iterable_t_schema = handler.generate_schema(Iterable)

        # Schema for when the input is a set
        from_set_schema = core_schema.no_info_after_validator_function(
            function=cls, schema=set_t_schema
        )

        # Schema for when the input is an iterable
        from_iterable_schema = core_schema.no_info_after_validator_function(
            function=cls, schema=iterable_t_schema
        )

        # Union of the two schemas
        python_schema = core_schema.union_schema(
            [
                instance_schema,
                from_set_schema,
                from_iterable_schema,
            ]
        )

        # Serializer that converts an instance to a list
        as_list_serializer = core_schema.plain_serializer_function_ser_schema(list)

        return core_schema.json_or_python_schema(
            json_schema=from_set_schema,
            python_schema=python_schema,
            serialization=as_list_serializer,
        )
