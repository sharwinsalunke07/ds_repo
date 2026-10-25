#include "../src/IndexedHeap.h"
#include <iostream>
#include <vector>
#include <unordered_map>
#include <random>
#include <cassert>
#include <algorithm>

struct TestItem {
    int id;
    int priority; // lower value = higher priority
};

int main() {
    std::cout << "========================================\n";
    std::cout << "Starting IndexedHeap Test Suite\n";
    std::cout << "========================================\n";

    // 1. Basic deterministic tests
    {
        std::unordered_map<int, int> priorities;
        auto comp = [&priorities](int a, int b) {
            if (priorities[a] != priorities[b]) {
                return priorities[a] < priorities[b];
            }
            return a < b;
        };

        IndexedHeap<decltype(comp)> heap(comp);

        priorities[1] = 50;
        priorities[2] = 20;
        priorities[3] = 40;
        priorities[4] = 10;
        priorities[5] = 30;

        heap.push(1);
        heap.push(2);
        heap.push(3);
        heap.push(4);
        heap.push(5);

        assert(heap.size() == 5);
        assert(heap.checkInvariants());
        assert(heap.peek() == 4); // 10 is min

        // Pop min
        int p1 = heap.pop();
        assert(p1 == 4);
        assert(heap.size() == 4);
        assert(heap.peek() == 2); // 20 is min
        assert(heap.checkInvariants());

        // Update priority of item 1 from 50 down to 5 (most urgent)
        priorities[1] = 5;
        heap.update(1);
        assert(heap.checkInvariants());
        assert(heap.peek() == 1);

        // Remove item 3
        assert(heap.contains(3));
        bool removed = heap.remove(3);
        assert(removed);
        assert(!heap.contains(3));
        assert(heap.size() == 3);
        assert(heap.checkInvariants());

        // Pop remaining
        assert(heap.pop() == 1); // 5
        assert(heap.pop() == 2); // 20
        assert(heap.pop() == 5); // 30
        assert(heap.empty());
        assert(heap.checkInvariants());

        std::cout << "[PASS] Basic push, pop, update, and remove tests passed.\n";
    }

    // 2. Randomized stress testing against brute-force oracle
    {
        const int NUM_OPERATIONS = 15000;
        const int MAX_ITEMS = 500;

        std::unordered_map<int, int> priorities;
        auto comp = [&priorities](int a, int b) {
            if (priorities[a] != priorities[b]) {
                return priorities[a] < priorities[b];
            }
            return a < b; // tiebreaker
        };

        IndexedHeap<decltype(comp)> heap(comp);
        std::vector<int> oracle; // simple list of active IDs

        std::mt19937 rng(42);
        std::uniform_int_distribution<int> opDist(0, 3);
        std::uniform_int_distribution<int> idDist(1, MAX_ITEMS);
        std::uniform_int_distribution<int> prioDist(1, 1000);

        for (int step = 0; step < NUM_OPERATIONS; ++step) {
            int op = opDist(rng);

            if (op == 0 || oracle.empty()) {
                // Operation: PUSH or update if exists
                int id = idDist(rng);
                int prio = prioDist(rng);
                priorities[id] = prio;

                auto it = std::find(oracle.begin(), oracle.end(), id);
                if (it == oracle.end()) {
                    oracle.push_back(id);
                    heap.push(id);
                } else {
                    heap.update(id);
                }
            } else if (op == 1) {
                // Operation: POP
                // Find oracle minimum
                auto minIt = std::min_element(oracle.begin(), oracle.end(), comp);
                int oracleMin = *minIt;
                oracle.erase(minIt);

                assert(!heap.empty());
                int heapMin = heap.pop();
                assert(heapMin == oracleMin);
            } else if (op == 2) {
                // Operation: UPDATE existing
                std::uniform_int_distribution<int> pickDist(0, static_cast<int>(oracle.size()) - 1);
                int id = oracle[pickDist(rng)];
                priorities[id] = prioDist(rng);
                heap.update(id);
            } else if (op == 3) {
                // Operation: REMOVE existing
                std::uniform_int_distribution<int> pickDist(0, static_cast<int>(oracle.size()) - 1);
                int idx = pickDist(rng);
                int id = oracle[idx];
                oracle.erase(oracle.begin() + idx);

                assert(heap.contains(id));
                bool rem = heap.remove(id);
                assert(rem);
            }

            // Invariant check
            assert(heap.size() == oracle.size());
            assert(heap.empty() == oracle.empty());
            assert(heap.checkInvariants());

            if (!oracle.empty()) {
                auto minIt = std::min_element(oracle.begin(), oracle.end(), comp);
                assert(heap.peek() == *minIt);
            }
        }

        std::cout << "[PASS] 15,000 randomized operations against brute-force oracle passed.\n";
    }

    std::cout << "========================================\n";
    std::cout << "All IndexedHeap tests PASSED successfully!\n";
    std::cout << "========================================\n";
    return 0;
}
