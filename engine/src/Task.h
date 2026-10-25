#ifndef TASK_H
#define TASK_H

#include <string>

enum class TaskStatus {
    NOT_ARRIVED,
    WAITING,
    RUNNING,
    DONE,
    MISSED
};

inline std::string statusToString(TaskStatus s) {
    switch (s) {
        case TaskStatus::NOT_ARRIVED: return "NOT_ARRIVED";
        case TaskStatus::WAITING:     return "WAITING";
        case TaskStatus::RUNNING:     return "RUNNING";
        case TaskStatus::DONE:        return "DONE";
        case TaskStatus::MISSED:      return "MISSED";
        default:                      return "UNKNOWN";
    }
}

struct Task {
    int id = 0;
    int arrive = 0;
    int burst = 0;
    int remaining = 0;
    int deadline = 0;
    int priority = 3; // 1 (most urgent) to 5 (least urgent)
    TaskStatus status = TaskStatus::NOT_ARRIVED;

    // Timing tracking for metrics
    int startTime = -1;       // First time task started running
    int finishTime = -1;      // Completion time (t + 1 when remaining hits 0)
    int waitedTicks = 0;      // Total ticks spent in WAITING status
    bool missReported = false; // Prevents duplicate MISS events in CONTINUE mode
};

#endif // TASK_H
