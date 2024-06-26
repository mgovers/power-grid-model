# SPDX-FileCopyrightText: Contributors to the Power Grid Model project <powergridmodel@lfenergy.org>
#
# SPDX-License-Identifier: MPL-2.0

"""Data types for power grid model dataset and component types."""

# This file is automatically generated. DO NOT modify it manually!


from enum import Enum
from typing import Any, Dict, Mapping

# pylint: disable=invalid-name


class DataType(str, Enum):
    """
    A DataType is the type of a :class:`Dataset` in power grid model.

    - Examples:

        - DataType.input = "input"
        - DataType.update = "update"
    """

    input = "input"
    sym_output = "sym_output"
    asym_output = "asym_output"
    update = "update"
    sc_output = "sc_output"


class ComponentType(str, Enum):
    """
    A ComponentType is the type of a grid component.

    - Examples:

        - ComponentType.node = "node"
        - ComponentType.line = "line"
    """

    node = "node"
    line = "line"
    link = "link"
    transformer = "transformer"
    transformer_tap_regulator = "transformer_tap_regulator"
    three_winding_transformer = "three_winding_transformer"
    sym_load = "sym_load"
    sym_gen = "sym_gen"
    asym_load = "asym_load"
    asym_gen = "asym_gen"
    shunt = "shunt"
    source = "source"
    sym_voltage_sensor = "sym_voltage_sensor"
    asym_voltage_sensor = "asym_voltage_sensor"
    sym_power_sensor = "sym_power_sensor"
    asym_power_sensor = "asym_power_sensor"
    fault = "fault"


# pylint: enable=invalid-name


def _str_to_datatype(data_type: Any) -> DataType:
    """Helper function to transform data_type str to DataType."""
    if isinstance(data_type, str):
        return DataType[data_type]
    return data_type


def _map_to_datatypes(data: Mapping[Any, Any]) -> Dict[DataType, Any]:
    """Helper function to map datatype str keys to DataType."""
    return {_str_to_datatype(key): value for key, value in data.items()}


def _str_to_componenttype(component: Any) -> ComponentType:
    """Helper function to transform component str to ComponentType."""
    if isinstance(component, str):
        return ComponentType[component]
    return component


def _map_to_componenttypes(data: Mapping[Any, Any]) -> Dict[ComponentType, Any]:
    """Helper function to map componenttype str keys to ComponentType."""
    return {_str_to_componenttype(key): value for key, value in data.items()}
