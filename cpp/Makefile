# General Makefile for C/C++ projects

CC = gcc
CXX = g++ # C++ compiler
CFLAGS = -Wall -O2 -g -Wno-unused-parameter -Wno-unused-variable
CXXFLAGS = -Wall -O2 -g -std=c++17 # C++ flags (you can change the standard version)
LDFLAGS =
SRC_C = $(wildcard *.c)
SRC_CPP = $(wildcard *.cpp)     # Get C++ source files
OBJ_C = $(SRC_C:.c=.o)
OBJ_CPP = $(SRC_CPP:.cpp=.o)    # Object files for C++

.PHONY: all clean

# Rule to compile C source files
%.o: %.c
	$(CC) $(CFLAGS) -c $< -o $@

# Rule to compile C++ source files
%.o: %.cpp
	$(CXX) $(CXXFLAGS) -c $< -o $@

# Existing targets for other programs
test_shiftRightImage.exe : shiftRightImage.o
	$(CC) $(CFLAGS) -o ./exe/$@ $^
	
test_detectAndFixShift.exe : detectAndFixShift.cpp
	$(CXX) -o $@ $< $(CXXFLAGS) `pkg-config --cflags --libs opencv4`

test_binToPng.exe : binToPng.cpp
	$(CXX) -o $@ $< $(CXXFLAGS) `pkg-config --cflags --libs opencv4`

# Clean up object files and executables
clean:
	rm -f $(OBJ_C) $(OBJ_CPP) *.exe
