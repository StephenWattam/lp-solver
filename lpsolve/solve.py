
from copy import copy
from . import ir

def solve(problem):
    """Solve the problem!"""

    print(f"Building initial tableau")
    tableau = Tableau(problem)
    tableau.summarise()

    itcount = 0
    while not tableau.optimal():
        itcount += 1
        print(f"Iteration: {itcount}")
        print(f"----------------")

        var, constraint = tableau._find_pivot()
        tableau.pivot(var, constraint)

        tableau.summarise()

    return None












class Tableau:

    OBJECTIVE_KEY = "__obj__"
    CONSTANT_KEY  = "__const__"

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

            # Pop the constant on the end
            self.table[constraint][Tableau.CONSTANT_KEY] = constraint.constant
            if Tableau.CONSTANT_KEY not in self.table_columns:
                self.table_columns.append(Tableau.CONSTANT_KEY)

        # Add a row at the end for the objective
        self.table[Tableau.OBJECTIVE_KEY] = {}
        for var in problem.symbols.table.values():
            self.table[Tableau.OBJECTIVE_KEY][var] = problem.objective.find_coefficient_for_variable(var, default=0)
        self.table[Tableau.OBJECTIVE_KEY][Tableau.CONSTANT_KEY] = 0

    def optimal(self):
        """Compute optimality by checking the final (objective function)
        row for any values below zero.

        """

        for var in self.table_columns:
            value = self.table[Tableau.OBJECTIVE_KEY][var]
            if value < 0:
                return False

        return True

    def _find_pivot(self):

        smallest_objective_value = 0
        pivot_var = None
        for var, val in self.table[Tableau.OBJECTIVE_KEY].items():
            if val is not None and val < smallest_objective_value:
                smallest_objective_value = float(val)
                pivot_var = var
        print(f"Pivot var (col) in objective: {pivot_var} ({smallest_objective_value})")

        # Find indicator by dividing by constant
        pivot_val = None
        lowest_val = None
        pivot_constraint = None
        for key in self.table.keys():
            if not isinstance(key, str):
                val = self.table[key][Tableau.CONSTANT_KEY] / self.table[key][pivot_var]
                # print(f" ==> {self.table[key][Tableau.CONSTANT_KEY]} / {self.table[key][pivot_var]} = {val}")
                if lowest_val is None or (val < lowest_val and val > 0):
                    lowest_val       = val
                    pivot_constraint = key
                    pivot_val        = self.table[key][pivot_var]
        print(f"Pivot constraint (row) in objective: {pivot_constraint.name} ({pivot_val})")

        return (pivot_var, pivot_constraint)


    def pivot(self, pivot_var, pivot_constraint):
        print(f"Pivoting around row [{pivot_constraint}], col [{pivot_var}] (value: {self.table[pivot_constraint][pivot_var]})")

        new_table = self._copy_table_vals(self.table)

        # Create pivot row with unit values
        for var in self.table_columns:
            new_table[pivot_constraint][var] = self.table[pivot_constraint][var] * (1.0 / self.table[pivot_constraint][pivot_var])

        # Populate column in new table with zeroes
        for constraint in self.table.keys():
            if constraint != pivot_constraint:
                new_table[constraint][pivot_var] = 0

        # Populate other rows
        for constraint in self.table.keys():
            for var in self.table_columns:
                if constraint != pivot_constraint and var != pivot_var:      # Avoid pivot row and pivot column

                    neg_val_in_old_tab_pivot_col = -1 * self.table[constraint][pivot_var]
                    val_in_new_tab_pivot_row     = new_table[pivot_constraint][var]
                    old_tab_val                  = self.table[constraint][var]

                    new_val = neg_val_in_old_tab_pivot_col * val_in_new_tab_pivot_row + old_tab_val
                    new_table[constraint][var] = new_val
                    print(f"[{isinstance(constraint, str) or constraint.name}][{isinstance(var, str) or var.name}] --> {neg_val_in_old_tab_pivot_col} * {val_in_new_tab_pivot_row} + {old_tab_val} = {new_val}")

        # Mutate self
        self.table = new_table


    def _copy_table_vals(self, table):
        """A mix of shallow and deep copy that retains keys but copies values and structure"""

        new_table = {}
        for k1, v1 in table.items():
            new_table[k1] = {}
            for k2, v2 in v1.items():
                new_table[k1][k2] = copy(v2)

        return new_table



    def summarise(self):

        CELL_WIDTH = 20

        # Start by printing the var names
        out = ["expression".rjust(CELL_WIDTH)]
        for var in self.table_columns:
            if isinstance(var, str):
                out.append(var.rjust(CELL_WIDTH))
            else:
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






