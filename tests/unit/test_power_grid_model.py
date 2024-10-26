# SPDX-FileCopyrightText: Contributors to the Power Grid Model project <powergridmodel@lfenergy.org>
#
# SPDX-License-Identifier: MPL-2.0

from copy import copy

import numpy as np
import pytest

from power_grid_model import (
    ComponentAttributeFilterOptions,
    ComponentType,
    DatasetType,
    PowerGridModel,
    initialize_array,
    power_grid_meta_data,
)
from power_grid_model._utils import compatibility_convert_row_columnar_dataset
from power_grid_model.errors import InvalidCalculationMethod, IterationDiverge, PowerGridBatchError, PowerGridError
from power_grid_model.utils import get_dataset_scenario, json_serialize_to_file
from power_grid_model.validation import assert_valid_input_data

from .utils import compare_result

"""
Testing network

source_1(1.0 p.u., 100.0 V) --internal_impedance(j10.0 ohm, sk=1000.0 VA, rx_ratio=0.0)--
-- node_0 (100.0 V) --load_2(const_i, -j5.0A, 0.0 W, 500.0 var)

u0 = 100.0 V - (j10.0 ohm * -j5.0 A) = 50.0 V

update_0:
    u_ref = 0.5 p.u. (50.0 V)
    q_specified = 100 var (-j1.0A)
u0 = 50.0 V - (j10.0 ohm * -j1.0 A) = 40.0 V

update_1:
    q_specified = 300 var (-j3.0A)
u0 = 100.0 V - (j10.0 ohm * -j3.0 A) = 70.0 V
"""


@pytest.fixture
def input_row():
    node = initialize_array(DatasetType.input, ComponentType.node, 1)
    node["id"] = 0
    node["u_rated"] = 100.0

    source = initialize_array(DatasetType.input, ComponentType.source, 1)
    source["id"] = 1
    source["node"] = 0
    source["status"] = 1
    source["u_ref"] = 1.0
    source["sk"] = 1000.0
    source["rx_ratio"] = 0.0

    sym_load = initialize_array(DatasetType.input, ComponentType.sym_load, 1)
    sym_load["id"] = 2
    sym_load["node"] = 0
    sym_load["status"] = 1
    sym_load["type"] = 2
    sym_load["p_specified"] = 0.0
    sym_load["q_specified"] = 500.0

    return {
        ComponentType.node: node,
        ComponentType.source: source,
        ComponentType.sym_load: sym_load,
    }


@pytest.fixture
def input_col_cpp():
    node = initialize_array(DatasetType.input, ComponentType.node, 2)
    node["id"] = [0, 4]
    node["u_rated"] = [100.0, 100.0]

    source = initialize_array(DatasetType.input, ComponentType.source, 1)
    source["id"] = 1
    source["node"] = 0
    source["status"] = 1
    source["u_ref"] = 1.0
    source["sk"] = 1000.0
    source["rx_ratio"] = 0.0

    sym_load = initialize_array(DatasetType.input, ComponentType.sym_load, 1)
    sym_load["id"] = 2
    sym_load["node"] = 0
    sym_load["status"] = 1
    sym_load["type"] = 2
    sym_load["p_specified"] = 0.0
    sym_load["q_specified"] = 500.0

    line = {}
    line["id"] = np.array([5, 6], dtype=power_grid_meta_data[DatasetType.input][ComponentType.line].dtype["id"])
    line["from_node"] = np.array(
        [0, 4], dtype=power_grid_meta_data[DatasetType.input][ComponentType.line].dtype["from_node"]
    )
    line["to_node"] = np.array(
        [4, 0], dtype=power_grid_meta_data[DatasetType.input][ComponentType.line].dtype["to_node"]
    )
    line["from_status"] = np.array(
        [0, 1], dtype=power_grid_meta_data[DatasetType.input][ComponentType.line].dtype["from_status"]
    )
    line["to_status"] = np.array(
        [1, 0], dtype=power_grid_meta_data[DatasetType.input][ComponentType.line].dtype["to_status"]
    )

    return {
        ComponentType.node: node,
        ComponentType.source: source,
        ComponentType.sym_load: sym_load,
        ComponentType.line: line,
    }


@pytest.fixture
def update_col_cpp():
    node = initialize_array(DatasetType.input, ComponentType.node, 2)
    node["id"] = [0, 4]
    node["u_rated"] = [100.0, 100.0]

    source = initialize_array(DatasetType.input, ComponentType.source, 1)
    source["id"] = 1
    source["node"] = 0
    source["status"] = 1
    source["u_ref"] = 0.5
    source["sk"] = 1000.0
    source["rx_ratio"] = 0.0

    sym_load = initialize_array(DatasetType.input, ComponentType.sym_load, 2)
    sym_load["id"] = [2, 2]
    sym_load["node"] = 0
    sym_load["status"] = 1
    sym_load["type"] = 2
    sym_load["p_specified"] = 0.0
    sym_load["q_specified"] = [100.0, 300]

    batch_line = {}
    batch_line["id"] = np.array(
        [[5, 6], [5, 6]], dtype=power_grid_meta_data[DatasetType.input][ComponentType.line].dtype["id"]
    )
    batch_line["from_node"] = np.array(
        [[0, 4], [0, 4]], dtype=power_grid_meta_data[DatasetType.input][ComponentType.line].dtype["from_node"]
    )
    batch_line["to_node"] = np.array(
        [[4, 0], [4, 0]], dtype=power_grid_meta_data[DatasetType.input][ComponentType.line].dtype["to_node"]
    )
    batch_line["from_status"] = np.array(
        [[0, 1], [0, 1]], dtype=power_grid_meta_data[DatasetType.input][ComponentType.line].dtype["from_status"]
    )
    batch_line["to_status"] = np.array(
        [[1, 0], [1, 0]], dtype=power_grid_meta_data[DatasetType.input][ComponentType.line].dtype["to_status"]
    )

    return {
        ComponentType.source: {
            "data": source,
            "indptr": np.array([0, 1, 1]),
        },
        ComponentType.sym_load: sym_load,
        ComponentType.line: batch_line,
    }


@pytest.fixture
def bad_update_col_cpp():
    node = initialize_array(DatasetType.input, ComponentType.node, 2)
    node["id"] = [0, 4]
    node["u_rated"] = [100.0, 100.0]

    source = initialize_array(DatasetType.input, ComponentType.source, 1)
    source["id"] = 1
    source["node"] = 0
    source["status"] = 1
    source["u_ref"] = 0.5
    source["sk"] = 1000.0
    source["rx_ratio"] = 0.0

    sym_load = initialize_array(DatasetType.input, ComponentType.sym_load, 2)
    sym_load["id"] = [2, 2]
    sym_load["node"] = 0
    sym_load["status"] = 1
    sym_load["type"] = 2
    sym_load["p_specified"] = 0.0
    sym_load["q_specified"] = [100.0, 300]

    batch_line = {}
    batch_line["id"] = np.array(
        [[99, 999], [99, 999]], dtype=power_grid_meta_data[DatasetType.input][ComponentType.line].dtype["id"]
    )
    batch_line["from_node"] = np.array(
        [[0, 4], [0, 4]], dtype=power_grid_meta_data[DatasetType.input][ComponentType.line].dtype["from_node"]
    )
    batch_line["to_node"] = np.array(
        [[4, 0], [4, 0]], dtype=power_grid_meta_data[DatasetType.input][ComponentType.line].dtype["to_node"]
    )
    batch_line["from_status"] = np.array(
        [[0, 1], [0, 1]], dtype=power_grid_meta_data[DatasetType.input][ComponentType.line].dtype["from_status"]
    )
    batch_line["to_status"] = np.array(
        [[1, 0], [1, 0]], dtype=power_grid_meta_data[DatasetType.input][ComponentType.line].dtype["to_status"]
    )

    return {
        ComponentType.source: {
            "data": source,
            "indptr": np.array([0, 1, 1]),
        },
        ComponentType.sym_load: sym_load,
        ComponentType.line: batch_line,
    }


@pytest.fixture
def input_col(input_row):
    return compatibility_convert_row_columnar_dataset(
        input_row, ComponentAttributeFilterOptions.relevant, DatasetType.input
    )


@pytest.fixture(params=["input_row", "input_col"])
def input(request):
    return request.getfixturevalue(request.param)


@pytest.fixture
def sym_output():
    node = initialize_array(DatasetType.sym_output, ComponentType.node, 1)
    node["id"] = 0
    node["u"] = 50.0
    node["u_pu"] = 0.5
    node["u_angle"] = 0.0

    return {ComponentType.node: node}


@pytest.fixture
def update_batch_row():
    source = initialize_array(DatasetType.update, ComponentType.source, 1)
    source["id"] = 1
    source["u_ref"] = 0.5

    sym_load = initialize_array(DatasetType.update, ComponentType.sym_load, 2)
    sym_load["id"] = [2, 2]
    sym_load["q_specified"] = [100.0, 300.0]

    return {
        ComponentType.source: {
            "data": source,
            "indptr": np.array([0, 1, 1]),
        },
        ComponentType.sym_load: {
            "data": sym_load,
            "indptr": np.array([0, 1, 2]),
        },
    }


@pytest.fixture
def update_batch_col(update_batch_row):
    return compatibility_convert_row_columnar_dataset(
        update_batch_row, ComponentAttributeFilterOptions.relevant, DatasetType.update
    )


@pytest.fixture(params=["update_batch_row", "update_batch_col"])
def update_batch(request):
    return request.getfixturevalue(request.param)


@pytest.fixture
def sym_output_batch():
    node = initialize_array(DatasetType.sym_output, ComponentType.node, (2, 1))
    node["id"] = [[0], [0]]
    node["u"] = [[40.0], [70.0]]
    node["u_pu"] = [[0.4], [0.7]]
    node["u_angle"] = [[0.0], [0.0]]

    return {
        ComponentType.node: node,
    }


@pytest.fixture
def model(input):
    return PowerGridModel(input)


def test_simple_power_flow(model: PowerGridModel, sym_output):
    result = model.calculate_power_flow()
    compare_result(result, sym_output, rtol=0.0, atol=1e-8)


def test_simple_permanent_update(model: PowerGridModel, update_batch, sym_output_batch):
    model.update(update_data=get_dataset_scenario(update_batch, 0))  # single permanent model update
    result = model.calculate_power_flow()
    expected_result = get_dataset_scenario(sym_output_batch, 0)
    compare_result(result, expected_result, rtol=0.0, atol=1e-8)


def test_update_error(model: PowerGridModel):
    load_update = initialize_array(DatasetType.update, ComponentType.sym_load, 1)
    load_update["id"] = 5
    update_data = {ComponentType.sym_load: load_update}
    with pytest.raises(PowerGridError, match="The id cannot be found:"):
        model.update(update_data=update_data)
    update_data_col = compatibility_convert_row_columnar_dataset(
        update_data, ComponentAttributeFilterOptions.relevant, DatasetType.update
    )
    model.update(update_data=update_data_col)


def test_copy_model(model: PowerGridModel, sym_output):
    model_2 = copy(model)
    result = model_2.calculate_power_flow()
    compare_result(result, sym_output, rtol=0.0, atol=1e-8)


def test_get_indexer(model: PowerGridModel):
    ids = np.array([2, 2])
    expected_indexer = np.array([0, 0])
    indexer = model.get_indexer(ComponentType.sym_load, ids)
    np.testing.assert_allclose(expected_indexer, indexer)


def test_batch_power_flow(model: PowerGridModel, update_batch, sym_output_batch):
    result = model.calculate_power_flow(update_data=update_batch)
    compare_result(result, sym_output_batch, rtol=0.0, atol=1e-8)


def test_construction_error(input):
    input[ComponentType.sym_load]["id"][0] = 0
    with pytest.raises(PowerGridError, match="Conflicting id detected:"):
        PowerGridModel(input)


def test_single_calculation_error(model: PowerGridModel):
    with pytest.raises(IterationDiverge, match="Iteration failed to converge after"):
        model.calculate_power_flow(max_iterations=1, error_tolerance=1e-100)
    with pytest.raises(InvalidCalculationMethod, match="The calculation method is invalid for this calculation!"):
        model.calculate_state_estimation(calculation_method="iterative_current")

    for calculation_method in ("linear", "newton_raphson", "iterative_current", "linear_current", "iterative_linear"):
        with pytest.raises(InvalidCalculationMethod):
            model.calculate_short_circuit(calculation_method=calculation_method)


def test_debug(input_col_cpp, update_col_cpp, bad_update_col_cpp):
    model = PowerGridModel(input_col_cpp)
    # should raise no exception
    # model.calculate_power_flow(update_data=update_col_cpp)
    # should pass with exception expected
    with pytest.raises(PowerGridBatchError) as e:
        model.calculate_power_flow(update_data=bad_update_col_cpp)
    # with error
    error = e.value
    np.testing.assert_allclose(error.failed_scenarios, [1])
    np.testing.assert_allclose(error.succeeded_scenarios, [0])
    assert "The id cannot be found:" in error.error_messages[0]


def test_batch_calculation_error(model: PowerGridModel, update_batch, input):
    # wrong id
    update_batch[ComponentType.source]["data"]["id"][0] = 999
    with pytest.raises(PowerGridBatchError) as e:
        model.calculate_power_flow(update_data=update_batch)
    # with error
    error = e.value
    np.testing.assert_allclose(error.failed_scenarios, [1])
    np.testing.assert_allclose(error.succeeded_scenarios, [0])
    assert "The id cannot be found:" in error.error_messages[0]


def test_batch_calculation_error_continue(model: PowerGridModel, update_batch, sym_output_batch):
    # wrong id
    update_batch[ComponentType.sym_load]["data"]["id"][1] = 5
    result = model.calculate_power_flow(update_data=update_batch, continue_on_batch_error=True)
    # assert error
    error = model.batch_error
    assert error is not None
    np.testing.assert_allclose(error.failed_scenarios, [1])
    np.testing.assert_allclose(error.succeeded_scenarios, [0])
    assert "The id cannot be found:" in error.error_messages[0]
    # assert value result for scenario 0
    result = {ComponentType.node: result[ComponentType.node][error.succeeded_scenarios, :]}
    expected_result = {ComponentType.node: sym_output_batch[ComponentType.node][error.succeeded_scenarios, :]}
    compare_result(result, expected_result, rtol=0.0, atol=1e-8)
    # general error before the batch
    with pytest.raises(PowerGridError, match="The calculation method is invalid for this calculation!"):
        model.calculate_state_estimation(
            calculation_method="iterative_current",
            update_data={
                ComponentType.source: initialize_array(DatasetType.update, ComponentType.source, shape=(5, 0))
            },
            continue_on_batch_error=True,
        )


def test_empty_input():
    node = initialize_array(DatasetType.input, ComponentType.node, 0)
    line = initialize_array(DatasetType.input, ComponentType.line, 0)
    sym_load = initialize_array(DatasetType.input, ComponentType.sym_load, 0)
    source = initialize_array(DatasetType.input, ComponentType.source, 0)

    input_data = {
        ComponentType.node: node,
        ComponentType.line: line,
        ComponentType.sym_load: sym_load,
        ComponentType.source: source,
    }

    assert_valid_input_data(input_data)
    model = PowerGridModel(input_data, system_frequency=50.0)

    result = model.calculate_power_flow()

    assert result == {}
