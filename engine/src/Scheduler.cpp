#include "Scheduler.h"
#include <algorithm>
#include <iostream>

Scheduler::Scheduler(const Scenario& sc, std::ostream& logStream)
    : scenario(sc),
      logger(logStream) {
    workers.resize(scenario.config.workers);
    for (int i = 0; i < scenario.config.workers; ++i) {
        workers[i].id = i;
        workers[i].currentTaskId = -1;
        workers[i].busyTicks = 0;
    }

    comparator = TaskComparator(&scenario.tasks, scenario.config.policy, scenario.config.hybridWeight);
    heap.setComparator(comparator);
}

void Scheduler::handleArrivals(int t) {
    std::vector<int> arrivingIds;
    for (const auto& kv : scenario.tasks) {
        if (kv.second.arrive == t && kv.second.status == TaskStatus::NOT_ARRIVED) {
            arrivingIds.push_back(kv.first);
        }
    }
    std::sort(arrivingIds.begin(), arrivingIds.end());

    for (int id : arrivingIds) {
        Task& tsk = scenario.tasks[id];
        tsk.status = TaskStatus::WAITING;
        logger.logArrive(t, tsk.id, tsk.priority, tsk.deadline);
        heap.push(id);
    }
}

void Scheduler::handlePriorityChanges(int t) {
    for (const auto& ev : scenario.priorityChanges) {
        if (ev.time == t) {
            auto it = scenario.tasks.find(ev.taskId);
            if (it != scenario.tasks.end()) {
                Task& tsk = it->second;
                if (tsk.status != TaskStatus::DONE && tsk.status != TaskStatus::MISSED) {
                    int oldP = tsk.priority;
                    tsk.priority = ev.newPriority;
                    logger.logPriorityChange(t, tsk.id, oldP, tsk.priority);
                    if (heap.contains(tsk.id)) {
                        heap.update(tsk.id);
                    }
                }
            }
        }
    }
}

void Scheduler::handleAging(int t) {
    if (!scenario.config.aging || t == 0 || (t % scenario.config.agingInterval != 0)) {
        return;
    }

    // Waiting tasks currently in heap
    std::vector<int> heapCopy = heap.getHeap();
    std::sort(heapCopy.begin(), heapCopy.end());

    for (int id : heapCopy) {
        Task& tsk = scenario.tasks[id];
        if (tsk.priority > 1) {
            int oldP = tsk.priority;
            tsk.priority -= 1;
            logger.logAging(t, tsk.id, oldP, tsk.priority);
            heap.update(tsk.id);
        }
    }
}

void Scheduler::handleDeadlines(int t) {
    // 1. Check waiting tasks in heap
    std::vector<int> heapTasks = heap.getHeap();
    for (int id : heapTasks) {
        Task& tsk = scenario.tasks[id];
        if (tsk.remaining > 0 && t >= tsk.deadline) {
            if (!tsk.missReported) {
                tsk.missReported = true;
                missedCount++;
                logger.logMiss(t, tsk.id, tsk.deadline);
            }
            if (scenario.config.missAction == MissAction::DROP) {
                tsk.status = TaskStatus::MISSED;
                heap.remove(tsk.id);
            }
        }
    }

    // 2. Check running tasks on workers
    for (auto& w : workers) {
        if (!w.isIdle()) {
            Task& tsk = scenario.tasks[w.currentTaskId];
            if (tsk.remaining > 0 && t >= tsk.deadline) {
                if (!tsk.missReported) {
                    tsk.missReported = true;
                    missedCount++;
                    logger.logMiss(t, tsk.id, tsk.deadline);
                }
                if (scenario.config.missAction == MissAction::DROP) {
                    tsk.status = TaskStatus::MISSED;
                    w.currentTaskId = -1; // Free worker immediately
                }
            }
        }
    }
}

void Scheduler::handlePreemption(int t) {
    if (!scenario.config.preemptive) return;

    while (!heap.empty()) {
        int victimWorkerIdx = -1;
        int victimTaskId = -1;

        // Find the running task with least urgency (highest key)
        for (size_t i = 0; i < workers.size(); ++i) {
            if (!workers[i].isIdle()) {
                int runningId = workers[i].currentTaskId;
                if (victimTaskId == -1) {
                    victimWorkerIdx = static_cast<int>(i);
                    victimTaskId = runningId;
                } else {
                    // If runningId is strictly less urgent than current victim
                    if (comparator(victimTaskId, runningId)) {
                        victimWorkerIdx = static_cast<int>(i);
                        victimTaskId = runningId;
                    }
                }
            }
        }

        if (victimTaskId == -1) {
            // No running tasks to preempt
            break;
        }

        int candidateId = heap.peek();
        // candidateId must be strictly more urgent than victimTaskId
        if (comparator(candidateId, victimTaskId)) {
            // Perform preemption
            heap.pop();
            logger.logPreempt(t, victimTaskId, workers[victimWorkerIdx].id, candidateId);

            Task& victim = scenario.tasks[victimTaskId];
            victim.status = TaskStatus::WAITING;
            heap.push(victimTaskId);

            Task& nextTask = scenario.tasks[candidateId];
            nextTask.status = TaskStatus::RUNNING;
            if (nextTask.startTime == -1) {
                nextTask.startTime = t;
            }
            workers[victimWorkerIdx].currentTaskId = candidateId;
            logger.logStart(t, candidateId, workers[victimWorkerIdx].id);
        } else {
            // Heap top is not more urgent than any running task
            break;
        }
    }
}

void Scheduler::handleAssignment(int t) {
    for (auto& w : workers) {
        if (w.isIdle() && !heap.empty()) {
            int nextId = heap.pop();
            Task& tsk = scenario.tasks[nextId];
            tsk.status = TaskStatus::RUNNING;
            if (tsk.startTime == -1) {
                tsk.startTime = t;
            }
            w.currentTaskId = nextId;
            logger.logStart(t, nextId, w.id);
        }
    }
}

void Scheduler::executeStep(int t) {
    for (auto& w : workers) {
        if (!w.isIdle()) {
            Task& tsk = scenario.tasks[w.currentTaskId];
            tsk.remaining--;
            w.busyTicks++;

            if (tsk.remaining == 0) {
                tsk.finishTime = t + 1;
                if (!tsk.missReported) {
                    tsk.status = TaskStatus::DONE;
                    doneCount++;
                } else {
                    tsk.status = TaskStatus::MISSED;
                }
                logger.logFinish(t, tsk.id, w.id);
                w.currentTaskId = -1;
            }
        }
    }

    // Waiting tasks accumulate wait time
    for (int id : heap.getHeap()) {
        scenario.tasks[id].waitedTicks++;
    }
}

bool Scheduler::shouldStopEarly(int t) const {
    // Check if any future arrivals exist
    for (const auto& kv : scenario.tasks) {
        if (kv.second.arrive > t) return false;
        if (kv.second.status == TaskStatus::NOT_ARRIVED || kv.second.status == TaskStatus::WAITING) {
            return false;
        }
    }
    // Check if any future priority changes exist
    for (const auto& ev : scenario.priorityChanges) {
        if (ev.time > t) return false;
    }
    // Check if any workers are busy
    for (const auto& w : workers) {
        if (!w.isIdle()) return false;
    }
    return heap.empty();
}

MetricsSummary Scheduler::computeMetrics(int totalTicks) const {
    MetricsSummary m;
    m.totalTasks = static_cast<int>(scenario.tasks.size());
    m.doneTasks = doneCount;
    m.missedTasks = missedCount;
    m.missRate = (m.totalTasks > 0) ? (static_cast<double>(m.missedTasks) / m.totalTasks) : 0.0;
    m.maxQueueLength = maxQueueLength;
    m.throughput = (totalTicks > 0) ? (static_cast<double>(doneCount) / totalTicks) : 0.0;

    double totalWait = 0.0;
    double totalTurnaround = 0.0;
    int turnaroundCount = 0;

    std::unordered_map<int, int> prioTotal;
    std::unordered_map<int, int> prioMissed;
    for (int p = 1; p <= 5; ++p) {
        prioTotal[p] = 0;
        prioMissed[p] = 0;
    }

    for (const auto& kv : scenario.tasks) {
        const Task& t = kv.second;
        totalWait += t.waitedTicks;
        prioTotal[t.priority]++;
        if (t.missReported) {
            prioMissed[t.priority]++;
        }
        if (t.finishTime != -1) {
            totalTurnaround += (t.finishTime - t.arrive);
            turnaroundCount++;
        }
    }

    m.avgWait = (m.totalTasks > 0) ? (totalWait / m.totalTasks) : 0.0;
    m.avgTurnaround = (turnaroundCount > 0) ? (totalTurnaround / turnaroundCount) : 0.0;

    m.utilization.resize(workers.size());
    for (size_t i = 0; i < workers.size(); ++i) {
        m.utilization[i] = (totalTicks > 0) ? (static_cast<double>(workers[i].busyTicks) / totalTicks) : 0.0;
    }

    for (int p = 1; p <= 5; ++p) {
        if (prioTotal[p] > 0) {
            m.perPriorityMiss[p] = static_cast<double>(prioMissed[p]) / prioTotal[p];
        } else {
            m.perPriorityMiss[p] = 0.0;
        }
    }

    return m;
}

MetricsSummary Scheduler::run() {
    int totalSimulationTicks = 0;

    for (int t = 0; t < scenario.config.maxTime; ++t) {
        currentTick = t;

        // 1. Arrivals
        handleArrivals(t);

        // 2. Priority Changes
        handlePriorityChanges(t);

        // 3. Aging
        handleAging(t);

        // 4. Deadlines
        handleDeadlines(t);

        // 5. Preemption
        handlePreemption(t);

        // 6. Assignment
        handleAssignment(t);

        // 7. Execution
        executeStep(t);

        // 8. Snapshot TICK
        std::vector<int> queueSnapshot = heap.getHeap();
        // Sort queueSnapshot in urgency order for UI replay
        std::sort(queueSnapshot.begin(), queueSnapshot.end(), comparator);
        maxQueueLength = std::max(maxQueueLength, static_cast<int>(queueSnapshot.size()));

        std::vector<int> runningSnapshot;
        for (const auto& w : workers) {
            runningSnapshot.push_back(w.currentTaskId);
        }

        logger.logTick(t, queueSnapshot, runningSnapshot, missedCount, doneCount);
        totalSimulationTicks = t + 1;

        // 9. Stop early check
        if (shouldStopEarly(t)) {
            break;
        }
    }

    MetricsSummary metrics = computeMetrics(totalSimulationTicks);
    logger.logMetrics(metrics);
    return metrics;
}
