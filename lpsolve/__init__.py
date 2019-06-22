
import os, sys
from .parser import parse_file

VERSION = "0.1.0"


def main():

    print(f"Steve's LP Solver {VERSION}")

    if len(sys.argv) != 3:
        print(f"USAGE: lpsolve --lp FILE")
        sys.exit(1)

    filename = sys.argv[2]
    print(f"Loading LP problem from CPLEX LP format, filename={filename}")
    problem = parse_file(filename)


    print("")
    print("Problem constructed")
    print("")
    print(f"Objective function: {problem.objective}")
    print(f"Subject to:")
    for c in problem.constraints:
        print(f"  {c.name}: {c}")

    print("Across variables:")
    print(f"{problem.symbols}")
