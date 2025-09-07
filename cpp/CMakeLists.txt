cmake_minimum_required(VERSION 3.14)

# Project name and version
project(BayerImageProcessor VERSION 1.0 LANGUAGES C CXX)

# Set C++ standard (C++17 is required for filesystem)
set(CMAKE_CXX_STANDARD 17)
set(CMAKE_CXX_STANDARD_REQUIRED True)

# Set C standard
set(CMAKE_C_STANDARD 11)

# Ensure vcpkg is integrated
set(CMAKE_TOOLCHAIN_FILE "C:/Users/Ahmad/vcpkg/scripts/buildsystems/vcpkg.cmake" CACHE STRING "vcpkg toolchain file" FORCE)

# Find OpenCV (vcpkg will set this up automatically)
find_package(OpenCV REQUIRED)

# Source files
set(SHIFT_RIGHT_IMAGE_SRC shiftRightImage.c)
set(BAYER_IMAGE_PROCESSOR_SRC BayerImageProcessor.cpp)
set(DETECT_AND_FIX_SHIFT_SRC detectAndFixShift.cpp)

# Define executable name
add_executable(BayerImageProcessor ${BAYER_IMAGE_PROCESSOR_SRC})

# Add include directories for OpenCV
target_include_directories(BayerImageProcessor PRIVATE
    ${OpenCV_INCLUDE_DIRS}
)

# Link OpenCV to your target
target_link_libraries(BayerImageProcessor PRIVATE
    ${OpenCV_LIBS}
)

# Optional: Set output directories (optional)
set_target_properties(BayerImageProcessor PROPERTIES
    RUNTIME_OUTPUT_DIRECTORY ${CMAKE_BINARY_DIR}/bin
)


# Executable: detectAndFixShift
add_executable(detectAndFixShift ${DETECT_AND_FIX_SHIFT_SRC})
target_include_directories(detectAndFixShift PRIVATE ${OpenCV_INCLUDE_DIRS})
target_link_libraries(detectAndFixShift PRIVATE ${OpenCV_LIBS})
set_target_properties(detectAndFixShift PROPERTIES
    RUNTIME_OUTPUT_DIRECTORY ${CMAKE_BINARY_DIR}/bin
)


# Executable: shiftRightImage
add_executable(shiftRightImage ${SHIFT_RIGHT_IMAGE_SRC})
target_include_directories(shiftRightImage PRIVATE ${CMAKE_CURRENT_SOURCE_DIR})
set_target_properties(shiftRightImage PROPERTIES
    RUNTIME_OUTPUT_DIRECTORY ${CMAKE_BINARY_DIR}/bin
)
