
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

    # 1) Load the problem from disk
    print(f"1) Loading LP problem from CPLEX LP format, filename={filename}...")
    problem = parse_file(filename)
    print("")
    print("Problem constructed")
    problem.summarise()





    # 2) Convert to standard form symbolically
    print("2) Converting to standard form...")
    problem = to_standard_form(problem)



    # 3) Build a tableau and assess optimality
    print("3) Solving...")
    solution = solve(problem)

    problem.summarise()

