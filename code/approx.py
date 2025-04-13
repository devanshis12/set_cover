'''
Please implement an approximation algorithm for the Minimum Set Cover with approximation guarantees of O(log n).
Hint: There is a simple and intuitive greedy algorithm that heuristically chooses a subset until U is
covered and can achieve an approximation of O(log n). Can you come up with such an algorithm?

The input is a set of n elements and a collection of subsets of these elements. 
The goal is to find the smallest number of subsets such that their union covers all elements in the set.

approximation guarantees of O(log n)
OPT is size of the optimal solution
k is size of the greedy solution
need to show: GREEDY <= OPT * log n
    1. at each step, we pick the set that covers the most uncovered elements => GREEDY covers at least as many as any OPT set would
        - let m be the size of the set we picked
        - m <= size of the set OPT picked
    2. GREEDY covers at least >= remaining elements / size of the set we picked
    3. using recursion, let r_i be the number of remaining elements after i iterations
        5. r_i <= r_{i-1} - r_{i-1}/m (r_i = 0 is the goal => all elements are covered)
        6. r_i <= n(1 - 1/m)^i
        7. n(1 - 1/m)^k < 1     (take log of both sides)
        8. k >= m*log(n)         
        9. k = O(m*log(n))
        10. k = O(OPT*log n)    (since m <= OPT)
    11. k = O(log n)

    example usage of executable: python3 approx.py -inst ../data/small1.in -alg Approx -time 600 -seed 42
'''
import argparse
import random
import time

def approx_msc(U, S):
    '''
    input: U = {x_1, x_2, ..., x_n}: set of n elements
           S = {S_1, S_2, ..., S_m} where S_i is a subset of U: list of sets
    output: C is a subset of S such that C covers all elements in U: list of sets
    '''
    C = []                # initialize the cover as empty
    uncovered = set(U)    # all elements in U are initially uncovered
    while uncovered:      # while there are still uncovered elements
        best_subset = max(S, key=lambda s: len(uncovered & s))  # find the subset that covers the most uncovered elements
        C.append(best_subset)     # add it to the cover
        uncovered -= best_subset  # remove the covered elements from the uncovered set

    # below is optional
    def needs_pruning(s, C):
        # check if the set s is necessary in the cover
        # a set is necessary if removing it would leave some elements uncovered
        remaining = set().union(*(c for c in C if c != s))
        return s <= remaining  # if s is a subset of the remaining sets, it is not necessary
    
    # prune the cover to remove any redundant sets
    pruned = []
    for s in C:
        temp_cover = pruned + [x for x in C if x != s]
        if not needs_pruning(s, temp_cover):
            pruned.append(s)
    C = pruned  # update the cover with the pruned sets

    return C   

def parse_instance(filepath):
    '''
    input: filepath: path to the file containing the instance
    output: U: set of elements
            S: list of subsets
    '''
    with open(filepath, 'r') as f:
        lines = f.readlines()
    
    n, m = map(int, lines[0].split())
    S = []

    for line in lines[1:]:
        parts = list(map(int, line.split()))
        S_i = set(parts[1:])
        S.append(S_i)
    U = set(range(1, n + 1))
    return U, S

def write_output(instance, method, cutoff, seed, solution):
    '''
    input: instance: path to the file containing the dataset
           method: name of the method used to solve the instance
           cutoff: time limit for the algorithm
           seed: random seed used for the algorithm
           solution: list of sets in the solution
    output: None
    '''
    base_name = f"{instance} {method} {cutoff} {seed}"

    with open(f"{base_name}.out", 'w') as f:
        f.write(f"{len(solution)}\n")
        f.write(" ".join(map(str, solution)) + "\n")

def main():
    '''
    input: None
    output: None
    '''
    parser = argparse.ArgumentParser()
    parser.add_argument('-inst', required=True)
    parser.add_argument('-alg', choices=['Approx'], required=True)
    parser.add_argument('-time', type=int, required=True)
    parser.add_argument('-seed', type=int, required=False)
    args = parser.parse_args()

    random.seed(args.seed)

    U, S = parse_instance(args.inst)
    if args.alg == 'Approx':
        start_time = time.time()
        solution = approx_msc(U, S)
        elapsed_time = time.time() - start_time
        if elapsed_time > args.time:
            print(f"Algorithm timed out after {args.time} seconds")
            return
        write_output(args.inst, args.alg, args.time, args.seed, solution)

if __name__ == "__main__":
    main()