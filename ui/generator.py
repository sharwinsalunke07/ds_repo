import random
from typing import List, Dict, Any
import pandas as pd

def generate_random_scenario(
    num_tasks: int = 8,
    arrival_spread: int = 15,
    min_burst: int = 2,
    max_burst: int = 8,
    tightness_factor: float = 1.6,
    seed: int = 42
) -> pd.DataFrame:
    """
    Generates a deterministic list of random tasks based on a seed.
    tightness_factor controls deadline: deadline = arrive + round(burst * factor) + buffer
    """
    rng = random.Random(seed)
    tasks = []

    for i in range(1, num_tasks + 1):
        arrive = rng.randint(0, arrival_spread)
        burst = rng.randint(min_burst, max_burst)
        
        # Calculate plausible deadline
        min_feasible_deadline = arrive + burst
        extra_slack = rng.randint(1, max(2, int(burst * tightness_factor)))
        deadline = min_feasible_deadline + extra_slack
        
        priority = rng.randint(1, 5)

        tasks.append({
            "id": i,
            "name": f"Generated Task {i}",
            "arrive": arrive,
            "burst": burst,
            "deadline": deadline,
            "priority": priority
        })

    # Sort tasks by arrival time, then id
    tasks.sort(key=lambda x: (x["arrive"], x["id"]))
    return pd.DataFrame(tasks)
