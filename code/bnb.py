"""
CSE6140 - Spring 2025 Project
Minimum Set Cover - Branch and Bound Algorithm

This file implements an exact Branch and Bound (BnB) algorithm to solve the Minimum Set Cover problem.
The objective is to identify the smallest number of subsets whose union covers all elements in the universe.

--------------------------------------------------------------
Algorithm Overview:
--------------------------------------------------------------
Branch and Bound systematically explores the solution space using depth-first search (DFS), 
while pruning branches that cannot yield better solutions than the current best. 

- Initial upper bound: We compute a greedy approximate solution (O(log n) approximation) to set the initial upper bound.
- Lower bound estimation: For pruning, we estimate the minimum number of additional subsets needed to cover the remaining elements using a greedy heuristic.
- Pruning: Any branch with lower bound ≥ current best is discarded.
- Recursion continues until all possible branches are explored or the cutoff time is reached.

This method guarantees an exact solution but is exponential in the worst case.
To manage runtime, the search is bounded by a time limit.

--------------------------------------------------------------
Inputs:
- A text file describing the universe and its collection of subsets
  (same format as used in approx.py).

--------------------------------------------------------------
Outputs:
- .sol file containing the size and indices of the selected subsets
- .trace file logging (time, cost) whenever a better solution is found

--------------------------------------------------------------
Example Usage:
    python3 bnb.py -inst ../data/small1.in -alg BnB -time 600

Assumptions:
- The input parser and approximation algorithm (used for initial bound) are in approx.py
- Subsets are represented as sets of elements (e.g., set([1, 2, 3]))
- The approx_msc, parse_instance and write_output functions are available from approx.py
"""

import time, os, math
from approx import approx_msc, parse_instance, write_output

def lower_bound_lp(covered, subsets, universe):
    """
    A better lower bound heuristic using an LP relaxation idea.
    For each uncovered element e in (universe - covered), let f(e) be the number
    of available subsets (in 'subsets') that cover e. Then the lower bound is the ceiling
    of the sum over e of 1/f(e).
    """
    remaining = universe - covered
    if not remaining:
        return 0
    total = 0.0
    for e in remaining:
        f_e = sum(1 for s in subsets if e in s)
        if f_e == 0:
            return float("inf")  # If an element is uncovered by any available subset
        total += 1 / f_e
    return math.ceil(total)

def log_trace(trace_path, timestamp, cost):
    """
    input:  trace_path: path to the .trace file to write to
            timestamp: current elapsed time (in seconds)
            cost: size of the current best solution

    output: None

    This function appends a line to the trace file recording the time at which a new best solution
    was found, along with the size of that solution. Used for tracking progress during execution.
    """
    with open(trace_path, "a") as f:
        f.write(f"{timestamp:.2f} {cost}\n")

def run_bnb(filepath, cutoff):
    """
    input:  filepath: path to the file containing the instance
            cutoff: time limit (in seconds) for the algorithm

    output: None (writes output to .sol and .trace files)

    This function runs a branch and bound algorithm to solve the Minimum Set Cover problem.
    It initializes an upper bound using a greedy approximation, then recursively explores the solution space
    using depth-first search. Subtrees are pruned if their lower bound exceeds the best solution found so far.
    A trace file logs each time a better solution is discovered.
    """
    instance_name = os.path.splitext(os.path.basename(filepath))[0]
    trace_path = os.path.join("..", "output", f"{instance_name}_BnB_{cutoff}.trace")

    start_time = time.time()
    universe, subsets = parse_instance(filepath)
    num_sets = len(subsets)

    # Use the greedy approximation to initialize the best solution.
    _, greedy_indices = approx_msc(universe, subsets)
    
    # Use a dictionary to store the current best solution and its cost.
    best = {
        "solution": list(greedy_indices),
        "cost": len(greedy_indices)
    }
    log_trace(trace_path, time.time() - start_time, best["cost"])

    # Define the DFS function that updates 'best' in place.
    def dfs(selected, covered, idx):
        elapsed = time.time() - start_time
        if elapsed > cutoff:
            return

        if covered == universe:
            if len(selected) < best["cost"]:
                best["solution"] = list(selected)
                best["cost"] = len(selected)
                log_trace(trace_path, elapsed, best["cost"])
            return

        if idx >= num_sets:
            return

        lower_bound = len(selected) + lower_bound_lp(covered, subsets[idx:], universe)
        if lower_bound >= best["cost"]:
            return

        # Include current subset: add the index and union the subset elements.
        dfs(selected + [idx], covered | subsets[idx], idx + 1)
        # Exclude current subset: keep current state and continue.
        dfs(selected, covered, idx + 1)

    dfs([], set(), 0)

    # Write the output using write_output (best solution is stored as indices)
    one_indexed_solution = [i + 1 for i in best["solution"]]
    write_output(filepath, "BnB", cutoff, one_indexed_solution)

def main():
    """
    input:  command-line arguments (parsed using argparse):
                -inst <input_file_path>
                -alg BnB
                -time <cutoff_time_in_seconds>

    output: None

    This is the entry point for the Branch and Bound program. It parses command-line arguments,
    and calls run_bnb with the appropriate parameters. Designed to support CLI usage.
    """
    parser = argparse.ArgumentParser()
    parser.add_argument('-inst', required=True)
    parser.add_argument('-alg', choices=['BnB'], required=True)
    parser.add_argument('-time', type=int, required=True)
    args = parser.parse_args()

    if args.alg == 'BnB':
        run_bnb(args.inst, args.time)

if __name__ == "__main__":
    main()
