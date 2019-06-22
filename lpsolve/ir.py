



class LPProblem:

    def __init__(self):

        self.symbols     = SymbolTable()
        self.objective   = None
        self.constraints = []

    def add_constraint(self, constraint):
        self.constraints.append(constraint)

    def set_objective(self, expression):
        self.objective = expression






class Variable:
    """Represents a variable in the LP problem"""

    def __init__(self, identifier):
        self.identifier = identifier

    def __str__(self):
        print(f"<v:{self.lower} <= {self.identifier} <= {self.upper} | b?{self.binary}>")

    def set_binary(self, binary):
        self.binary = binary

    def set_lower_bound(self, lower_bound="0", strict=False):
        self.lower_bound = lower_bound
        self.lower_strict = strict

    def set_upper_bound(self, upper_bound="+infinity", strict=False):
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


class Expression:

    def __init__(self, name, tokens):
        self.tokens = tokens
        self.name   = name

        # TODO: list variables in use, etc.


class Constraint:

    def __init__(self, name, expression, relation, constant):

        self.name       = name
        self.expression = expression
        self.relation   = relation
        self.constant   = constant

