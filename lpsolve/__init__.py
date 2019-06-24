
import os, sys
from .parser import parse_file
from .presolve import to_standard_form
from .solve import solve

VERSION = "0.1.0"


def main():

    print(f"Steve's LP Solver {VERSION}")

    if len(sys.argv) != 3:
        print(f"USAGE: lpsolve --lp FILE")
        sys.exit(1)

    filename = sys.argv[2]
    iteration_limit = 20
    heuristic = "lowest"

    # 1) Load the problem from disk
    print("")
    print(f"1) Loading LP problem from CPLEX LP format, filename={filename}...")
    problem = parse_file(filename)
    problem.summarise()





    # 2) Convert to standard form symbolically
    print("")
    print("2) Converting to standard form...")
    problem = to_standard_form(problem)



    # 3) Build a tableau and assess optimality
    print("")
    print(f"3) Solving with iteration limit of {iteration_limit} using heuristic '{heuristic}'")
    solution = solve(problem, iteration_limit, heuristic)


    print("")
    print(f"4) Solution summary")
    solution.summarise()

