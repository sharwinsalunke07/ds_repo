#include "Scenario.h"
#include "Scheduler.h"
#include <iostream>

int main(int argc, char* argv[]) {
    if (argc < 2) {
        std::cerr << "Usage: scheduler <scenario_file>\n";
        std::cerr << "Example: scheduler scenarios/basic.txt\n";
        return 1;
    }

    std::string filepath = argv[1];

    try {
        Scenario scenario = Scenario::loadFromFile(filepath);
        Scheduler scheduler(scenario, std::cout);
        scheduler.run();
    } catch (const std::exception& ex) {
        std::cerr << "Scheduler Error: " << ex.what() << "\n";
        return 1;
    }

    return 0;
}
