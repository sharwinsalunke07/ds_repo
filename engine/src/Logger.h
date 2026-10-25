#ifndef LOGGER_H
#define LOGGER_H

#include <string>
#include <vector>
#include <unordered_map>
#include <iostream>

struct MetricsSummary {
    int totalTasks = 0;
    int doneTasks = 0;
    int missedTasks = 0;
    double missRate = 0.0;
    double avgWait = 0.0;
    double avgTurnaround = 0.0;
    std::vector<double> utilization;
    std::unordered_map<int, double> perPriorityMiss;
    int maxQueueLength = 0;
    double throughput = 0.0;
};

class Logger {
private:
    std::ostream& out;

public:
    explicit Logger(std::ostream& os = std::cout);

    void logArrive(int t, int id, int priority, int deadline);
    void logStart(int t, int id, int worker);
    void logPreempt(int t, int id, int worker, int byId);
    void logPriorityChange(int t, int id, int oldPriority, int newPriority);
    void logFinish(int t, int id, int worker);
    void logMiss(int t, int id, int deadline);
    void logAging(int t, int id, int oldPriority, int newPriority);
    void logTick(int t, const std::vector<int>& queue, const std::vector<int>& running, int missedCount, int doneCount);
    void logMetrics(const MetricsSummary& metrics);
};

#endif // LOGGER_H
