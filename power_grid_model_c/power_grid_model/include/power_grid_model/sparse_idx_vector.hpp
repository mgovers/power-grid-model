// SPDX-FileCopyrightText: 2022 Contributors to the Power Grid Model project <dynamic.grid.calculation@alliander.com>
//
// SPDX-License-Identifier: MPL-2.0

#pragma once
#ifndef POWER_GRID_MODEL_SPARSE_IDX_VECTOR_HPP
#define POWER_GRID_MODEL_SPARSE_IDX_VECTOR_HPP

#include "power_grid_model.hpp"

#include <boost/iterator/iterator_facade.hpp>
#include <boost/range.hpp>
#include <boost/range/counting_range.hpp>

/*
A data-structure for iterating through the indptr, ie. sparse representation of data.
Indptr can be eg: [0, 3, 6, 7]
This means that:
objects 0, 1, 2 are coupled to index 0
objects 3, 4, 5 are coupled to index 1
objects 6 is coupled to index 2

Another intuitive way to look at this for python developers is like list of lists: [[0, 1, 2], [3, 4, 5], [6]].

DenseIdxVector is a vector of element to group. ie. [0, 1, 1, 4] would denote that [[0], [1, 2], [], [], [3]]
The input, ie. [0, 1, 3] should be strictly increasing

*/

namespace power_grid_model::detail {

class SparseIdxVector {
  public:
    explicit SparseIdxVector(IdxVector indptr) : indptr_(indptr) {}

    auto get_element_range(Idx group) { return boost::iterator_range<IdxCount>(indptr_[group], indptr_[group + 1]); }

    Idx get_group(Idx element) {
        return static_cast<Idx>(std::upper_bound(indptr_.begin(), indptr_.end(), element) - indptr_.begin());
    }

  private:
    IdxVector indptr_;
};

class DenseIdxVector {
  public:
    explicit DenseIdxVector(IdxVector dense_idx_vector) : dense_idx_vector_(dense_idx_vector) {}

    auto get_group(Idx element) { return dense_idx_vector_[element]; }

    auto get_element_range(Idx group) {
        auto dense_begin = dense_idx_vector_.begin();
        auto dense_end = dense_idx_vector_.end();
        auto range_pair = std::equal_range(dense_begin, dense_end, group);
        return boost::iterator_range<IdxCount>(range_pair.first - dense_begin, range_pair.second - dense_begin);
    }

  private:
    IdxVector dense_idx_vector_;
};

// template<class ...T>
// requires(same_as<T, SparseIdxVector>...)
// auto iter_element_groups(T const& v1...)

// for (auto cosnt [bus, group_1_range, group_2_range]: iter_element_groups(v1, v2)) {
//   // do something with bus
//   for (auto const source: group_1_range) {
//     // sowething source
//   }
//   for (auto const load: group_2_range) {
//     // something load
//   }
// }

} // namespace power_grid_model::detail

#endif
