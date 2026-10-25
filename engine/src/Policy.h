#ifndef POLICY_H
#define POLICY_H

#include "Task.h"
#include <unordered_map>
#include <string>
#include <stdexcept>

enum class PolicyType {
    PRIORITY,
    EDF,
    HYBRID,
    LST
};

inline PolicyType parsePolicy(const std::string& name) {
    if (name == "PRIORITY") return PolicyType::PRIORITY;
    if (name == "EDF")      return PolicyType::EDF;
    if (name == "HYBRID")   return PolicyType::HYBRID;
    if (name == "LST")      return PolicyType::LST;
    throw std::invalid_argument("Unknown policy: " + name);
}

inline std::string policyToString(PolicyType p) {
    switch (p) {
        case PolicyType::PRIORITY: return "PRIORITY";
        case PolicyType::EDF:      return "EDF";
        case PolicyType::HYBRID:   return "HYBRID";
        case PolicyType::LST:      return "LST";
        default:                   return "UNKNOWN";
    }
}

/**
 * @brief Comparator for the hand-built IndexedHeap.
 * 
 * Uses static keys for waiting tasks to preserve heap order without dynamic drift.
 * Returns true if task idA has higher urgency (lower key value) than idB.
 */
struct TaskComparator {
    const std::unordered_map<int, Task>* tasks = nullptr;
    PolicyType policy = PolicyType::PRIORITY;
    int hybridWeight = 3;

    TaskComparator() = default;
    TaskComparator(const std::unordered_map<int, Task>* taskMap, PolicyType pol = PolicyType::PRIORITY, int weight = 3)
        : tasks(taskMap), policy(pol), hybridWeight(weight) {}

    bool operator()(int idA, int idB) const {
        if (idA == idB || tasks == nullptr) return false;
        auto itA = tasks->find(idA);
        auto itB = tasks->find(idB);
        if (itA == tasks->end() || itB == tasks->end()) return idA < idB;

        const Task& a = itA->second;
        const Task& b = itB->second;

        switch (policy) {
            case PolicyType::PRIORITY: {
                if (a.priority != b.priority) return a.priority < b.priority;
                if (a.arrive != b.arrive) return a.arrive < b.arrive;
                return a.id < b.id;
            }
            case PolicyType::EDF: {
                if (a.deadline != b.deadline) return a.deadline < b.deadline;
                if (a.priority != b.priority) return a.priority < b.priority;
                return a.id < b.id;
            }
            case PolicyType::HYBRID: {
                long long keyA = static_cast<long long>(a.deadline) - static_cast<long long>(hybridWeight) * (6 - a.priority);
                long long keyB = static_cast<long long>(b.deadline) - static_cast<long long>(hybridWeight) * (6 - b.priority);
                if (keyA != keyB) return keyA < keyB;
                if (a.arrive != b.arrive) return a.arrive < b.arrive;
                return a.id < b.id;
            }
            case PolicyType::LST: {
                long long slackA = static_cast<long long>(a.deadline) - a.remaining;
                long long slackB = static_cast<long long>(b.deadline) - b.remaining;
                if (slackA != slackB) return slackA < slackB;
                if (a.arrive != b.arrive) return a.arrive < b.arrive;
                return a.id < b.id;
            }
        }
        return a.id < b.id;
    }
};

#endif // POLICY_H
