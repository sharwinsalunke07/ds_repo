#ifndef SCHEDULER_H
#define SCHEDULER_H

#include "Scenario.h"
#include "IndexedHeap.h"
#include "Worker.h"
#include "Logger.h"
#include <vector>
#include <unordered_map>

class Scheduler {
private:
    Scenario scenario;
    std::vector<Worker> workers;
    TaskComparator comparator;
    IndexedHeap<TaskComparator> heap;
    Logger logger;

    int currentTick = 0;
    int doneCount = 0;
    int missedCount = 0;
    int maxQueueLength = 0;

    void handleArrivals(int t);
    void handlePriorityChanges(int t);
    void handleAging(int t);
    void handleDeadlines(int t);
    void handlePreemption(int t);
    void handleAssignment(int t);
    void executeStep(int t);
    bool shouldStopEarly(int t) const;
    MetricsSummary computeMetrics(int totalTicks) const;

public:
    explicit Scheduler(const Scenario& sc, std::ostream& logStream = std::cout);

    MetricsSummary run();
};

#endif // SCHEDULER_H
