
from . import ir

def solve(problem):
    """Solve the problem!"""


    tableau = Tableau(problem)
    tableau.summarise()

    return None












class Tableau:

    OBJECTIVE_KEY = "__objective__"

    def __init__(self, problem):

        self.table = {}
        self.table_columns = []     # Cache.  Delete if not needed.


        # Rows correspond to constraint functions
        for constraint in problem.constraints.values():
            # Loop over variables and find their coefficients in the constraints
            self.table[constraint] = {}
            for var in problem.symbols.table.values():
                self.table[constraint][var] = constraint.expression.find_coefficient_for_variable(var, default=0)

                # Keep an in-order record of the variables seen so we can traverse later
                if var not in self.table_columns:
                    self.table_columns.append(var)

        # Add a row at the end for the objective
        self.table[Tableau.OBJECTIVE_KEY] = {}
        for var in problem.symbols.table.values():
            self.table[Tableau.OBJECTIVE_KEY][var] = problem.objective.find_coefficient_for_variable(var, default=0)


    def summarise(self):

        CELL_WIDTH = 20

        # Start by printing the var names
        out = ["expression".rjust(CELL_WIDTH)]
        for var in self.table_columns:
            out.append(var.name.rjust(CELL_WIDTH))
        print("|".join(out))


        for constraint in self.table.keys():
            out = []

            # First col is special
            if isinstance(constraint, str):
                out.append(constraint.rjust(CELL_WIDTH))
            else:
                out.append(constraint.name.rjust(CELL_WIDTH))

            # Then mine the internal table for coefficients
            for var in self.table_columns:
                out.append(f"{self.table[constraint][var]}".rjust(CELL_WIDTH))

            print("|".join(out))






