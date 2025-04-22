import approx
import simulatedannealing
import hillclimbing
import bnb

# main.py
import argparse
import sys
import time
import random


def main():
    parser = argparse.ArgumentParser(description='Minimum Set Cover Solver')
    parser.add_argument('-inst', required=True, help='Input filename')
    parser.add_argument('-alg', required=True, choices=['BnB', 'Approx', 'LS1', 'LS2'], help='Algorithm to use')
    parser.add_argument('-time', type=int, required=True, help='Cutoff time in seconds')
    parser.add_argument('-seed', type=int, required=False, help='Random seed')

    args = parser.parse_args()

    # Set random seed
    random.seed(args.seed)

    # Dispatch to the selected algorithm
    start_time = time.time()
    if args.alg == 'BnB':
        bnb.run(args.inst, args.time, args.seed)
    elif args.alg == 'Approx':
        approx.run(args.inst)
    elif args.alg == 'LS1':
        ls1.run(args.inst, args.time, args.seed)
    elif args.alg == 'LS2':
        simulatedannealing.process_file(args.inst, args.alg, args.time, args.seed)
    else:
        print("Unknown algorithm.")
        sys.exit(1)

    print(f"Completed in {time.time() - start_time:.2f}s")

if __name__ == '__main__':
    main()
