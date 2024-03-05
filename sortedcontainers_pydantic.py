from collections.abc import Mapping
from typing import TYPE_CHECKING, Any, Iterable, Tuple

from pydantic import (
    GetCoreSchemaHandler,
    GetJsonSchemaHandler,
)
from pydantic.json_schema import JsonSchemaValue
from pydantic_core import core_schema
import sortedcontainers

if TYPE_CHECKING:
    from sortedcontainers.sorteddict import _VT, _OrderT  # pragma: no cover

__version__ = "1.0.0"


class SortedDict(sortedcontainers.SortedDict):
    @classmethod
    def __get_pydantic_core_schema__(
        cls,
        _source_type: Any,
        _handler: GetCoreSchemaHandler,
    ) -> core_schema.CoreSchema:
        """
        Returns pydantic_core.CoreSchema that defines how Pydantic should validate or
        serialize this class.

        - Validating from JSON: Parse as a dict and then pass to SortedDict constructor
        - Validating from Python:
            - If it's already a SortedDict, do nothing
            - If it can be parsed as a dict, do so and then pass to SortedDict
              constructor
            - If it can be parsed as a list of two-tuples, do so and then pass to
              SortedDict constructor
        - Serialization: Convert to a dict
        """

        def validate_from_mapping(value: Mapping) -> SortedDict:
            return SortedDict(value)

        from_mapping_schema = core_schema.chain_schema(
            [
                core_schema.dict_schema(),
                core_schema.no_info_plain_validator_function(validate_from_mapping),
            ]
        )

        def validate_from_iterable_of_pairs(
            value: Iterable[Tuple["_OrderT", "_VT"]],
        ) -> SortedDict:
            return SortedDict(value)

        from_iterable_of_pairs_schema = core_schema.chain_schema(
            [
                core_schema.list_schema(
                    items_schema=core_schema.tuple_schema(
                        [core_schema.any_schema(), core_schema.any_schema()],
                    )
                ),
                core_schema.no_info_plain_validator_function(validate_from_iterable_of_pairs),
            ]
        )

        return core_schema.json_or_python_schema(
            json_schema=from_mapping_schema,
            python_schema=core_schema.union_schema(
                [
                    # check if it's an instance first before doing any further work
                    core_schema.is_instance_schema(SortedDict),
                    from_mapping_schema,
                    from_iterable_of_pairs_schema,
                ]
            ),
            serialization=core_schema.plain_serializer_function_ser_schema(
                lambda instance: dict(instance)
            ),
        )

    @classmethod
    def __get_pydantic_json_schema__(
        cls, _core_schema: core_schema.CoreSchema, handler: GetJsonSchemaHandler
    ) -> JsonSchemaValue:
        """Returns the JSON schema for this class. Uses the same schema as a normal
        dict.
        """
        return handler(core_schema.dict_schema())


class SortedList(sortedcontainers.SortedList):
    @classmethod
    def __get_pydantic_core_schema__(
        cls,
        _source_type: Any,
        _handler: GetCoreSchemaHandler,
    ) -> core_schema.CoreSchema:
        """
        Returns pydantic_core.CoreSchema that defines how Pydantic should validate or
        serialize this class.

        - Validating from JSON: Parse as a list and then pass to SortedList constructor
        - Validating from Python:
            - If it's already a SortedList, do nothing
            - If it can be parsed as a list, do so and then pass to SortedList
              constructor
        - Serialization: Convert to a list
        """

        def validate_from_iterable(value: Iterable) -> SortedList:
            return SortedList(value)

        from_iterable_schema = core_schema.chain_schema(
            [
                core_schema.list_schema(),
                core_schema.no_info_plain_validator_function(validate_from_iterable),
            ]
        )

        return core_schema.json_or_python_schema(
            json_schema=from_iterable_schema,
            python_schema=core_schema.union_schema(
                [
                    # check if it's an instance first before doing any further work
                    core_schema.is_instance_schema(SortedList),
                    from_iterable_schema,
                ]
            ),
            serialization=core_schema.plain_serializer_function_ser_schema(
                lambda instance: list(instance)
            ),
        )

    @classmethod
    def __get_pydantic_json_schema__(
        cls, _core_schema: core_schema.CoreSchema, handler: GetJsonSchemaHandler
    ) -> JsonSchemaValue:
        """Returns the JSON schema for this class. Uses the same schema as a normal
        list.
        """
        return handler(core_schema.list_schema())


class SortedSet(sortedcontainers.SortedSet):
    @classmethod
    def __get_pydantic_core_schema__(
        cls,
        _source_type: Any,
        _handler: GetCoreSchemaHandler,
    ) -> core_schema.CoreSchema:
        """
        Returns pydantic_core.CoreSchema that defines how Pydantic should validate or
        serialize this class.

        - Validating from JSON: Parse as a set and then pass to SortedSet constructor
        - Validating from Python:
            - If it's already a SortedSet, do nothing
            - If it can be parsed as a set, do so and then pass to SortedSet constructor
        - Serialization: Convert to a set
        """

        def validate_from_iterable(value: Iterable) -> SortedSet:
            return SortedSet(value)

        from_iterable_schema = core_schema.chain_schema(
            [
                core_schema.set_schema(),
                core_schema.no_info_plain_validator_function(validate_from_iterable),
            ]
        )

        return core_schema.json_or_python_schema(
            json_schema=from_iterable_schema,
            python_schema=core_schema.union_schema(
                [
                    # check if it's an instance first before doing any further work
                    core_schema.is_instance_schema(SortedSet),
                    from_iterable_schema,
                ]
            ),
            serialization=core_schema.plain_serializer_function_ser_schema(
                lambda instance: set(instance)
            ),
        )

    @classmethod
    def __get_pydantic_json_schema__(
        cls, _core_schema: core_schema.CoreSchema, handler: GetJsonSchemaHandler
    ) -> JsonSchemaValue:
        """Returns the JSON schema for this class. Uses the same schema as a normal
        set.
        """
        return handler(core_schema.set_schema())
