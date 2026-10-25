#ifndef INDEXED_HEAP_H
#define INDEXED_HEAP_H

#include <vector>
#include <stdexcept>
#include <algorithm>
#include <functional>

/**
 * @brief Hand-built Indexed Binary Min-Heap.
 * 
 * Satisfies the assignment constraint: No std::priority_queue in product code.
 * Maintains an internal position lookup pos[id] -> index in heap, enabling:
 * - push(id): O(log n)
 * - pop(): O(log n)
 * - peek(): O(1)
 * - update(id): O(log n)
 * - remove(id): O(log n)
 * - contains(id): O(1)
 * 
 * Invariants:
 * 1. For every 0 <= i < heap.size(): pos[heap[i]] == i.
 * 2. If id is not present in the heap: pos[id] == -1.
 * 3. Min-heap property: For every i > 0, !comp(heap[i], heap[parent(i)]).
 */
template <typename Compare = std::less<int>>
class IndexedHeap {
private:
    std::vector<int> heap; // Array of item IDs
    std::vector<int> pos;  // pos[id] = index in heap array (-1 if absent)
    Compare comp;

    inline int parent(int i) const { return (i - 1) / 2; }
    inline int left(int i) const { return 2 * i + 1; }
    inline int right(int i) const { return 2 * i + 2; }

    void ensureCapacity(int id) {
        if (id < 0) {
            throw std::invalid_argument("Item ID must be non-negative");
        }
        if (id >= static_cast<int>(pos.size())) {
            pos.resize(std::max(id + 1, static_cast<int>(pos.size()) * 2), -1);
        }
    }

    void swapNodes(int i, int j) {
        int idA = heap[i];
        int idB = heap[j];
        heap[i] = idB;
        heap[j] = idA;
        pos[idA] = j;
        pos[idB] = i;
    }

    void siftUp(int i) {
        while (i > 0) {
            int p = parent(i);
            // comp(a, b) returns true if a is strictly higher priority (more urgent) than b
            if (comp(heap[i], heap[p])) {
                swapNodes(i, p);
                i = p;
            } else {
                break;
            }
        }
    }

    void siftDown(int i) {
        int n = static_cast<int>(heap.size());
        while (true) {
            int best = i;
            int l = left(i);
            int r = right(i);

            if (l < n && comp(heap[l], heap[best])) {
                best = l;
            }
            if (r < n && comp(heap[r], heap[best])) {
                best = r;
            }

            if (best != i) {
                swapNodes(i, best);
                i = best;
            } else {
                break;
            }
        }
    }

public:
    explicit IndexedHeap(Compare comparator = Compare())
        : comp(comparator) {}

    void setComparator(Compare newComp) {
        comp = newComp;
        // Re-heapify all elements in O(n)
        for (int i = static_cast<int>(heap.size()) / 2 - 1; i >= 0; --i) {
            siftDown(i);
        }
    }

    bool contains(int id) const {
        if (id < 0 || id >= static_cast<int>(pos.size())) return false;
        return pos[id] != -1;
    }

    int getPosition(int id) const {
        if (!contains(id)) return -1;
        return pos[id];
    }

    size_t size() const {
        return heap.size();
    }

    bool empty() const {
        return heap.empty();
    }

    void push(int id) {
        ensureCapacity(id);
        if (pos[id] != -1) {
            // Already present; update its position if key changed
            update(id);
            return;
        }
        int idx = static_cast<int>(heap.size());
        heap.push_back(id);
        pos[id] = idx;
        siftUp(idx);
    }

    int peek() const {
        if (heap.empty()) {
            throw std::runtime_error("IndexedHeap is empty on peek()");
        }
        return heap[0];
    }

    int pop() {
        if (heap.empty()) {
            throw std::runtime_error("IndexedHeap is empty on pop()");
        }
        int topId = heap[0];
        int lastIdx = static_cast<int>(heap.size()) - 1;
        if (lastIdx == 0) {
            pos[topId] = -1;
            heap.pop_back();
            return topId;
        }

        swapNodes(0, lastIdx);
        pos[topId] = -1;
        heap.pop_back();
        siftDown(0);
        return topId;
    }

    bool update(int id) {
        if (!contains(id)) return false;
        int idx = pos[id];
        siftUp(idx);
        siftDown(idx);
        return true;
    }

    bool remove(int id) {
        if (!contains(id)) return false;
        int idx = pos[id];
        int lastIdx = static_cast<int>(heap.size()) - 1;

        if (idx == lastIdx) {
            pos[id] = -1;
            heap.pop_back();
            return true;
        }

        swapNodes(idx, lastIdx);
        pos[id] = -1;
        heap.pop_back();
        siftUp(idx);
        siftDown(idx);
        return true;
    }

    void clear() {
        for (int id : heap) {
            if (id >= 0 && id < static_cast<int>(pos.size())) {
                pos[id] = -1;
            }
        }
        heap.clear();
    }

    const std::vector<int>& getHeap() const {
        return heap;
    }

    /**
     * @brief Validates heap invariants and pos[] mapping consistency.
     */
    bool checkInvariants() const {
        int n = static_cast<int>(heap.size());
        for (int i = 0; i < n; ++i) {
            int id = heap[i];
            if (id < 0 || id >= static_cast<int>(pos.size()) || pos[id] != i) {
                return false; // pos mismatch
            }
            if (i > 0) {
                int p = parent(i);
                if (comp(heap[i], heap[p])) {
                    return false; // min-heap violation
                }
            }
        }
        return true;
    }
};

#endif // INDEXED_HEAP_H
