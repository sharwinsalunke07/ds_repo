CXX = g++
CXXFLAGS = -std=c++17 -O2 -Wall -Isrc

SRC = src/Scenario.cpp src/Logger.cpp src/Scheduler.cpp
OBJ = $(SRC:.cpp=.o)

all: scheduler

scheduler: $(OBJ) src/main.o
	$(CXX) $(CXXFLAGS) -o scheduler $(OBJ) src/main.o

%.o: %.cpp
	$(CXX) $(CXXFLAGS) -c $< -o $@

test_heap: tests/test_heap.cpp
	$(CXX) $(CXXFLAGS) -o test_heap tests/test_heap.cpp
	./test_heap

test_scheduler: $(OBJ) tests/test_scheduler.cpp
	$(CXX) $(CXXFLAGS) -o test_scheduler tests/test_scheduler.cpp $(OBJ)
	./test_scheduler

clean:
	rm -f src/*.o scheduler test_heap test_scheduler *.exe
