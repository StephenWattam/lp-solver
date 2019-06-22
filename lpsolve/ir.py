



class LPProblem:

    def __init__(self):

        self.symbols     = SymbolTable()
        self.objective   = None
        self.constraints = {}

    def add_constraint(self, name, constraint):
        self.constraints[name] = constraint

    def set_objective(self, expression, mode):
        self.objective = expression
        self.mode      = mode

    def get_expression(self, name, terms):

        expr = Expression(self, name, terms)
        return expr

    def get_equation(self, name, terms, constant):

        equat = Equation(self, name, terms, constant)
        return equat

    def get_inequality(self, name, terms, greater_than, strict, constant):

        inequal = Inequality(self, name, terms, greater_than, strict, constant)
        return inequal

    def summarise(self):
        print(f"Objective function: {self.mode}imise {self.objective}")
        print(f"Subject to:")
        for name, c in self.constraints.items():
            print(f"  {name}: {c}")
        print("Across variables:")
        for name, var in self.symbols.table.items():
            print(f"  {name}: {var}")




class Variable:
    """Represents a variable in the LP problem"""

    def __init__(self, name):
        self.name = name
        self.set_upper_bound()
        self.set_lower_bound()
        self.set_binary(False)

    def __str__(self):
        lower_bound = "<" if self.lower_strict else "<="
        upper_bound = "<" if self.upper_strict else "<="
        return f"{self.lower_bound} {lower_bound} {self.name} {upper_bound} {self.upper_bound} {'(binary)' if self.binary else ''}"

    def set_binary(self, binary):
        self.binary = binary

    def set_lower_bound(self, lower_bound=0.0, strict=False):
        self.lower_bound = lower_bound
        self.lower_strict = strict

    def set_upper_bound(self, upper_bound=float("+infinity"), strict=False):
        self.upper_bound = upper_bound
        self.upper_strict = strict

    def fixed_value(self):
        return self.upper_bound == self.lower_bound and not self.upper_strict and not self.lower_strict






class SymbolTable:

    def __init__(self):

        self.table = {}


    def get(self, name, create=False):

        if name in self.table:
            return self.table[name]
        else:
            if create:
                self.new_variable(name)
                return self.get(name)


    def new_variable(self, name):

        var              = Variable(name)
        self.table[name] = var

        return var

    def __str__(self):
        string = ""
        for k, v in self.table.items():
            string += f"{k}: {v}\n"

        return string


class Expression:

    def __init__(self, problem, name, terms):

        self.symbols = problem.symbols
        self.terms = terms
        self.name   = name

    def __str__(self):
        terms_as_string = " + ".join([f"{t[0] if t[0] != 1 else ''}{t[1].name}" for t in self.terms])
        return f"{terms_as_string}"

    def multiply(self, coefficient):
        new_terms = []
        for term in self.terms:
            new_terms.append( (term[0] * coefficient, term[1]) )

        self.terms = new_terms

    def find_coefficient_for_variable(self, variable, default=None):
        for coefficient, var in self.terms:
            if var == variable:
                return coefficient
        return default


class Inequality:

    def __init__(self, problem, name, terms, greater_than, strict, constant):
        self.name         = name
        self.expression   = Expression(problem, name, terms)
        self.greater_than = greater_than # Bool
        self.strict       = strict       # Bool
        self.constant     = constant

    def __str__(self):
        relation = ">" if self.greater_than else "<"
        relation = f"{relation}=" if not self.strict else relation
        return f"{self.expression} {relation} {self.constant}"

    def invert(self):
        """Convert an x < y constraint to a -x > y constraint"""

        self.expression.multiply(-1)
        self.constant    *= -1
        self.greater_than = not self.greater_than

class Equation:

    def __init__(self, problem, name, terms, constant):
        self.name       = name
        self.expression = Expression(problem, name, terms)
        self.constant   = constant

    def __str__(self):
        return f"{self.expression} = {self.constant}"


class Constraint:

    def __init__(self, name, expression, relation, constant):

        self.name       = name
        self.expression = expression
        self.relation   = relation
        self.constant   = constant

