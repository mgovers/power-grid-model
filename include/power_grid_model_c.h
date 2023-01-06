// SPDX-FileCopyrightText: 2022 Contributors to the Power Grid Model project <dynamic.grid.calculation@alliander.com>
//
// SPDX-License-Identifier: MPL-2.0

#pragma once
#ifndef POWER_GRID_MODEL_C_H
#define POWER_GRID_MODEL_C_H

// Generic helper definitions for shared library support
#if defined _WIN32
#define POWER_GRID_MODEL_HELPER_DLL_IMPORT __declspec(dllimport)
#define POWER_GRID_MODEL_HELPER_DLL_EXPORT __declspec(dllexport)
#define POWER_GRID_MODEL_HELPER_DLL_LOCAL
#else
#if __GNUC__ >= 4
#define POWER_GRID_MODEL_HELPER_DLL_IMPORT __attribute__((visibility("default")))
#define POWER_GRID_MODEL_HELPER_DLL_EXPORT __attribute__((visibility("default")))
#define POWER_GRID_MODEL_HELPER_DLL_LOCAL __attribute__((visibility("hidden")))
#else
#define POWER_GRID_MODEL_HELPER_DLL_IMPORT
#define POWER_GRID_MODEL_HELPER_DLL_EXPORT
#define POWER_GRID_MODEL_HELPER_DLL_LOCAL
#endif
#endif
// Now we use the generic helper definitions above to define POWER_GRID_MODEL_API and POWER_GRID_MODEL_LOCAL.
#ifdef POWER_GRID_MODEL_DLL_EXPORTS  // defined if we are building the POWER_GRID_MODEL DLL (instead of using it)
#define POWER_GRID_MODEL_API POWER_GRID_MODEL_HELPER_DLL_EXPORT
#else
#define POWER_GRID_MODEL_API POWER_GRID_MODEL_HELPER_DLL_IMPORT
#endif  // POWER_GRID_MODEL_DLL_EXPORTS
#define POWER_GRID_MODEL_LOCAL POWER_GRID_MODEL_HELPER_DLL_LOCAL

// integers
#include <stdint.h>

// C linkage
#ifdef __cplusplus
extern "C" {
#endif

#ifndef POWER_GRID_MODEL_DLL_EXPORTS
// else define opaque pointer
typedef struct POWER_GRID_MODEL_PowerGridModel POWER_GRID_MODEL_PowerGridModel;
// context handle
typedef struct POWER_GRID_MODEL_Handle POWER_GRID_MODEL_Handle;
// index type
typedef int64_t Idx;
#endif

// create and release handle
POWER_GRID_MODEL_API POWER_GRID_MODEL_Handle* POWER_GRID_MODEL_create_handle();
POWER_GRID_MODEL_API void POWER_GRID_MODEL_destroy_handle(POWER_GRID_MODEL_Handle* handle);

// get error code and error messsage
POWER_GRID_MODEL_API POWER_GRID_MODEL_Idx POWER_GRID_MODEL_err_code(POWER_GRID_MODEL_Handle const* handle);
POWER_GRID_MODEL_API char const* POWER_GRID_MODEL_err_msg(POWER_GRID_MODEL_Handle const* handle);

// retrieve meta data
POWER_GRID_MODEL_API POWER_GRID_MODEL_Idx POWER_GRID_MODEL_meta_dataset_types(POWER_GRID_MODEL_Handle const* handle,
                                                                              char const*** dataset_types);
POWER_GRID_MODEL_API POWER_GRID_MODEL_Idx POWER_GRID_MODEL_meta_data_classes(POWER_GRID_MODEL_Handle const* handle,
                                                                             char const* dataset_type,
                                                                             char const*** data_classes,
                                                                             size_t const** sizes,
                                                                             size_t const** alignments);
POWER_GRID_MODEL_API POWER_GRID_MODEL_Idx POWER_GRID_MODEL_meta_attributes(
    POWER_GRID_MODEL_Handle const* handle, char const* dataset_type, char const* data_class, char const*** attributes,
    char const*** c_types, size_t const** offsets);

#ifdef __cplusplus
}
#endif

#endif  // POWER_GRID_MODEL_C_H