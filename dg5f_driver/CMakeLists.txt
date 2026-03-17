cmake_minimum_required(VERSION 3.8)
project(dg5f_driver)

if(CMAKE_COMPILER_IS_GNUCXX OR CMAKE_CXX_COMPILER_ID MATCHES "Clang")
  add_compile_options(-Wall -Wextra -Wpedantic)
endif()

find_package(ament_cmake REQUIRED)
find_package(rclcpp REQUIRED)
find_package(trajectory_msgs REQUIRED)
find_package(sensor_msgs REQUIRED) 
find_package(delto_hardware REQUIRED)

# dg5f_operator_driver executable
add_executable(dg5f_operator_driver src/dg5f_operator_driver.cpp)
ament_target_dependencies(dg5f_operator_driver rclcpp trajectory_msgs sensor_msgs)

target_include_directories(dg5f_operator_driver PUBLIC
  $<BUILD_INTERFACE:${CMAKE_CURRENT_SOURCE_DIR}/include>
  $<INSTALL_INTERFACE:include>
)

install(TARGETS 
  dg5f_operator_driver
  DESTINATION lib/${PROJECT_NAME}
)

install(
  PROGRAMS 
  script/dg5f_left_jtc_test.py
  script/dg5f_right_jtc_test.py
  script/dg5f_left_pid_test.py
  script/dg5f_right_pid_test.py
  script/dg5f_left_pid_all_test.py
  script/dg5f_right_pid_all_test.py
  script/manus_retarget/manus_retarget.py
  DESTINATION lib/${PROJECT_NAME}
)

install(
  DIRECTORY include/
  DESTINATION include
)

install(
  DIRECTORY config urdf launch
  DESTINATION share/${PROJECT_NAME}
)

if(BUILD_TESTING)
  find_package(ament_lint_auto REQUIRED)
  set(ament_cmake_cpplint_FOUND TRUE)
  ament_lint_auto_find_test_dependencies()
endif()

ament_package()
