// generated from rosidl_generator_cpp/resource/idl__traits.hpp.em
// with input from niryo_interfaces:msg/Detection.idl
// generated code does not contain a copyright notice

// IWYU pragma: private, include "niryo_interfaces/msg/detection.hpp"


#ifndef NIRYO_INTERFACES__MSG__DETAIL__DETECTION__TRAITS_HPP_
#define NIRYO_INTERFACES__MSG__DETAIL__DETECTION__TRAITS_HPP_

#include <stdint.h>

#include <sstream>
#include <string>
#include <type_traits>

#include "niryo_interfaces/msg/detail/detection__struct.hpp"
#include "rosidl_runtime_cpp/traits.hpp"

namespace niryo_interfaces
{

namespace msg
{

inline void to_flow_style_yaml(
  const Detection & msg,
  std::ostream & out)
{
  out << "{";
  // member: x
  {
    out << "x: ";
    rosidl_generator_traits::value_to_yaml(msg.x, out);
    out << ", ";
  }

  // member: y
  {
    out << "y: ";
    rosidl_generator_traits::value_to_yaml(msg.y, out);
    out << ", ";
  }

  // member: z
  {
    out << "z: ";
    rosidl_generator_traits::value_to_yaml(msg.z, out);
    out << ", ";
  }

  // member: color
  {
    out << "color: ";
    rosidl_generator_traits::value_to_yaml(msg.color, out);
    out << ", ";
  }

  // member: label
  {
    out << "label: ";
    rosidl_generator_traits::value_to_yaml(msg.label, out);
    out << ", ";
  }

  // member: confidence
  {
    out << "confidence: ";
    rosidl_generator_traits::value_to_yaml(msg.confidence, out);
  }
  out << "}";
}  // NOLINT(readability/fn_size)

inline void to_block_style_yaml(
  const Detection & msg,
  std::ostream & out, size_t indentation = 0)
{
  // member: x
  {
    if (indentation > 0) {
      out << std::string(indentation, ' ');
    }
    out << "x: ";
    rosidl_generator_traits::value_to_yaml(msg.x, out);
    out << "\n";
  }

  // member: y
  {
    if (indentation > 0) {
      out << std::string(indentation, ' ');
    }
    out << "y: ";
    rosidl_generator_traits::value_to_yaml(msg.y, out);
    out << "\n";
  }

  // member: z
  {
    if (indentation > 0) {
      out << std::string(indentation, ' ');
    }
    out << "z: ";
    rosidl_generator_traits::value_to_yaml(msg.z, out);
    out << "\n";
  }

  // member: color
  {
    if (indentation > 0) {
      out << std::string(indentation, ' ');
    }
    out << "color: ";
    rosidl_generator_traits::value_to_yaml(msg.color, out);
    out << "\n";
  }

  // member: label
  {
    if (indentation > 0) {
      out << std::string(indentation, ' ');
    }
    out << "label: ";
    rosidl_generator_traits::value_to_yaml(msg.label, out);
    out << "\n";
  }

  // member: confidence
  {
    if (indentation > 0) {
      out << std::string(indentation, ' ');
    }
    out << "confidence: ";
    rosidl_generator_traits::value_to_yaml(msg.confidence, out);
    out << "\n";
  }
}  // NOLINT(readability/fn_size)

inline std::string to_yaml(const Detection & msg, bool use_flow_style = false)
{
  std::ostringstream out;
  if (use_flow_style) {
    to_flow_style_yaml(msg, out);
  } else {
    to_block_style_yaml(msg, out);
  }
  return out.str();
}

}  // namespace msg

}  // namespace niryo_interfaces

namespace rosidl_generator_traits
{

[[deprecated("use niryo_interfaces::msg::to_block_style_yaml() instead")]]
inline void to_yaml(
  const niryo_interfaces::msg::Detection & msg,
  std::ostream & out, size_t indentation = 0)
{
  niryo_interfaces::msg::to_block_style_yaml(msg, out, indentation);
}

[[deprecated("use niryo_interfaces::msg::to_yaml() instead")]]
inline std::string to_yaml(const niryo_interfaces::msg::Detection & msg)
{
  return niryo_interfaces::msg::to_yaml(msg);
}

template<>
inline const char * data_type<niryo_interfaces::msg::Detection>()
{
  return "niryo_interfaces::msg::Detection";
}

template<>
inline const char * name<niryo_interfaces::msg::Detection>()
{
  return "niryo_interfaces/msg/Detection";
}

template<>
struct has_fixed_size<niryo_interfaces::msg::Detection>
  : std::integral_constant<bool, false> {};

template<>
struct has_bounded_size<niryo_interfaces::msg::Detection>
  : std::integral_constant<bool, false> {};

template<>
struct is_message<niryo_interfaces::msg::Detection>
  : std::true_type {};

}  // namespace rosidl_generator_traits

#endif  // NIRYO_INTERFACES__MSG__DETAIL__DETECTION__TRAITS_HPP_
