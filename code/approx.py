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

example usage of executable: python3 approx.py -inst ../data/small1.in -alg Approx -time 600
'''
import argparse
import random
import time
import os

def approx_msc(U, S):
    '''
    input: U = {x_1, x_2, ..., x_n}: set of n elements
           S = {S_1, S_2, ..., S_m} where S_i is a subset of U: list of sets
    output: C is a subset of S such that C covers all elements in U: list of sets
            indices: list of indices of the sets in C
    '''
    selected = []         # list to store the selected sets and their indices
    S_indices = list(range(len(S)))  # list of indices of the sets in S
    uncovered = set(U)    # all elements in U are initially uncovered
    while uncovered:      # while there are still uncovered elements
        best_subset = max(S, key=lambda s: len(uncovered & s))  # find the subset that covers the most uncovered elements
        idx = S.index(best_subset)  # get the index of the best subset
        selected.append((best_subset, idx))  # add the best subset and its index to the selected list
        uncovered -= best_subset    # remove the covered elements from the uncovered set


    # below is optional
    def needs_pruning(s, C):
        # check if the set s is necessary in the cover
        # a set is necessary if removing it would leave some elements uncovered
        remaining = set().union(*(c for c in C if c != s))
        return s <= remaining  # if s is a subset of the remaining sets, it is not necessary
    
    # prune the cover to remove any redundant sets
    # prune the indices of any redundant sets
    pruned = []                                              # list to store the pruned sets and their indices
    for subset, idx in selected:                             # iterate over the selected sets
        temp_cover = [s for s, _ in selected if s != subset] # create a temporary cover without the current subset
        if not needs_pruning(subset, temp_cover):            # check if the current subset is necessary
            pruned.append((subset, idx))                     # if it is necessary, add it to the pruned list

    pruned_indices = [idx for _, idx in pruned]              # extract the indices of the pruned sets
    pruned_sets = [s for s, _ in pruned]                     # extract the pruned sets
    return pruned_sets, pruned_indices

def parse_instance(filepath):
    '''
    input: filepath: path to the file containing the instance
    output: U: set of elements
            S: list of subsets
    '''
    with open(filepath, 'r') as f:
        lines = f.readlines()
    
    n, m = map(int, lines[0].split())         # Read the first line to get n and m, n is the number of elements, m is the number of subsets
    S = []

    for line in lines[1:]:                    # Read the next m lines to get the subsets
        parts = list(map(int, line.split()))  # Each line starts with the size of the subset followed by the elements in the subset
        S_i = set(parts[1:])                  # The first element is the size of the subset, the rest are the elements in the subset
        S.append(S_i)                         # Add the subset to the list S
    U = set(range(1, n + 1))                  # Create the set U with elements from 1 to n
    return U, S

def write_output(instance, method, cutoff, solution):
    '''
    input: instance: path to the file containing the dataset
           method: name of the method used to solve the instance
           cutoff: time limit for the algorithm
           solution: list of indices in the solution
    output: None
    '''
    instance_name = instance.split('/')[-1]               # Extract the base name of the instance file (e.g., test1.in)
    instance_name = os.path.splitext(instance_name)[0]    # Remove the file extension (e.g., test1)
    output_dir = "../output"                              # Define the output directory and file name
    base_name = f"{instance_name}_{method}_{cutoff}"
    output_path = f"{output_dir}/{base_name}.sol"

    with open(output_path, 'w') as f:                     # Write the output to the specified file
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
    args = parser.parse_args()

    U, S = parse_instance(args.inst)              # Parse the instance file to get U and S
    if args.alg == 'Approx':                      # Check if the algorithm is Approx
        start_time = time.time()                  # Run the approximation algorithm
        _, indices = approx_msc(U, S)             # Get the solution and its indices
        elapsed_time = time.time() - start_time   # Calculate the elapsed time
        if elapsed_time > args.time:
            print(f"Algorithm timed out after {args.time} seconds")
            return
        write_output(args.inst, args.alg, args.time, indices)

'''
uncomment to run the main script
def run(instance_path, cutoff=None, seed=None):
    '''
    wrapper to run the approximation algorithm (for use with exec script)

    input:
        instance_path (str): path to input .in file in data folder
        cutoff (int): cutoff time in seconds (not used here, but included for compatibility)
        seed (int): random seed (not used in this deterministic algorithm)
    '''
    U, S = parse_instance(instance_path)
    start_time = time.time()
    _, indices = approx_msc(U, S)
    elapsed_time = time.time() - start_time

    if cutoff is not None and elapsed_time > cutoff:
        print(f"Approximation algorithm exceeded cutoff time of {cutoff} seconds.")
        return

    write_output(instance_path, "Approx", cutoff if cutoff else 0, indices)
'''
if __name__ == "__main__":
    main()
