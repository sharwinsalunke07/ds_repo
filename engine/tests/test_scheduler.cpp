#include "../src/Scenario.h"
#include "../src/Scheduler.h"
#include <iostream>
#include <sstream>
#include <cassert>

int main() {
    std::cout << "========================================\n";
    std::cout << "Starting Scheduler Test Suite\n";
    std::cout << "========================================\n";

    // 1. Basic Scenario Test
    {
        std::string basicContent = 
            "CONFIG workers=2 policy=PRIORITY preemptive=0 aging=0 miss_action=DROP max_time=30\n"
            "TASK id=1 arrive=0 burst=4 deadline=10 priority=3\n"
            "TASK id=2 arrive=1 burst=3 deadline=8  priority=1\n"
            "TASK id=3 arrive=2 burst=5 deadline=15 priority=2\n"
            "TASK id=4 arrive=4 burst=2 deadline=12 priority=4\n";

        Scenario sc = Scenario::loadFromString(basicContent);
        std::stringstream ss;
        Scheduler sched(sc, ss);
        MetricsSummary m = sched.run();

        assert(m.totalTasks == 4);
        assert(m.doneTasks == 4);
        assert(m.missedTasks == 0);
        assert(m.missRate == 0.0);
        std::cout << "[PASS] Basic scenario test passed (all tasks completed on time).\n";
    }

    // 2. Overload & Miss Detection Test
    {
        std::string overloadContent =
            "CONFIG workers=1 policy=EDF preemptive=1 aging=0 miss_action=DROP max_time=40\n"
            "TASK id=1 arrive=0 burst=8 deadline=10 priority=2\n"
            "TASK id=2 arrive=1 burst=6 deadline=9  priority=1\n"
            "TASK id=3 arrive=2 burst=7 deadline=11 priority=3\n"
            "TASK id=4 arrive=3 burst=5 deadline=8  priority=1\n"
            "TASK id=5 arrive=4 burst=9 deadline=14 priority=4\n";

        Scenario sc = Scenario::loadFromString(overloadContent);
        std::stringstream ss;
        Scheduler sched(sc, ss);
        MetricsSummary m = sched.run();

        assert(m.totalTasks == 5);
        assert(m.missedTasks > 0);
        assert(m.missRate > 0.0);
        std::cout << "[PASS] Overload test passed (" << m.missedTasks << " missed tasks detected correctly).\n";
    }

    // 3. Priority Change & Preemption Test
    {
        std::string prioChangeContent =
            "CONFIG workers=1 policy=PRIORITY preemptive=1 aging=0 miss_action=DROP max_time=40\n"
            "TASK id=1 arrive=0 burst=6 deadline=20 priority=3\n"
            "TASK id=2 arrive=1 burst=5 deadline=25 priority=2\n"
            "TASK id=3 arrive=2 burst=4 deadline=16 priority=5\n"
            "PRIORITY_CHANGE time=4 id=3 new_priority=1\n";

        Scenario sc = Scenario::loadFromString(prioChangeContent);
        std::stringstream ss;
        Scheduler sched(sc, ss);
        MetricsSummary m = sched.run();

        assert(m.totalTasks == 3);
        std::string logOutput = ss.str();
        assert(logOutput.find("\"event\":\"PRIORITY_CHANGE\"") != std::string::npos);
        assert(logOutput.find("\"event\":\"PREEMPT\"") != std::string::npos);
        std::cout << "[PASS] Priority change and preemption test passed.\n";
    }

    // 4. Determinism Test
    {
        std::string content =
            "CONFIG workers=2 policy=HYBRID preemptive=1 aging=1 aging_interval=4 miss_action=DROP max_time=30\n"
            "TASK id=1 arrive=0 burst=5 deadline=12 priority=3\n"
            "TASK id=2 arrive=1 burst=3 deadline=6  priority=1\n"
            "TASK id=3 arrive=2 burst=4 deadline=14 priority=2\n";

        Scenario sc1 = Scenario::loadFromString(content);
        std::stringstream ss1;
        Scheduler sched1(sc1, ss1);
        sched1.run();

        Scenario sc2 = Scenario::loadFromString(content);
        std::stringstream ss2;
        Scheduler sched2(sc2, ss2);
        sched2.run();

        assert(ss1.str() == ss2.str());
        std::cout << "[PASS] Determinism test passed (identical output on consecutive runs).\n";
    }

    std::cout << "========================================\n";
    std::cout << "All Scheduler tests PASSED successfully!\n";
    std::cout << "========================================\n";
    return 0;
}
