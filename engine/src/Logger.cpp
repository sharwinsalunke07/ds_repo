#include "Logger.h"
#include <iomanip>
#include <sstream>

Logger::Logger(std::ostream& os) : out(os) {}

void Logger::logArrive(int t, int id, int priority, int deadline) {
    out << "{\"t\":" << t 
        << ",\"event\":\"ARRIVE\""
        << ",\"id\":" << id 
        << ",\"priority\":" << priority 
        << ",\"deadline\":" << deadline 
        << "}\n";
    out.flush();
}

void Logger::logStart(int t, int id, int worker) {
    out << "{\"t\":" << t 
        << ",\"event\":\"START\""
        << ",\"id\":" << id 
        << ",\"worker\":" << worker 
        << "}\n";
    out.flush();
}

void Logger::logPreempt(int t, int id, int worker, int byId) {
    out << "{\"t\":" << t 
        << ",\"event\":\"PREEMPT\""
        << ",\"id\":" << id 
        << ",\"worker\":" << worker 
        << ",\"by\":" << byId 
        << "}\n";
    out.flush();
}

void Logger::logPriorityChange(int t, int id, int oldPriority, int newPriority) {
    out << "{\"t\":" << t 
        << ",\"event\":\"PRIORITY_CHANGE\""
        << ",\"id\":" << id 
        << ",\"old\":" << oldPriority 
        << ",\"new\":" << newPriority 
        << "}\n";
    out.flush();
}

void Logger::logFinish(int t, int id, int worker) {
    out << "{\"t\":" << t 
        << ",\"event\":\"FINISH\""
        << ",\"id\":" << id 
        << ",\"worker\":" << worker 
        << "}\n";
    out.flush();
}

void Logger::logMiss(int t, int id, int deadline) {
    out << "{\"t\":" << t 
        << ",\"event\":\"MISS\""
        << ",\"id\":" << id 
        << ",\"deadline\":" << deadline 
        << "}\n";
    out.flush();
}

void Logger::logAging(int t, int id, int oldPriority, int newPriority) {
    out << "{\"t\":" << t 
        << ",\"event\":\"AGING\""
        << ",\"id\":" << id 
        << ",\"old\":" << oldPriority 
        << ",\"new\":" << newPriority 
        << "}\n";
    out.flush();
}

void Logger::logTick(int t, const std::vector<int>& queue, const std::vector<int>& running, int missedCount, int doneCount) {
    out << "{\"t\":" << t 
        << ",\"event\":\"TICK\""
        << ",\"queue\":[";
    for (size_t i = 0; i < queue.size(); ++i) {
        out << queue[i] << (i + 1 < queue.size() ? "," : "");
    }
    out << "],\"running\":[";
    for (size_t i = 0; i < running.size(); ++i) {
        out << running[i] << (i + 1 < running.size() ? "," : "");
    }
    out << "],\"missed\":" << missedCount 
        << ",\"done\":" << doneCount 
        << "}\n";
    out.flush();
}

void Logger::logMetrics(const MetricsSummary& m) {
    std::ios state(nullptr);
    state.copyfmt(out);

    out << std::fixed << std::setprecision(4);
    out << "{\"event\":\"METRICS\""
        << ",\"total\":" << m.totalTasks
        << ",\"done\":" << m.doneTasks
        << ",\"missed\":" << m.missedTasks
        << ",\"miss_rate\":" << m.missRate
        << ",\"avg_wait\":" << m.avgWait
        << ",\"avg_turnaround\":" << m.avgTurnaround
        << ",\"throughput\":" << m.throughput
        << ",\"max_queue\":" << m.maxQueueLength
        << ",\"utilization\":[";
    
    for (size_t i = 0; i < m.utilization.size(); ++i) {
        out << m.utilization[i] << (i + 1 < m.utilization.size() ? "," : "");
    }
    out << "],\"per_priority_miss\":{";
    
    bool first = true;
    for (int p = 1; p <= 5; ++p) {
        if (!first) out << ",";
        double rate = 0.0;
        auto it = m.perPriorityMiss.find(p);
        if (it != m.perPriorityMiss.end()) {
            rate = it->second;
        }
        out << "\"" << p << "\":" << rate;
        first = false;
    }
    out << "}}\n";
    out.flush();

    out.copyfmt(state);
}
