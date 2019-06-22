
import re



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



class Expression:

    def __init__(self, tokens):
        self.tokens = tokens
        self.name = ""


class Section:

    def __init__(self):
        self.buf = Buffer("")
        self.tokens = []

    def append_raw(self, string):
        self.buf.string += f"\n{string}"

    def tokenise(self):

        IDENTIFIER_PATTERN                  = "[AaBbCcDdFfGgHhIiJjKkLlMmNnOoPpQqRrSsTtUuVvWwXxYyZz\!\"#$%&()/,;?@_`'{}|~][a-zA-Z0-9\!\"#$%&()/,;?@_`'{}|~.]*"
        NAME_SEPARATOR_PATTERN              = "\s*:\s*"
        LINE_SEPARATOR_PATTERN              = "\n"
        NUMBER_PATTERN                      = "[0-9]+(.[0-9]+)?(e[0-9]+(\.[0-9]+)?)?"
        UNARY_NEGATION_PATTERN              = "-"
        WHITESPACE_PERMITTED_IN_EXPRESSIONS = "\s+"
        RELATION_PATTERN                    = "(<|<=|=<|>|>=|=>|=)"
        OPERATOR_PATTERN                    = "(\+|-)"

        tokens = []
        while not self.buf.empty():
            if self.buf.peek(NUMBER_PATTERN):
                tokens.append( ("number", self.buf.consume(NUMBER_PATTERN)) )
            elif self.buf.consume(UNARY_NEGATION_PATTERN):
                tokens.append( ("negate", "-") )
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
        print("Tokens:")
        for n, tks in phrases.items():
            print(f"{n}: {tks}")
        # for i, tok in enumerate(new_tokens):
        #     print(f"[{i}] {tok}")
        self.tokens = phrases

    def _parse_phrases(self):
        expressions = []


    def parse(self):
        print("STUB: Section#parse in parser.py")
        pass

class Objective(Section):

    def parse(self):
        print(f"<objective>")

        # TODO: put the value somewhere.
        #return Objective(expression)

class Constraints(Section):

    def parse(self):
        pass

class Bounds(Section):
    pass

class IntVars(Section):
    pass

class BinVars(Section):
    pass



def parse_file(filename):
    """Parse a LP file with a given filename, returning an
    intermediate representation that is of use for further solving."""

    with open(filename) as fin:
        return parse_string(fin.read())

def parse_string(string):
    """Parse an LP-format string, returning an intermediate representation
    that is of use for further solver stages"""

    string = _strip_comments(string)

    sections = _split_sections(string)
    print(f" -> Sections: {sections}")

    # Parse each section
    for section in sections:
        section.tokenise()
        section.parse()

    return None

def error(msg):
    print(msg)
    raise ValueError(msg)

# Comments are a backslash to comment until end of line,
# or a blank line entirely
COMMENT_PATTERN = "(\\\\.*$|^$)"
def _strip_comments(string):

    string = re.sub(COMMENT_PATTERN, "", string, flags=re.MULTILINE)
    return string


SECTION_PATTERN_OBJECTIVE   = "m(ax|in)(imize|imum)?\s*"
SECTION_PATTERN_CONSTRAINTS = "(subject to|such that|st|s\\.t\\.)\s*"
SECTION_PATTERN_BOUNDS      = "bounds?\s*"
SECTION_PATTERN_INT_VARS    = "gen(eral|erals)?\s*"
SECTION_PATTERN_BIN_VARS    = "bin(aries|ary)?\s*"
END_PATTERN                 = "end\s*?"
def _split_sections(string):

    lines = string.splitlines()
    sections = []

    section = None
    for line in lines:

        new_section = None
        if re.match(SECTION_PATTERN_OBJECTIVE, line, flags=re.I):
            new_section = Objective()
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
        else:
            if section is None:
                error(f"Error --- non-section statement outside of section: {line}")
            # Add line to section
            section.append_raw(line)

        # Do this here to mininmise repetitition above
        if new_section:
            sections.append(section)
            section = new_section

    if len(sections) == 0:
        error("No sections found in document.")

    return sections[1:]








