// generated from rosidl_generator_cpp/resource/idl__builder.hpp.em
// with input from niryo_interfaces:msg/Detection.idl
// generated code does not contain a copyright notice

// IWYU pragma: private, include "niryo_interfaces/msg/detection.hpp"


#ifndef NIRYO_INTERFACES__MSG__DETAIL__DETECTION__BUILDER_HPP_
#define NIRYO_INTERFACES__MSG__DETAIL__DETECTION__BUILDER_HPP_

#include <algorithm>
#include <utility>

#include "niryo_interfaces/msg/detail/detection__struct.hpp"
#include "rosidl_runtime_cpp/message_initialization.hpp"


namespace niryo_interfaces
{

namespace msg
{

namespace builder
{

class Init_Detection_confidence
{
public:
  explicit Init_Detection_confidence(::niryo_interfaces::msg::Detection & msg)
  : msg_(msg)
  {}
  ::niryo_interfaces::msg::Detection confidence(::niryo_interfaces::msg::Detection::_confidence_type arg)
  {
    msg_.confidence = std::move(arg);
    return std::move(msg_);
  }

private:
  ::niryo_interfaces::msg::Detection msg_;
};

class Init_Detection_label
{
public:
  explicit Init_Detection_label(::niryo_interfaces::msg::Detection & msg)
  : msg_(msg)
  {}
  Init_Detection_confidence label(::niryo_interfaces::msg::Detection::_label_type arg)
  {
    msg_.label = std::move(arg);
    return Init_Detection_confidence(msg_);
  }

private:
  ::niryo_interfaces::msg::Detection msg_;
};

class Init_Detection_color
{
public:
  explicit Init_Detection_color(::niryo_interfaces::msg::Detection & msg)
  : msg_(msg)
  {}
  Init_Detection_label color(::niryo_interfaces::msg::Detection::_color_type arg)
  {
    msg_.color = std::move(arg);
    return Init_Detection_label(msg_);
  }

private:
  ::niryo_interfaces::msg::Detection msg_;
};

class Init_Detection_z
{
public:
  explicit Init_Detection_z(::niryo_interfaces::msg::Detection & msg)
  : msg_(msg)
  {}
  Init_Detection_color z(::niryo_interfaces::msg::Detection::_z_type arg)
  {
    msg_.z = std::move(arg);
    return Init_Detection_color(msg_);
  }

private:
  ::niryo_interfaces::msg::Detection msg_;
};

class Init_Detection_y
{
public:
  explicit Init_Detection_y(::niryo_interfaces::msg::Detection & msg)
  : msg_(msg)
  {}
  Init_Detection_z y(::niryo_interfaces::msg::Detection::_y_type arg)
  {
    msg_.y = std::move(arg);
    return Init_Detection_z(msg_);
  }

private:
  ::niryo_interfaces::msg::Detection msg_;
};

class Init_Detection_x
{
public:
  Init_Detection_x()
  : msg_(::rosidl_runtime_cpp::MessageInitialization::SKIP)
  {}
  Init_Detection_y x(::niryo_interfaces::msg::Detection::_x_type arg)
  {
    msg_.x = std::move(arg);
    return Init_Detection_y(msg_);
  }

private:
  ::niryo_interfaces::msg::Detection msg_;
};

}  // namespace builder

}  // namespace msg

template<typename MessageType>
auto build();

template<>
inline
auto build<::niryo_interfaces::msg::Detection>()
{
  return niryo_interfaces::msg::builder::Init_Detection_x();
}

}  // namespace niryo_interfaces

#endif  // NIRYO_INTERFACES__MSG__DETAIL__DETECTION__BUILDER_HPP_
