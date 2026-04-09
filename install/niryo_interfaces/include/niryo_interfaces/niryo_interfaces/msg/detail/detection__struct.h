// NOLINT: This file starts with a BOM since it contain non-ASCII characters
// generated from rosidl_generator_c/resource/idl__struct.h.em
// with input from niryo_interfaces:msg/Detection.idl
// generated code does not contain a copyright notice

// IWYU pragma: private, include "niryo_interfaces/msg/detection.h"


#ifndef NIRYO_INTERFACES__MSG__DETAIL__DETECTION__STRUCT_H_
#define NIRYO_INTERFACES__MSG__DETAIL__DETECTION__STRUCT_H_

#ifdef __cplusplus
extern "C"
{
#endif

#include <stdbool.h>
#include <stddef.h>
#include <stdint.h>

// Constants defined in the message

// Include directives for member types
// Member 'color'
// Member 'label'
#include "rosidl_runtime_c/string.h"

/// Struct defined in msg/Detection in the package niryo_interfaces.
/**
  * Detected object from vision node
 */
typedef struct niryo_interfaces__msg__Detection
{
  /// world-frame X (metres)
  double x;
  /// world-frame Y (metres)
  double y;
  /// world-frame Z (metres, table surface)
  double z;
  /// "blue" | "orange"
  rosidl_runtime_c__String color;
  /// "good" | "defective"
  rosidl_runtime_c__String label;
  /// 0.0–1.0
  double confidence;
} niryo_interfaces__msg__Detection;

// Struct for a sequence of niryo_interfaces__msg__Detection.
typedef struct niryo_interfaces__msg__Detection__Sequence
{
  niryo_interfaces__msg__Detection * data;
  /// The number of valid items in data
  size_t size;
  /// The number of allocated items in data
  size_t capacity;
} niryo_interfaces__msg__Detection__Sequence;

#ifdef __cplusplus
}
#endif

#endif  // NIRYO_INTERFACES__MSG__DETAIL__DETECTION__STRUCT_H_
