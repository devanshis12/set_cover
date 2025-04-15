import argparse
import random
import time
import os
import math
import glob

""" Simulated Annealing
- Uses Approximation Algorithm as the initial solution

- Implements Simulated Annealing with:
    - A time cutoff (in seconds)
    - A no-improvement cutoff along with time cutoff
    - A probabilistic acceptance of worse moves based on a temperature schedule
    - add, swap, and remove possibilities at each iteration
    - run for max of 10 minutes per .in file
"""
def parse_instance(filepath):
    with open(filepath, 'r') as f:
        lines = f.readlines()
    n, m = map(int, lines[0].split())
    S = []
    raw_indices = []
    for i, line in enumerate(lines[1:], 1):
        parts = list(map(int, line.split()))
        S_i = set(parts[1:])
        S.append(S_i)
        raw_indices.append(i)
    U = set(range(1, n + 1))
    return U, S, raw_indices
def greedy_approx(U, S, raw_indices):
    cover_indices = []
    uncovered = set(U)
    S_copy = list(zip(S, range(len(S)), raw_indices))
    while uncovered:
        best_idx = max(range(len(S_copy)), key=lambda i: len(uncovered & S_copy[i][0]))
        best_set, idx, raw_idx = S_copy[best_idx]
        cover_indices.append(idx)
        uncovered -= best_set
        S_copy.pop(best_idx)
        if not uncovered:
            break
    original_indices = [raw_indices[i] for i in cover_indices]
    return cover_indices, original_indices

def get_coverage(solution_indices, S):
    covered = set()
    for i in solution_indices:
        covered.update(S[i])
    return covered
def is_valid_solution(solution_indices, S, U):
    return get_coverage(solution_indices, S) == U
def prune_solution(solution_indices, S, U):
    res = solution_indices.copy()
    i = 0
    while i < len(res):
        candidate = res[:i] + res[i+1:]
        if is_valid_solution(candidate, S, U):
            res = candidate
            i = 0
        else:
            i += 1
    return res
def simulated_annealing(U, S, raw_indices, cutoff_time, seed=1, threshold=100, initial_solution=None):
    random.seed(seed)
    start_time = time.time()

    if initial_solution is None:
        solution_indices, n = greedy_approx(U, S, raw_indices)
    else:
        solution_indices = initial_solution.copy()
    solution_indices = prune_solution(solution_indices, S, U)
    trace = [(0.0, len(solution_indices))]
    temp = 200
    final_temp = 2
    alpha = 0.995
    base_iterations = max(10, len(S) // 5)
    best_solution = solution_indices.copy()
    best_quality = len(best_solution)
    current_solution = solution_indices.copy()
    current_quality = len(current_solution)
    s = 0
    c = 0
    while temp > final_temp and (time.time() - start_time < cutoff_time) and (s < threshold):
        improved = False
        if s > 50:
            iters = base_iterations * 2 #try and do more work if approaching 100 same results
        else:
            iters = base_iterations
        for i in range(iters):
            if time.time() - start_time >= cutoff_time:
                break
            c += 1
            if c % 100 == 0:
                print(f"Iteration {c}: Temp={temp:.2f}, Current Quality={current_quality}, "
                      f"Best Quality={best_quality}, stagnation={s}")
            neighbors = []
            for i in range(len(current_solution)):
                candidate = current_solution[:i] + current_solution[i+1:]
                if is_valid_solution(candidate, S, U):
                    candidate = prune_solution(candidate, S, U)
                    neighbors.append(candidate)
            curr = set(range(len(S)))
            not_in_solution = list(curr - set(current_solution))
            #add 
            if not_in_solution:
                candidate = current_solution.copy()
                candidate.append(random.choice(not_in_solution))
                candidate = prune_solution(candidate, S, U)
                if is_valid_solution(candidate, S, U):
                    neighbors.append(candidate)
            #swap
            if current_solution and not_in_solution:
                candidate = current_solution.copy()
                iswap = random.randint(0, len(candidate) - 1)
                candidate[iswap] = random.choice(not_in_solution)
                candidate = prune_solution(candidate, S, U)
                if is_valid_solution(candidate, S, U):
                    neighbors.append(candidate)
            if len(current_solution) > 1:
                candidate = current_solution.copy()
                removal_index = random.choice(range(len(current_solution)))
                candidate.pop(removal_index)
                if is_valid_solution(candidate, S, U):
                    candidate = prune_solution(candidate, S, U)
                    neighbors.append(candidate)
            if not neighbors:
                continue
            for q in range(1):
                new_solution = random.choice(neighbors)
                new_quality = len(new_solution)
                delta = new_quality - current_quality
                if delta < 0 or random.random() < math.exp(-delta / temp):
                    current_solution = new_solution.copy()
                    current_quality = new_quality
                    if current_quality < best_quality:
                        best_solution = current_solution.copy()
                        best_quality = current_quality
                        trace.append((time.time() - start_time, best_quality))
                        improved = True
        if not improved:
            s += 1
        else:
            s = 0
        temp *= alpha
    original_indices = [raw_indices[i] for i in best_solution]
    elapsed = time.time() - start_time
    return best_solution, original_indices, trace, elapsed

def write_output(instance_path, method, cutoff, original_indices, seed=None, trace=None):
    instance_name = os.path.splitext(os.path.basename(instance_path))[0]
    output_dir = "output"
    os.makedirs(output_dir, exist_ok=True)
    if method in ["LS1"]:
        base_name = f"{instance_name}_{method}_{cutoff}_{seed}"
    solution_path = os.path.join(output_dir, f"{base_name}.sol")
    with open(solution_path, 'w') as f:
        f.write(f"{len(original_indices)}\n")
        f.write(" ".join(map(str, original_indices)) + "\n")
    if trace and method in ["LS1"]:
        trace_path = os.path.join(output_dir, f"{base_name}.trace")
        with open(trace_path, 'w') as f:
            for timestamp, quality in trace:
                f.write(f"{timestamp:.2f} {quality}\n")

def process_file(file_path, algorithm, cutoff_time, seed):
    U, S, raw_indices = parse_instance(file_path)
    if algorithm == "LS1":
        initial_solution, x = greedy_approx(U, S, raw_indices)
        initial_solution = prune_solution(initial_solution, S, U)
        best_solution, original_indices, trace, nxt = simulated_annealing(
            U, S, raw_indices, cutoff_time, seed=seed, initial_solution=initial_solution)
        write_output(file_path, algorithm, cutoff_time, original_indices, seed, trace)

def main():
    parser = argparse.ArgumentParser(description="Minimum Set Cover Solver")
    parser.add_argument('-inst', required=True)
    parser.add_argument('-alg', choices=['LS1'], required=True)
    parser.add_argument('-time', type=int, required=True)
    parser.add_argument('-seed', type=int, default=42)
    args = parser.parse_args()
    if os.path.isfile(args.inst):
        process_file(args.inst, args.alg, args.time, args.seed)
    elif os.path.isdir(args.inst) or args.inst == 'data':
        data_dir = args.inst if args.inst.endswith(os.sep) else args.inst + os.sep
        in_files = sorted(glob.glob(f"{data_dir}*.in"))
        for file_path in in_files:
            process_file(file_path, args.alg, args.time, args.seed)

if __name__ == "__main__":
    main()