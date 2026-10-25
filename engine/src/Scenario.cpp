#include "Scenario.h"
#include <fstream>
#include <sstream>
#include <iostream>
#include <algorithm>
#include <cctype>

namespace {
    std::string trim(const std::string& str) {
        size_t first = str.find_first_not_of(" \t\r\n");
        if (first == std::string::npos) return "";
        size_t last = str.find_last_not_of(" \t\r\n");
        return str.substr(first, (last - first + 1));
    }

    std::vector<std::string> splitTokens(const std::string& line) {
        std::vector<std::string> tokens;
        std::stringstream ss(line);
        std::string token;
        while (ss >> token) {
            tokens.push_back(token);
        }
        return tokens;
    }

    std::pair<std::string, std::string> parseKeyValue(const std::string& token) {
        size_t eqPos = token.find('=');
        if (eqPos == std::string::npos) {
            return {token, ""};
        }
        return {token.substr(0, eqPos), token.substr(eqPos + 1)};
    }
}

Scenario Scenario::loadFromFile(const std::string& filepath) {
    std::ifstream infile(filepath);
    if (!infile.is_open()) {
        throw std::runtime_error("Cannot open scenario file: " + filepath);
    }
    std::stringstream buffer;
    buffer << infile.rdbuf();
    return loadFromString(buffer.str());
}

Scenario Scenario::loadFromString(const std::string& content) {
    Scenario sc;
    std::stringstream ss(content);
    std::string line;
    int lineNum = 0;

    while (std::getline(ss, line)) {
        lineNum++;
        std::string trimmed = trim(line);
        if (trimmed.empty() || trimmed[0] == '#') {
            continue;
        }

        std::vector<std::string> tokens = splitTokens(trimmed);
        if (tokens.empty()) continue;

        const std::string& directive = tokens[0];

        if (directive == "CONFIG") {
            for (size_t i = 1; i < tokens.size(); ++i) {
                auto kv = parseKeyValue(tokens[i]);
                const std::string& key = kv.first;
                const std::string& val = kv.second;

                if (key == "workers") {
                    sc.config.workers = std::max(1, std::stoi(val));
                } else if (key == "policy") {
                    sc.config.policy = parsePolicy(val);
                } else if (key == "preemptive") {
                    sc.config.preemptive = (val == "1" || val == "true");
                } else if (key == "aging") {
                    sc.config.aging = (val == "1" || val == "true");
                } else if (key == "aging_interval") {
                    sc.config.agingInterval = std::max(1, std::stoi(val));
                } else if (key == "miss_action") {
                    sc.config.missAction = parseMissAction(val);
                } else if (key == "max_time") {
                    sc.config.maxTime = std::max(1, std::stoi(val));
                } else if (key == "hybrid_weight") {
                    sc.config.hybridWeight = std::stoi(val);
                } else {
                    std::cerr << "Warning [Line " << lineNum << "]: Unknown CONFIG key '" << key << "'\n";
                }
            }
        } else if (directive == "TASK") {
            Task t;
            for (size_t i = 1; i < tokens.size(); ++i) {
                auto kv = parseKeyValue(tokens[i]);
                const std::string& key = kv.first;
                const std::string& val = kv.second;

                if (key == "id") {
                    t.id = std::stoi(val);
                } else if (key == "arrive") {
                    t.arrive = std::stoi(val);
                } else if (key == "burst") {
                    t.burst = std::stoi(val);
                    t.remaining = t.burst;
                } else if (key == "deadline") {
                    t.deadline = std::stoi(val);
                } else if (key == "priority") {
                    t.priority = std::stoi(val);
                }
            }

            if (sc.tasks.find(t.id) != sc.tasks.end()) {
                throw std::runtime_error("Error [Line " + std::to_string(lineNum) + "]: Duplicate task id=" + std::to_string(t.id));
            }
            if (t.burst <= 0) {
                throw std::runtime_error("Error [Line " + std::to_string(lineNum) + "]: Task id=" + std::to_string(t.id) + " burst must be > 0");
            }
            if (t.priority < 1 || t.priority > 5) {
                throw std::runtime_error("Error [Line " + std::to_string(lineNum) + "]: Task id=" + std::to_string(t.id) + " priority must be between 1 and 5");
            }

            sc.tasks[t.id] = t;
        } else if (directive == "PRIORITY_CHANGE") {
            PriorityChangeEvent ev;
            for (size_t i = 1; i < tokens.size(); ++i) {
                auto kv = parseKeyValue(tokens[i]);
                const std::string& key = kv.first;
                const std::string& val = kv.second;

                if (key == "time") {
                    ev.time = std::stoi(val);
                } else if (key == "id") {
                    ev.taskId = std::stoi(val);
                } else if (key == "new_priority") {
                    ev.newPriority = std::stoi(val);
                }
            }
            if (ev.newPriority < 1 || ev.newPriority > 5) {
                throw std::runtime_error("Error [Line " + std::to_string(lineNum) + "]: PRIORITY_CHANGE new_priority must be between 1 and 5");
            }
            sc.priorityChanges.push_back(ev);
        } else {
            std::cerr << "Warning [Line " << lineNum << "]: Unknown directive '" << directive << "'\n";
        }
    }

    sc.validate();
    return sc;
}

void Scenario::validate() const {
    if (config.workers < 1) {
        throw std::runtime_error("Scenario validation failed: workers must be at least 1");
    }
    for (const auto& kv : tasks) {
        const Task& t = kv.second;
        if (t.deadline <= t.arrive) {
            std::cerr << "Warning: Task id=" << t.id << " deadline (" << t.deadline 
                      << ") is <= arrive (" << t.arrive << "). Will miss immediately!\n";
        }
    }
}
