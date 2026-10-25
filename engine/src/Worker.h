#ifndef WORKER_H
#define WORKER_H

struct Worker {
    int id = 0;
    int currentTaskId = -1; // -1 indicates idle
    int busyTicks = 0;      // Total ticks spent processing tasks

    bool isIdle() const {
        return currentTaskId == -1;
    }
};

#endif // WORKER_H
