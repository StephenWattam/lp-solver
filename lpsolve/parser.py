
import re
from . import ir

class Buffer:

    def __init__(self, string):
        self.string = string
        self.line = 0
        self.char = 0

    def peek(self, pattern, flags=re.MULTILINE):
        if re.match(pattern, self.string, flags=flags):
            return True
        return False

    def consume(self, pattern, flags=re.MULTILINE):

        m = re.match(pattern, self.string, flags=flags)
        if m is None:
            return None

        # print(f"Matched \"{m.group(0)}\" =~ {pattern}")
        self.string = self.string[len(m.group(0)):]
        self.line += len(re.findall("\n", m.group(0)) or "")
        if re.search("\n", m.group(0)):
            self.char += len(re.search("\n.*$", m.group(0)).group(0))
        else:
            self.char += len(m.group(0))

        return m.group(0)

    def report(self):
        return f"line {self.line}, char {self.char}"

    def empty(self):
        return len(self.string) == 0




class Section:

    def __init__(self):
        self.buf = Buffer("")
        self.tokens = {}

    def append_raw(self, string):
        self.buf.string += f"\n{string}"

    def tokenise(self):

        IDENTIFIER_PATTERN                  = "[AaBbCcDdFfGgHhIiJjKkLlMmNnOoPpQqRrSsTtUuVvWwXxYyZz\!\"#$%&()/,;?@_`'{}|~][a-zA-Z0-9\!\"#$%&()/,;?@_`'{}|~.]*"
        NAME_SEPARATOR_PATTERN              = "\s*:\s*"
        LINE_SEPARATOR_PATTERN              = "\n"
        NUMBER_PATTERN                      = "([0-9]+(.[0-9]+)?(e[0-9]+(\.[0-9]+)?)?|(-|\+)inf(inity)?)"
        WHITESPACE_PERMITTED_IN_EXPRESSIONS = "\s+"
        RELATION_PATTERN                    = "(<=|=<|>=|=>|=|<|>)"
        OPERATOR_PATTERN                    = "(\+|-)"
        VARIABLE_FREE_PATTERN               = "free"

        tokens = []
        while not self.buf.empty():
            if self.buf.peek(NUMBER_PATTERN):
                tokens.append( ("number", self.buf.consume(NUMBER_PATTERN)) )
            elif self.buf.peek(VARIABLE_FREE_PATTERN):
                tokens.append( ("free", self.buf.consume(VARIABLE_FREE_PATTERN)) )
            elif self.buf.peek(IDENTIFIER_PATTERN):
                tokens.append( ("identifier", self.buf.consume(IDENTIFIER_PATTERN)) )
            elif self.buf.peek(OPERATOR_PATTERN):
                tokens.append( ("operator", self.buf.consume(OPERATOR_PATTERN)) )
            elif self.buf.peek(RELATION_PATTERN):
                tokens.append( ("relation", self.buf.consume(RELATION_PATTERN)) )
            elif self.buf.consume(LINE_SEPARATOR_PATTERN):
                tokens.append( ("newline", "\n") )
            elif self.buf.consume(NAME_SEPARATOR_PATTERN):
                tokens.append( ("name_separator", ":") )
            elif self.buf.consume(WHITESPACE_PERMITTED_IN_EXPRESSIONS):
                pass
            else:
                error(f"Unknown token at {self.buf.report()}: {self.buf.string[:10]}...")


        # Now simplify tokens to handle known common parsing cases.
        # Probably not really the place but w/ee

        # 1) if an identifier is surrounded by a name separator and a newline then it is an expression label
        new_tokens = []
        for i, token in enumerate(tokens):

            # Leading newline is a product of the tokeniser.
            if i == 0 and token[0] == "newline":
                pass

            # Case where an identifier is used as an expression label
            elif token[0] == "identifier" and i > 0 and tokens[i-1][0] == "newline" and i < len(tokens)-1 and tokens[i+1][0] == "name_separator":
                new_tokens.append( ("phrase_label", token[1]) )

            # We have used the name separator character above to identify a label, so can discard this token
            elif token[0] == "name_separator":
                pass

            # If we have variable name followed by "free" then this variable needs omitting and we'll put +-inf on the token
            # list instead to ensure a consistent format
            elif token[0] == "identifier" and i < len(tokens)-1 and tokens[i+1][0] == "free":
                new_tokens.append( ("number", float("-infinity")) )
                new_tokens.append( ("relation", "<=") )
                new_tokens.append( token )
                new_tokens.append( ("relation", "<=") )
                new_tokens.append( ("number", float("+infinity")) )
            # And the case for the 'free' marker to make this work:
            elif token[0] == "free":
                pass

            # Case where the next token after the newline is an operator or relation, meaning the expression
            # continues on the next line
            elif token[0] == "newline" and i < len(tokens)-1 and (tokens[i+1][0] == "relation" or tokens[i+1][0] == "operator"):
                pass

            # Case where the current token is an operator but the next one is a newline, so the expression continues
            # on the next line
            elif token[0] == "newline" and i > 0 and (tokens[i-1][0] == "relation" or tokens[i-1][0] == "operator"):
                pass

            # Case where this line ends on an identifier and the next line begins with something other than a relation or operator,
            # meaning this is the end of an expression
            elif token[0] == "newline" and i > 0 and tokens[i-1][0] != "relation" and tokens[i-1][0] != "operator" and i < len(tokens)-1 and (tokens[i+1][0] != "operator" and tokens[i+1][0] != "relation"):
                new_tokens.append( ("end_phrase", "\n") )

            elif token[0] == "number":
                new_tokens.append( ("number", float(token[1])) )
            else:
                new_tokens.append(token)

        # Let's always trigger this to make life easier.
        if len(new_tokens) > 0:
            new_tokens.append( ("end_phrase", "EOF") )

        # Now let's group these into phrases
        phrases = {}
        phrase_name = None
        phrase_tokens = []
        for i, token in enumerate(new_tokens):
            if token[0] == "phrase_label":
                phrase_name = token[1]
            elif token[0] == "end_phrase":
                if phrase_name is None:
                    phrase_name = f"rule_{len(phrases)+1}"
                phrases[phrase_name] = phrase_tokens
                phrase_tokens = []
                phrase_name = None
            else:
                phrase_tokens.append(token)

        # And show the people at home what we've done
        # print("Tokens:")
        # for n, tks in phrases.items():
        #     print(f"{n}: {tks}")
        # for i, tok in enumerate(new_tokens):
        #     print(f"[{i}] {tok}")
        self.tokens = phrases

    def _token_expression_to_terms(self, problem, name, tokens):
        """Converts parsed tokens to algorithmic terms.

        Necessary anywhere where expressions are parsed."""

        # Parse tokens into another IR that is more suited to computation
        terms = []
        coefficient = 1.0
        negative = False
        for token in tokens:
            if token[0] == "number":
                coefficient = float(token[1])
            elif token[0] == "operator" and token[1] == "-":
                negative = not negative
            elif token[0] == "identifier":
                var = problem.symbols.get(token[1], create=True)
                terms.append( (coefficient * (-1 if negative else 1), var) )
                coefficient = 1
                negative = False
            elif token[0] == "operator" and token[1] == "+":
                pass    # Ignore
            else:
                error(f"Unexpected term in expression with name {name}: {token[1]}")

        return terms


    def build_ir(self, problem):
        print("STUB: Section#parse in parser.py")
        pass






class Objective(Section):

    def __init__(self, mode):
        super().__init__()
        self.mode = mode

    def build_ir(self, problem):
        if len(self.tokens) > 1:
            error("Too many objective expressions -- this library only supports one right now")

        # Build an expression object out of the token list
        #
        # TODO: I'm not sure how I want to encode this yet, so
        #       will worry about that later.
        name, tokens = list(self.tokens.items())[0]

        terms = self._token_expression_to_terms(problem, name, tokens)

        # print(f"{problem.get_expression(name, terms)}")
        problem.set_objective(problem.get_expression(name, terms), self.mode)


class Constraints(Section):

    def build_ir(self, problem):
        # Add a list of constraints
        payload = []
        for name, tokens in self.tokens.items():

            # Each constraint should be composed of an expression, a relation,
            # and a number, e.g.:
            #
            # - x1 + x2 + x3 + 10 x4 <= 20


            if len(tokens) < 3:
                error(f"Not enough tokens to form a meaningful constraint, name {name}.  Token list: {tokens}")
            # We expect the RHS to be a number, so this is the place to patch unary negation
            if tokens[-1][0] == "number" and tokens[-2][0] == "operator" and tokens[-2][1] == "-":
                tokens = tokens[:-2] + [("number", -1*float(tokens[-1][1]))]
            if tokens[-1][0] != "number":
                error(f"Expected number (coefficient) on RHS of constraint with name {name} but found token: {tokens[-1]}")
            if tokens[-2][0] != "relation":
                error(f"Expected a relation as the penultimate token in constraint with name {name}, but found token {tokens[-2]}")


            relation = tokens[-2][1]    # TODO: represent more usefully
            constant = tokens[-1][1]    # TODO: parse


            terms = self._token_expression_to_terms(problem, name, tokens[:-2])


            # If the relation is an equals, get an equation
            if relation == "=":
                constraint = problem.get_equation(f"constraint_eq_{name}", terms, constant)
            else:
                constraint = problem.get_inequality(f"constraint_ineq_{name}", terms,
                        True if relation in [">", ">=", "=>"] else False, 
                        False if "=" in relation else True, constant)

            problem.add_constraint(name, constraint)

class Bounds(Section):


    def _set_variable_bounds(self, problem, identifier, relation, number):
        """Sets variable bounds on the assumption that the statement is in the form:

        var rel number, e.g.
        x5 < 4.5
        y > 64
        buses = 10
        """

        var = problem.symbols.get(identifier, create=True)

        if relation in [">", ">=", "=>"]:
            var.set_lower_bound(number, strict=False if "=" in relation else True)
        if relation in ["<", "<=", "=<"]:
            var.set_upper_bound(number, strict=False if "=" in relation else True)
        if relation in "=":
            var.set_lower_bound(number, strict=False)
            var.set_upper_bound(number, strict=False)


    def build_ir(self, problem):

        RELATION_INVERSION = {">": "<",
                              ">=": "<=",
                              "=>": "<=",
                              "=": "=",
                              "<": ">",
                              "<=": ">=",
                              "=<": ">="}

        payload = []
        for name, tokens in self.tokens.items():

            # Case where bounds are given as a single, upper or lower:
            #
            # x5 >= 3.4
            # 4.6 <= x2
            #
            if len(tokens) == 3:
                if tokens[1][0] != "relation":
                    error(f"Bounds given with a single relation, yet that relation is not the middle token.  Bound name: {name}, token list: {tokens}")

                if not ((tokens[0][0] == "identifier" and tokens[2][0] == "number") or (tokens[0][0] == "number" and tokens[2][0] == "identifier")):
                    error(f"Expected an identifier and number as bounds but found something else.  Bound name: {name}, token list: {tokens}")


                # Normalise this to have the identifier on the LHS
                if tokens[0][0] == "identifier":
                    identifier = tokens[0][1]
                    relation = tokens[1][1]
                    number = float(tokens[2][1])
                elif tokens[0][0] == "number":
                    identifier = tokens[2][1]
                    relation = RELATION_INVERSION[tokens[1][1]]
                    number = float(tokens[0][1])


                # We are now of the format:
                #
                # identifier relation number, e.g.
                # x5 > 6
                # x2 <= 4
                #
                self._set_variable_bounds(problem, identifier, relation, number)


            # Case where bounds as given as number relation identifier relation number
            #
            #  0 <= x1 <= 40
            #  2 <= x4 <= 3
            if len(tokens) == 5:
                if tokens[0][0] != tokens[4][0] or tokens[1][0] != tokens[3][0] or tokens[2][0] != "identifier" or tokens[0][0] != "number" or tokens[1][0] != "relation":
                    error(f"Expected <number, relation, identifier, relation, number> but got something else.  Bound name: {name}, token list: {tokens}")

                lower          = float(tokens[0][1])
                lower_relation = tokens[1][1]
                identifier     = tokens[2][1]
                upper_relation = tokens[3][1]
                upper          = float(tokens[4][1])

                # For us to add these in the same format we need to normalise them to the same format
                # as the single-bound case above, which means identifier-relation-number.
                self._set_variable_bounds(problem, identifier, RELATION_INVERSION[lower_relation], lower)
                self._set_variable_bounds(problem, identifier, upper_relation, upper)


class IntVars(Section):

    def build_ir(self, problem):
        for name, tokens in self.tokens.items():
            if len(tokens) > 1 and tokens[0][0] != "identifier":
                error("Expected only a single token identifier to set to general use.  Rule name: {name}, token list: {tokens}")

            var = problem.symbols.get(tokens[0][1], create=True)
            var.set_binary(False)


class BinVars(Section):

    def build_ir(self, problem):
        for name, tokens in self.tokens.items():
            if len(tokens) > 1 and tokens[0][0] != "identifier":
                error("Expected only a single token identifier to set to binary mode.  Rule name: {name}, token list: {tokens}")

            var = problem.symbols.get(tokens[0][1], create=True)
            var.set_binary(True)










def parse_file(filename):
    """Parse a LP file with a given filename, returning an
    intermediate representation that is of use for further solving."""

    with open(filename) as fin:
        return parse_string(fin.read())

def parse_string(string):
    """Parse an LP-format string, returning an intermediate representation
    that is of use for further solver stages"""

    problem = ir.LPProblem()
    string = _strip_comments(string)
    sections = _split_sections(string)

    # Parse each section
    for section in sections:
        section.tokenise()
        section.build_ir(problem)

    return problem

def error(msg):
    print(msg)
    raise ValueError(msg)

# Comments are a backslash to comment until end of line,
# or a blank line entirely
COMMENT_PATTERN = "(\\\\.*$|^$)"
def _strip_comments(string):

    string = re.sub(COMMENT_PATTERN, "", string, flags=re.MULTILINE)
    return string


SECTION_PATTERN_MAX_OBJECTIVE   = "max(imize|imum)?\s*"
SECTION_PATTERN_MIN_OBJECTIVE   = "min(imize|imum)?\s*"
SECTION_PATTERN_CONSTRAINTS = "(subject to|such that|st|s\\.t\\.)\s*"
SECTION_PATTERN_BOUNDS      = "bounds?\s*"
SECTION_PATTERN_INT_VARS    = "gen(eral|erals)?\s*"
SECTION_PATTERN_BIN_VARS    = "bin(aries|ary)?\s*"
END_PATTERN                 = "end\s*?"
def _split_sections(string):

    lines = string.splitlines()
    sections = []

    section = None
    for i, line in enumerate(lines):

        new_section = None
        if re.match(SECTION_PATTERN_MAX_OBJECTIVE, line, flags=re.I):
            new_section = Objective("max")
        elif re.match(SECTION_PATTERN_MIN_OBJECTIVE, line, flags=re.I):
            new_section = Objective("min")
        elif re.match(SECTION_PATTERN_CONSTRAINTS, line, flags=re.I):
            new_section = Constraints()
        elif re.match(SECTION_PATTERN_BOUNDS, line, flags=re.I):
            new_section = Bounds()
        elif re.match(SECTION_PATTERN_INT_VARS, line, flags=re.I):
            new_section = IntVars()
        elif re.match(SECTION_PATTERN_BIN_VARS, line, flags=re.I):
            new_section = BinVars()
        elif re.match(END_PATTERN, line, flags=re.I):
            pass    # Throw this one away
        elif re.match("^\s*$", line, flags=re.I):
            pass    # empty line
        else:
            if section is None:
                error(f"Error --- non-section statement outside of section: Line {i}, '{line}'")
            # Add line to section
            section.append_raw(line)

        # Do this here to mininmise repetitition above
        if new_section:
            sections.append(section)
            section = new_section

    # Catch the last section
    sections.append(section)

    if len(sections) == 0:
        error("No sections found in document.")

    return sections[1:]








