#ifndef SCENARIO_H
#define SCENARIO_H

#include "Task.h"
#include "Policy.h"
#include <vector>
#include <unordered_map>
#include <string>

enum class MissAction {
    DROP,
    CONTINUE
};

inline MissAction parseMissAction(const std::string& str) {
    if (str == "DROP") return MissAction::DROP;
    if (str == "CONTINUE") return MissAction::CONTINUE;
    throw std::invalid_argument("Unknown miss_action: " + str);
}

inline std::string missActionToString(MissAction action) {
    return (action == MissAction::DROP) ? "DROP" : "CONTINUE";
}

struct PriorityChangeEvent {
    int time = 0;
    int taskId = 0;
    int newPriority = 1;
};

struct ScenarioConfig {
    int workers = 1;
    PolicyType policy = PolicyType::PRIORITY;
    bool preemptive = false;
    bool aging = false;
    int agingInterval = 5;
    MissAction missAction = MissAction::DROP;
    int maxTime = 100;
    int hybridWeight = 3;
};

struct Scenario {
    ScenarioConfig config;
    std::unordered_map<int, Task> tasks;
    std::vector<PriorityChangeEvent> priorityChanges;

    static Scenario loadFromFile(const std::string& filepath);
    static Scenario loadFromString(const std::string& content);
    void validate() const;
};

#endif // SCENARIO_H
