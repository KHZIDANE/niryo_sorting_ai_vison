// generated from rosidl_generator_c/resource/idl__description.c.em
// with input from niryo_interfaces:msg/Detection.idl
// generated code does not contain a copyright notice

#include "niryo_interfaces/msg/detail/detection__functions.h"

ROSIDL_GENERATOR_C_PUBLIC_niryo_interfaces
const rosidl_type_hash_t *
niryo_interfaces__msg__Detection__get_type_hash(
  const rosidl_message_type_support_t * type_support)
{
  (void)type_support;
  static rosidl_type_hash_t hash = {1, {
      0xd7, 0x2f, 0xec, 0x39, 0xee, 0xb0, 0xae, 0x64,
      0x33, 0xf5, 0x0f, 0xba, 0xbe, 0x78, 0x89, 0x95,
      0x8b, 0x89, 0x7a, 0x48, 0x40, 0x55, 0x24, 0xca,
      0x54, 0x79, 0xb0, 0x02, 0xc6, 0xad, 0xe8, 0xc9,
    }};
  return &hash;
}

#include <assert.h>
#include <string.h>

// Include directives for referenced types

// Hashes for external referenced types
#ifndef NDEBUG
#endif

static char niryo_interfaces__msg__Detection__TYPE_NAME[] = "niryo_interfaces/msg/Detection";

// Define type names, field names, and default values
static char niryo_interfaces__msg__Detection__FIELD_NAME__x[] = "x";
static char niryo_interfaces__msg__Detection__FIELD_NAME__y[] = "y";
static char niryo_interfaces__msg__Detection__FIELD_NAME__z[] = "z";
static char niryo_interfaces__msg__Detection__FIELD_NAME__color[] = "color";
static char niryo_interfaces__msg__Detection__FIELD_NAME__label[] = "label";
static char niryo_interfaces__msg__Detection__FIELD_NAME__confidence[] = "confidence";

static rosidl_runtime_c__type_description__Field niryo_interfaces__msg__Detection__FIELDS[] = {
  {
    {niryo_interfaces__msg__Detection__FIELD_NAME__x, 1, 1},
    {
      rosidl_runtime_c__type_description__FieldType__FIELD_TYPE_DOUBLE,
      0,
      0,
      {NULL, 0, 0},
    },
    {NULL, 0, 0},
  },
  {
    {niryo_interfaces__msg__Detection__FIELD_NAME__y, 1, 1},
    {
      rosidl_runtime_c__type_description__FieldType__FIELD_TYPE_DOUBLE,
      0,
      0,
      {NULL, 0, 0},
    },
    {NULL, 0, 0},
  },
  {
    {niryo_interfaces__msg__Detection__FIELD_NAME__z, 1, 1},
    {
      rosidl_runtime_c__type_description__FieldType__FIELD_TYPE_DOUBLE,
      0,
      0,
      {NULL, 0, 0},
    },
    {NULL, 0, 0},
  },
  {
    {niryo_interfaces__msg__Detection__FIELD_NAME__color, 5, 5},
    {
      rosidl_runtime_c__type_description__FieldType__FIELD_TYPE_STRING,
      0,
      0,
      {NULL, 0, 0},
    },
    {NULL, 0, 0},
  },
  {
    {niryo_interfaces__msg__Detection__FIELD_NAME__label, 5, 5},
    {
      rosidl_runtime_c__type_description__FieldType__FIELD_TYPE_STRING,
      0,
      0,
      {NULL, 0, 0},
    },
    {NULL, 0, 0},
  },
  {
    {niryo_interfaces__msg__Detection__FIELD_NAME__confidence, 10, 10},
    {
      rosidl_runtime_c__type_description__FieldType__FIELD_TYPE_DOUBLE,
      0,
      0,
      {NULL, 0, 0},
    },
    {NULL, 0, 0},
  },
};

const rosidl_runtime_c__type_description__TypeDescription *
niryo_interfaces__msg__Detection__get_type_description(
  const rosidl_message_type_support_t * type_support)
{
  (void)type_support;
  static bool constructed = false;
  static const rosidl_runtime_c__type_description__TypeDescription description = {
    {
      {niryo_interfaces__msg__Detection__TYPE_NAME, 30, 30},
      {niryo_interfaces__msg__Detection__FIELDS, 6, 6},
    },
    {NULL, 0, 0},
  };
  if (!constructed) {
    constructed = true;
  }
  return &description;
}

static char toplevel_type_raw_source[] =
  "# Detected object from vision node\n"
  "float64 x          # world-frame X (metres)\n"
  "float64 y          # world-frame Y (metres)\n"
  "float64 z          # world-frame Z (metres, table surface)\n"
  "string  color      # \"blue\" | \"orange\"\n"
  "string  label      # \"good\" | \"defective\"\n"
  "float64 confidence # 0.0\\xe2\\x80\\x931.0";

static char msg_encoding[] = "msg";

// Define all individual source functions

const rosidl_runtime_c__type_description__TypeSource *
niryo_interfaces__msg__Detection__get_individual_type_description_source(
  const rosidl_message_type_support_t * type_support)
{
  (void)type_support;
  static const rosidl_runtime_c__type_description__TypeSource source = {
    {niryo_interfaces__msg__Detection__TYPE_NAME, 30, 30},
    {msg_encoding, 3, 3},
    {toplevel_type_raw_source, 292, 292},
  };
  return &source;
}

const rosidl_runtime_c__type_description__TypeSource__Sequence *
niryo_interfaces__msg__Detection__get_type_description_sources(
  const rosidl_message_type_support_t * type_support)
{
  (void)type_support;
  static rosidl_runtime_c__type_description__TypeSource sources[1];
  static const rosidl_runtime_c__type_description__TypeSource__Sequence source_sequence = {sources, 1, 1};
  static bool constructed = false;
  if (!constructed) {
    sources[0] = *niryo_interfaces__msg__Detection__get_individual_type_description_source(NULL),
    constructed = true;
  }
  return &source_sequence;
}
