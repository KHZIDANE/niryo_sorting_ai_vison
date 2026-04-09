// generated from rosidl_generator_c/resource/idl__functions.c.em
// with input from niryo_interfaces:msg/Detection.idl
// generated code does not contain a copyright notice
#include "niryo_interfaces/msg/detail/detection__functions.h"

#include <assert.h>
#include <stdbool.h>
#include <stdlib.h>
#include <string.h>

#include "rcutils/allocator.h"


// Include directives for member types
// Member `color`
// Member `label`
#include "rosidl_runtime_c/string_functions.h"

bool
niryo_interfaces__msg__Detection__init(niryo_interfaces__msg__Detection * msg)
{
  if (!msg) {
    return false;
  }
  // x
  // y
  // z
  // color
  if (!rosidl_runtime_c__String__init(&msg->color)) {
    niryo_interfaces__msg__Detection__fini(msg);
    return false;
  }
  // label
  if (!rosidl_runtime_c__String__init(&msg->label)) {
    niryo_interfaces__msg__Detection__fini(msg);
    return false;
  }
  // confidence
  return true;
}

void
niryo_interfaces__msg__Detection__fini(niryo_interfaces__msg__Detection * msg)
{
  if (!msg) {
    return;
  }
  // x
  // y
  // z
  // color
  rosidl_runtime_c__String__fini(&msg->color);
  // label
  rosidl_runtime_c__String__fini(&msg->label);
  // confidence
}

bool
niryo_interfaces__msg__Detection__are_equal(const niryo_interfaces__msg__Detection * lhs, const niryo_interfaces__msg__Detection * rhs)
{
  if (!lhs || !rhs) {
    return false;
  }
  // x
  if (lhs->x != rhs->x) {
    return false;
  }
  // y
  if (lhs->y != rhs->y) {
    return false;
  }
  // z
  if (lhs->z != rhs->z) {
    return false;
  }
  // color
  if (!rosidl_runtime_c__String__are_equal(
      &(lhs->color), &(rhs->color)))
  {
    return false;
  }
  // label
  if (!rosidl_runtime_c__String__are_equal(
      &(lhs->label), &(rhs->label)))
  {
    return false;
  }
  // confidence
  if (lhs->confidence != rhs->confidence) {
    return false;
  }
  return true;
}

bool
niryo_interfaces__msg__Detection__copy(
  const niryo_interfaces__msg__Detection * input,
  niryo_interfaces__msg__Detection * output)
{
  if (!input || !output) {
    return false;
  }
  // x
  output->x = input->x;
  // y
  output->y = input->y;
  // z
  output->z = input->z;
  // color
  if (!rosidl_runtime_c__String__copy(
      &(input->color), &(output->color)))
  {
    return false;
  }
  // label
  if (!rosidl_runtime_c__String__copy(
      &(input->label), &(output->label)))
  {
    return false;
  }
  // confidence
  output->confidence = input->confidence;
  return true;
}

niryo_interfaces__msg__Detection *
niryo_interfaces__msg__Detection__create(void)
{
  rcutils_allocator_t allocator = rcutils_get_default_allocator();
  niryo_interfaces__msg__Detection * msg = (niryo_interfaces__msg__Detection *)allocator.allocate(sizeof(niryo_interfaces__msg__Detection), allocator.state);
  if (!msg) {
    return NULL;
  }
  memset(msg, 0, sizeof(niryo_interfaces__msg__Detection));
  bool success = niryo_interfaces__msg__Detection__init(msg);
  if (!success) {
    allocator.deallocate(msg, allocator.state);
    return NULL;
  }
  return msg;
}

void
niryo_interfaces__msg__Detection__destroy(niryo_interfaces__msg__Detection * msg)
{
  rcutils_allocator_t allocator = rcutils_get_default_allocator();
  if (msg) {
    niryo_interfaces__msg__Detection__fini(msg);
  }
  allocator.deallocate(msg, allocator.state);
}


bool
niryo_interfaces__msg__Detection__Sequence__init(niryo_interfaces__msg__Detection__Sequence * array, size_t size)
{
  if (!array) {
    return false;
  }
  rcutils_allocator_t allocator = rcutils_get_default_allocator();
  niryo_interfaces__msg__Detection * data = NULL;

  if (size) {
    data = (niryo_interfaces__msg__Detection *)allocator.zero_allocate(size, sizeof(niryo_interfaces__msg__Detection), allocator.state);
    if (!data) {
      return false;
    }
    // initialize all array elements
    size_t i;
    for (i = 0; i < size; ++i) {
      bool success = niryo_interfaces__msg__Detection__init(&data[i]);
      if (!success) {
        break;
      }
    }
    if (i < size) {
      // if initialization failed finalize the already initialized array elements
      for (; i > 0; --i) {
        niryo_interfaces__msg__Detection__fini(&data[i - 1]);
      }
      allocator.deallocate(data, allocator.state);
      return false;
    }
  }
  array->data = data;
  array->size = size;
  array->capacity = size;
  return true;
}

void
niryo_interfaces__msg__Detection__Sequence__fini(niryo_interfaces__msg__Detection__Sequence * array)
{
  if (!array) {
    return;
  }
  rcutils_allocator_t allocator = rcutils_get_default_allocator();

  if (array->data) {
    // ensure that data and capacity values are consistent
    assert(array->capacity > 0);
    // finalize all array elements
    for (size_t i = 0; i < array->capacity; ++i) {
      niryo_interfaces__msg__Detection__fini(&array->data[i]);
    }
    allocator.deallocate(array->data, allocator.state);
    array->data = NULL;
    array->size = 0;
    array->capacity = 0;
  } else {
    // ensure that data, size, and capacity values are consistent
    assert(0 == array->size);
    assert(0 == array->capacity);
  }
}

niryo_interfaces__msg__Detection__Sequence *
niryo_interfaces__msg__Detection__Sequence__create(size_t size)
{
  rcutils_allocator_t allocator = rcutils_get_default_allocator();
  niryo_interfaces__msg__Detection__Sequence * array = (niryo_interfaces__msg__Detection__Sequence *)allocator.allocate(sizeof(niryo_interfaces__msg__Detection__Sequence), allocator.state);
  if (!array) {
    return NULL;
  }
  bool success = niryo_interfaces__msg__Detection__Sequence__init(array, size);
  if (!success) {
    allocator.deallocate(array, allocator.state);
    return NULL;
  }
  return array;
}

void
niryo_interfaces__msg__Detection__Sequence__destroy(niryo_interfaces__msg__Detection__Sequence * array)
{
  rcutils_allocator_t allocator = rcutils_get_default_allocator();
  if (array) {
    niryo_interfaces__msg__Detection__Sequence__fini(array);
  }
  allocator.deallocate(array, allocator.state);
}

bool
niryo_interfaces__msg__Detection__Sequence__are_equal(const niryo_interfaces__msg__Detection__Sequence * lhs, const niryo_interfaces__msg__Detection__Sequence * rhs)
{
  if (!lhs || !rhs) {
    return false;
  }
  if (lhs->size != rhs->size) {
    return false;
  }
  for (size_t i = 0; i < lhs->size; ++i) {
    if (!niryo_interfaces__msg__Detection__are_equal(&(lhs->data[i]), &(rhs->data[i]))) {
      return false;
    }
  }
  return true;
}

bool
niryo_interfaces__msg__Detection__Sequence__copy(
  const niryo_interfaces__msg__Detection__Sequence * input,
  niryo_interfaces__msg__Detection__Sequence * output)
{
  if (!input || !output) {
    return false;
  }
  if (output->capacity < input->size) {
    const size_t allocation_size =
      input->size * sizeof(niryo_interfaces__msg__Detection);
    rcutils_allocator_t allocator = rcutils_get_default_allocator();
    niryo_interfaces__msg__Detection * data =
      (niryo_interfaces__msg__Detection *)allocator.reallocate(
      output->data, allocation_size, allocator.state);
    if (!data) {
      return false;
    }
    // If reallocation succeeded, memory may or may not have been moved
    // to fulfill the allocation request, invalidating output->data.
    output->data = data;
    for (size_t i = output->capacity; i < input->size; ++i) {
      if (!niryo_interfaces__msg__Detection__init(&output->data[i])) {
        // If initialization of any new item fails, roll back
        // all previously initialized items. Existing items
        // in output are to be left unmodified.
        for (; i-- > output->capacity; ) {
          niryo_interfaces__msg__Detection__fini(&output->data[i]);
        }
        return false;
      }
    }
    output->capacity = input->size;
  }
  output->size = input->size;
  for (size_t i = 0; i < input->size; ++i) {
    if (!niryo_interfaces__msg__Detection__copy(
        &(input->data[i]), &(output->data[i])))
    {
      return false;
    }
  }
  return true;
}
