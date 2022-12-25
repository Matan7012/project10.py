"""
This file is part of nand2tetris, as taught in The Hebrew University, and
was written by Aviv Yaish. It is an extension to the specifications given
[here](https://www.nand2tetris.org) (Shimon Schocken and Noam Nisan, 2017),
as allowed by the Creative Common Attribution-NonCommercial-ShareAlike 3.0
Unported [License](https://creativecommons.org/licenses/by-nc-sa/3.0/).
"""
import typing
import JackTokenizer


class CompilationEngine:
    """Gets input from a JackTokenizer and emits its parsed structure into an
    output stream.
    """

    def __init__(self, input_stream: "JackTokenizer", output_stream) -> None:
        """
        Creates a new compilation engine with the given input and output. The
        next routine called must be compileClass()
        :param input_stream: The input stream.
        :param output_stream: The output stream.
        """
        # Your code goes here!
        # Note that you can write to output_stream like so:
        self.output_stream = output_stream
        self.jacktokenizer = input_stream
        self.classnames = []
        # output_stream.write("Hello world! \n")
        while self.jacktokenizer.has_more_tokens():
            token_type = self.jacktokenizer.token_type()
            if token_type == "KEYWORD":
                keyword = self.jacktokenizer.keyword()
                if keyword == 'CLASS':
                    self.compile_class()
                elif keyword == 'STATIC' or 'FIELD':
                    self.compile_class_var_dec()
                elif keyword in ['CONSTRUCTOR', 'FUNCTION', 'METHOD']:
                    self.compile_subroutine()
                elif keyword == 'VAR':
                    self.compile_var_dec()
            print(self.jacktokenizer.has_more_tokens())
            self.jacktokenizer.advance() #MAYBE WITHOUT THIS

    def compile_class(self) -> None:
        """Compiles a complete class."""
        self.output_stream.write("<class>\n")

        self.write_keyword()
        self.write_identifier()
        self.write_symbol()
        while self.jacktokenizer.keyword() == "STATIC" or self.jacktokenizer.keyword() == "FIELD":
            self.compile_class_var_dec()
        while self.jacktokenizer.keyword() == "CONSTRUCTOR" or self.jacktokenizer.keyword() == "FUNCTION" \
                or self.jacktokenizer.keyword() == "METHOD":
            self.compile_subroutine()

        self.write_symbol()

        self.output_stream.write("</class>\n")

    def compile_class_var_dec(self) -> None:
        """Compiles a static declaration or a field declaration."""
        self.output_stream.write("<classVarDec>\n")

        self.write_keyword()
        self.write_type()
        self.write_identifier()

        while self.jacktokenizer.symbol() == ",":  # PROBLEMATIC WHILE - THE CODE GETS STUCK
            print(self.jacktokenizer.symbol())
            self.write_symbol()
            self.write_identifier()

        self.write_symbol()

        self.output_stream.write("</classVarDec>\n")

    def compile_subroutine(self) -> None:
        """
        Compiles a complete method, function, or constructor.
        You can assume that classes with constructors have at least one field,
        you will understand why this is necessary in project 11.
        """
        self.output_stream.write("<subroutineDec>\n")

        self.write_keyword()
        if self.jacktokenizer.keyword() == "VOID":
            self.write_keyword()
        else:
            self.write_type()

        self.write_identifier()

        self.write_symbol()

        self.compile_parameter_list()

        self.write_symbol()

        self.compile_subroutineBody()

        self.output_stream.write("</subroutineDec>\n")

    def compile_parameter_list(self) -> None:
        """Compiles a (possibly empty) parameter list, not including the 
        enclosing "()".
        """
        self.output_stream.write("<parameterList>\n")

        if self.jacktokenizer.token_type() == "KEYWORD":
            self.write_type()

            self.write_identifier()

            while self.jacktokenizer.symbol() != ")":
                self.write_symbol()
                self.write_type()
                self.write_identifier()

        self.output_stream.write("</parameterList>\n")

    def compile_subroutineBody(self):
        """ I added this so this is not need the open statements"""
        self.output_stream.write("<subroutineBody>\n")

        self.write_symbol()

        while self.jacktokenizer.keyword == "VOID":
            self.compile_var_dec()

        self.compile_statements()

        self.write_symbol()

        self.output_stream.write("</subroutineBody>\n")

    def compile_var_dec(self) -> None:
        """Compiles a var declaration."""
        # Your code goes here!
        self.output_stream.write("<varDec>\n")

        self.write_keyword()

        self.write_type()

        self.write_identifier()
        while self.jacktokenizer.symbol() != ";":
            self.write_symbol()
            self.write_identifier()

        self.write_symbol()
        self.output_stream.write("</varDec>\n")

    def compile_statements(self) -> None:
        """Compiles a sequence of statements, not including the enclosing 
        "{}".
        """

        self.output_stream.write("<statements>\n")
        while self.jacktokenizer.token_type() == "KEYWORD":
            if self.jacktokenizer.keyword() == "LET":
                self.compile_let()
            elif self.jacktokenizer.keyword() == "IF":
                self.compile_if()
            elif self.jacktokenizer.keyword() == "WHILE":
                self.compile_while()
            elif self.jacktokenizer.keyword() == "DO":
                self.compile_do()
            elif self.jacktokenizer.keyword() == "RETURN":
                self.compile_return()

        self.output_stream.write("</statements>\n")

    def compile_do(self) -> None:
        """Compiles a do statement."""
        self.output_stream.write("<doStatement>\n")

        self.write_keyword()

        self.compile_subroutineCall()

        self.write_symbol()
        self.output_stream.write("</doStatement>\n")

    def compile_let(self) -> None:
        """Compiles a let statement."""
        # Your code goes here!
        self.output_stream.write("<letStatement>\n")
        self.write_keyword()
        self.write_identifier()
        if self.jacktokenizer.symbol() == "[":
            self.write_symbol()
            self.compile_expression()
            self.write_symbol()

        self.write_symbol()
        self.compile_expression()
        self.write_symbol()

        self.output_stream.write("</letStatement>\n")

    def compile_while(self) -> None:
        """Compiles a while statement."""
        # Your code goes here!
        self.output_stream.write("<whileStatement>\n")

        self.write_keyword()
        self.write_symbol()
        self.compile_expression()
        self.write_symbol()
        self.write_symbol()
        self.compile_statements()
        self.write_symbol()

        self.output_stream.write("</whileStatement>\n")

    def compile_return(self) -> None:
        """Compiles a return statement."""
        self.output_stream.write("<returnStatement>\n")
        self.write_keyword()
        if self.jacktokenizer.token_type() != "SYMBOL":
            self.compile_expression()
        elif self.jacktokenizer.symbol() in ["(", "-", "~", '^', '#']:
            self.compile_expression()
        self.write_symbol()
        self.output_stream.write("</returnStatement>\n")

    def compile_if(self) -> None:
        """Compiles a if statement, possibly with a trailing else clause."""
        # Your code goes here!

        self.output_stream.write("<ifStatement>\n")
        self.write_keyword()
        self.write_symbol()
        self.compile_expression()
        self.write_symbol()
        self.write_symbol()
        self.compile_statements()
        self.write_symbol()

        if self.jacktokenizer.keyword() == "ELSE":
            self.write_keyword()
            self.write_symbol()
            self.compile_statements()
            self.write_symbol()

        self.output_stream.write("</ifStatement>\n")

    def compile_expression(self) -> None:
        """Compiles an expression."""
        self.output_stream.write("<expression>\n")

        self.compile_term()
        op = ['+', '-', '*', '/', '&', '|', '<', '>', '=']
        while (self.jacktokenizer.token_type() == "SYMBOL") and \
                (self.jacktokenizer.symbol() in op):
            self.write_symbol()
            self.compile_term()
        self.output_stream.write("</expression>\n")

    def compile_term(self) -> None:
        """Compiles a term. 
        This routine is faced with a slight difficulty when
        trying to decide between some of the alternative parsing rules.
        Specifically, if the current token is an identifier, the routing must
        distinguish between a variable, an array entry, and a subroutine call.
        A single look-ahead token, which may be one of "[", "(", or "." suffices
        to distinguish between the three possibilities. Any other token is not
        part of this term and should not be advanced over.
        """
        # Your code goes here!
        if self.jacktokenizer.token_type() == "INT_CONST":
            self.write_integerConstant()
        elif self.jacktokenizer.token_type() == "STRING_CONST":
            self.write_stringConstant()
        elif self.jacktokenizer.token_type() == "KEYWORD":
            self.write_keyword()
        elif self.jacktokenizer.token_type() == "SYMBOL":
            if self.jacktokenizer.symbol() == "(":
                self.write_symbol()
                self.compile_expression()
                self.write_symbol()
            elif self.jacktokenizer.symbol() in ['-', '~', '^', '#']:
                self.write_symbol()
                self.compile_term()  # recursive?
        elif self.jacktokenizer.token_type() == "IDENTIFIER":
            self.write_identifier()
            if self.jacktokenizer.symbol() == "[":
                self.write_symbol()
                self.compile_expression()
                self.write_symbol()
            elif self.jacktokenizer.symbol() == "(":
                self.write_symbol()
                self.compile_expression_list()
                self.write_symbol()
            elif self.jacktokenizer.symbol() == ".":
                self.write_symbol()
                self.write_identifier()
                self.write_symbol()
                self.compile_expression_list()
                self.write_symbol()

    def compile_subroutineCall(self):
        """ Compiles a subroutineCall"""

        self.write_identifier()
        if self.jacktokenizer.symbol() == "(":
            self.write_symbol()
            self.compile_expression_list()
            self.write_symbol()
        else:
            self.write_symbol()
            self.write_identifier()
            self.write_symbol()
            self.compile_expression_list()
            self.write_symbol()

    def compile_expression_list(self) -> None:
        """Compiles a (possibly empty) comma-separated list of expressions."""
        # Your code goes here!
        if self.jacktokenizer.token_type() != "SYMBOL":
            self.compile_expression()
            while (self.jacktokenizer.token_type() == "SYMBOL") and (self.jacktokenizer.symbol == ","):
                self.write_symbol()
                self.compile_expression()
        elif self.jacktokenizer.symbol() in ["(", "-", "~", '^', '#']:
            self.compile_expression()
            while (self.jacktokenizer.token_type() == "SYMBOL") and (self.jacktokenizer.symbol == ","):
                self.write_symbol()
                self.compile_expression()

    # the most elementary functions
    def write_keyword(self):
        self.output_stream.write("<keyword>" +
                                 self.jacktokenizer.keyword() + "</keyword>\n")
        self.jacktokenizer.advance()

    def write_identifier(self):
        self.output_stream.write("<identifier>" +
                                 self.jacktokenizer.identifier() + "</identifier>\n")
        self.jacktokenizer.advance()

    def write_symbol(self):
        self.output_stream.write("<symbol>" +
                                 self.jacktokenizer.symbol() + "</symbol>\n")
        self.jacktokenizer.advance()

    def write_integerConstant(self):
        self.output_stream.write("<integerConstant>" +
                                 self.jacktokenizer.int_val() + "</integerConstant>\n")
        self.jacktokenizer.advance()

    def write_stringConstant(self):
        self.output_stream.write("<stringConstant>" +
                                 self.jacktokenizer.string_val() + "</stringConstant>\n")
        self.jacktokenizer.advance()

    def write_type(self):
        if self.jacktokenizer.token_type() == "IDENTIFIER":
            self.write_identifier()
        else:
            self.write_keyword()
        self.jacktokenizer.advance()
