

from . import ir

def to_standard_form(problem):
    """Convert a problem to standard form, suitable for solving using the simplex method

    Standard form involves:
     - Maximise-only optimisation target
     - All linear constraints are of the form 'expression <= constant`
     - All variables are non-negative
    """

    # Invert objective if suitable
    if problem.maximise:
        print("Converting minimise objective into maximise")
        invert_objective(problem)

    # Convert objective to equality.  Similar to adding slack variables.
    convert_objective_to_equality(problem)

    # Invert constraints to suit
    ensure_upper_bounded_constraints(problem)

    # Convert constraints to equations by inserting slack variables
    insert_slack_variables(problem)

    # Add constraints to ensure all variables are GTE 0
    ensure_variables_gte_zero(problem)

    # TODO: lots more preoptimisation!

    return problem





def invert_objective(problem):
    """Convert a minimise objective to a maximise objective and vice versa.

    Simply multiplies the objective expression by -1"""

    problem.objective.multiply(-1)
    problem.maximise = not problem.maximise


def convert_objective_to_equality(problem):

    new_objective_terms = problem.objective.terms + [(1.0, problem.symbols.new_variable(ir.OBJECTIVE_VARIABLE_NAME, True))]
    problem.objective = ir.Equation(problem, f"__obj__", new_objective_terms, 0.0)


def ensure_upper_bounded_constraints(problem):
    """Converts all constraints to be of the form expression <= constant"""

    for name, constraint in problem.constraints.items():
        if isinstance(constraint, ir.Inequality) and constraint.greater_than:
            constraint.invert()



def insert_slack_variables(problem):
    """Insert slack variables to convert constraints to equalities"""

    # Convert each constraint
    new_constraints = {}
    for name, constraint in problem.constraints.items():
        if isinstance(constraint, ir.Inequality):
            new_terms = constraint.expression.terms + [(1.0, problem.symbols.new_variable(f"_s_{name}", True))]
            new_constraints[name] = ir.Equation(problem, f"_c_{name}", new_terms, constraint.constant)
        else:
            new_constraints[name] = constraint

    problem.constraints = new_constraints



def ensure_variables_gte_zero(problem):
    """Inserts constraints to ensure all variables >= 0"""

    # FIXME: I'm not sure this is correct mathematically.
    # TODO: Ensure these bounds are enforced
    for name, var in problem.symbols.table.items():
        var.set_lower_bound(0, strict=False)

