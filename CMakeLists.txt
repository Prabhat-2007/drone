# Install Python executables
install(PROGRAMS
  src/examples/offboard_py/offboard_control.py
  DESTINATION lib/${PROJECT_NAME}
)

install(PROGRAMS
  px4_ros_com/offboard_takeoff.py
  px4_ros_com/offboard_trajectories.py 
  DESTINATION lib/${PROJECT_NAME}
)
