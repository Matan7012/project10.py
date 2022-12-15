"""
This file is part of nand2tetris, as taught in The Hebrew University, and
was written by Aviv Yaish. It is an extension to the specifications given
[here](https://www.nand2tetris.org) (Shimon Schocken and Noam Nisan, 2017),
as allowed by the Creative Common Attribution-NonCommercial-ShareAlike 3.0
Unported [License](https://creativecommons.org/licenses/by-nc-sa/3.0/).
"""
import typing
import re

SYMBOLS = {'{' , '}' , '(' , ')' , '[' , ']' , '.' , ',' , ';' , '+' ,
              '-' , '*' , '/' , '&' , '|' , '<' , '>' , '=' , '~' , '^' , '#'}
SYMBOL_REGEX = '{|}|\(|\)|\[|\]|\.|,|;|\+|-|\*|\/|&|\||<|>|=|~|\^|#'
KEYWORD_REGEX = 'class|constructor|function|method|field|static|var|int|char|boolean|void|true|false|null|this|let|do|if|else|while|return'

class JackTokenizer:
    """Removes all comments from the input stream and breaks it
    into Jack language tokens, as specified by the Jack grammar.
    
    # Jack Language Grammar

    A Jack file is a stream of characters. If the file represents a
    valid program, it can be tokenized into a stream of valid tokens. The
    tokens may be separated by an arbitrary number of whitespace characters, 
    and comments, which are ignored. There are three possible comment formats: 
    /* comment until closing */ , /** API comment until closing */ , and 
    // comment until the line’s end.

    - ‘xxx’: quotes are used for tokens that appear verbatim (‘terminals’).
    - xxx: regular typeface is used for names of language constructs 
           (‘non-terminals’).
    - (): parentheses are used for grouping of language constructs.
    - x | y: indicates that either x or y can appear.
    - x?: indicates that x appears 0 or 1 times.
    - x*: indicates that x appears 0 or more times.

    ## Lexical Elements

    The Jack language includes five types of terminal elements (tokens).

    - keyword: 'class' | 'constructor' | 'function' | 'method' | 'field' | 
               'static' | 'var' | 'int' | 'char' | 'boolean' | 'void' | 'true' |
               'false' | 'null' | 'this' | 'let' | 'do' | 'if' | 'else' | 
               'while' | 'return'
    - symbol: '{' | '}' | '(' | ')' | '[' | ']' | '.' | ',' | ';' | '+' | 
              '-' | '*' | '/' | '&' | '|' | '<' | '>' | '=' | '~' | '^' | '#'
    - integerConstant: A decimal number in the range 0-32767.
    - StringConstant: '"' A sequence of Unicode characters not including 
                      double quote or newline '"' "sdasdsadas"
    - identifier: A sequence of letters, digits, and underscore ('_') not 
                  starting with a digit. You can assume keywords cannot be
                  identifiers, so 'self' cannot be an identifier, etc'.

    ## Program Structure

    A Jack program is a collection of classes, each appearing in a separate 
    file. A compilation unit is a single class. A class is a sequence of tokens 
    structured according to the following context free syntax:
    
    - class: 'class' className '{' classVarDec* subroutineDec* '}'
    - classVarDec: ('static' | 'field') type varName (',' varName)* ';'
    - type: 'int' | 'char' | 'boolean' | className
    - subroutineDec: ('constructor' | 'function' | 'method') ('void' | type) 
    - subroutineName '(' parameterList ')' subroutineBody
    - parameterList: ((type varName) (',' type varName)*)?
    - subroutineBody: '{' varDec* statements '}'
    - varDec: 'var' type varName (',' varName)* ';'
    - className: identifier
    - subroutineName: identifier
    - varName: identifier

    ## Statements

    - statements: statement*
    - statement: letStatement | ifStatement | whileStatement | doStatement | 
                 returnStatement
    - letStatement: 'let' varName ('[' expression ']')? '=' expression ';'
    - ifStatement: 'if' '(' expression ')' '{' statements '}' ('else' '{' 
                   statements '}')?
    - whileStatement: 'while' '(' 'expression' ')' '{' statements '}'
    - doStatement: 'do' subroutineCall ';'
    - returnStatement: 'return' expression? ';'

    ## Expressions
    
    - expression: term (op term)*
    - term: integerConstant | stringConstant | keywordConstant | varName | 
            varName '['expression']' | subroutineCall | '(' expression ')' |
            unaryOp term
    - subroutineCall: subroutineName '(' expressionList ')' | (className | 
                      varName) '.' subroutineName '(' expressionList ')'
    - expressionList: (expression (',' expression)* )?
    - op: '+' | '-' | '*' | '/' | '&' | '|' | '<' | '>' | '='
    - unaryOp: '-' | '~' | '^' | '#'
    - keywordConstant: 'true' | 'false' | 'null' | 'this'
    
    Note that ^, # correspond to shiftleft and shiftright, respectively.
    """


    def __init__(self, input_stream: typing.TextIO) -> None:
        """Opens the input stream and gets ready to tokenize it.

        Args:
            input_stream (typing.TextIO): input stream.
        """
        # Your code goes here!
        # A good place to start is to read all the lines of the input:
        input_str = input_stream.read()
        input_str_no_comments = re.sub("\/\*[\s\S]*?\*\/|\/\/.*|\/\*\*[\s\S]*?\*\/",'',input_str) #replaces all the comments with empty space.
        input_str_clean = re.sub("(^\s*\n)|(\s+$)(^\s*\n)|(\s+$)/m","",input_str_no_comments) #removes the white spaces at the end of line
        # and removes the empty lines with a newline.
        self.input_lines = input_str_clean.splitlines()
        self.i = 0
        self.token_type_str = None
        self.word = None
        self.advance()
        pass

    def has_more_tokens(self) -> bool:
        """Do we have more tokens in the input?

        Returns:
            bool: True if there are more tokens, False otherwise.
        """
        if self.i < (len(self.input_lines)-1) or self.input_lines[self.i] != '':
            print(self.i)
            print(len(self.input_lines))
            return True
        # Your code goes here!
        return False

    def advance(self) -> None:
        """Gets the next token from the input and makes it the current token. 
        This method should be called if has_more_tokens() is true. 
        Initially there is no current token.
        """
        self.input_lines[self.i] = re.sub("^\s*", "", self.input_lines[self.i])
        while self.input_lines[self.i] == '':
            self.i += 1
            self.input_lines[self.i] = re.sub("^\s*", "", self.input_lines[self.i])

        # Handaling symbols
        if self.input_lines[self.i][0] in SYMBOLS:
            self.token_type_str = "SYMBOL"
            self.word = self.input_lines[self.i][0]
            self.input_lines[self.i] = self.input_lines[self.i][1:]
            return

        # Handaling keywords
        find_keyword_at_start_regex = r'^(' + KEYWORD_REGEX + r')(?=(' + SYMBOL_REGEX + r'|\s+))'
        keyword_at_start = re.search(find_keyword_at_start_regex, self.input_lines[self.i])
        keyword_bool = not (keyword_at_start is None)
        if keyword_bool:
            self.set_according_to_regex("KEYWORD", keyword_at_start.group(0).upper(), find_keyword_at_start_regex)
            return

        find_numbers_at_start_regex = r'^(' + '[0-9]+' + r')(?=(' + SYMBOL_REGEX + r'|\s+))'
        number_at_start = re.search(find_numbers_at_start_regex, self.input_lines[self.i])
        number_bool = not (number_at_start is None)
        if number_bool:
            self.set_according_to_regex("INT_CONST", number_at_start.group(0), find_numbers_at_start_regex)
            return
        find_double_quotes_regex = '^(")(.+)(")/U'
        quotes_at_start = re.search(find_double_quotes_regex, self.input_lines[self.i])
        quote_bool = not (quotes_at_start is None)
        if quote_bool:
            self.set_according_to_regex("STRING_CONST", quotes_at_start.group(0)[1:-1], find_double_quotes_regex)
            return
        find_Identifier_regex = '^([A-z]|_|[0-9])+'
        Identifier_at_start = re.search(find_Identifier_regex, self.input_lines[self.i])
        Identifier_bool = not (Identifier_at_start is None)
        if Identifier_bool:
            self.set_according_to_regex("STRING_CONST", Identifier_at_start.group(0), find_Identifier_regex)
            return
        return Exception()
        # Your code goes here!
    def set_according_to_regex(self, token_type_string, word_string, start_regex):
        self.token_type_str = token_type_string
        self.word = word_string
        self.input_lines[self.i] = re.sub(start_regex, '', self.input_lines[self.i])

    def token_type(self) -> str:
        """
        Returns:
            str: the type of the current token, can be
            "KEYWORD", "SYMBOL", "IDENTIFIER", "INT_CONST", "STRING_CONST"
        """

        return self.token_type_str

    def keyword(self) -> str:
        """
        Returns:
            str: the keyword which is the current token.
            Should be called only when token_type() is "KEYWORD".
            Can return "CLASS", "METHOD", "FUNCTION", "CONSTRUCTOR", "INT", 
            "BOOLEAN", "CHAR", "VOID", "VAR", "STATIC", "FIELD", "LET", "DO", 
            "IF", "ELSE", "WHILE", "RETURN", "TRUE", "FALSE", "NULL", "THIS"
        """
        return self.word

    def symbol(self) -> str:
        """
        Returns:
            str: the character which is the current token.
            Should be called only when token_type() is "SYMBOL".
            Recall that symbol was defined in the grammar like so:
            symbol: '{' | '}' | '(' | ')' | '[' | ']' | '.' | ',' | ';' | '+' | 
              '-' | '*' | '/' | '&' | '|' | '<' | '>' | '=' | '~' | '^' | '#'
        """
        # Your code goes here!
        return self.word

    def identifier(self) -> str:
        """
        Returns:
            str: the identifier which is the current token.
            Should be called only when token_type() is "IDENTIFIER".
            Recall that identifiers were defined in the grammar like so:
            identifier: A sequence of letters, digits, and underscore ('_') not 
                  starting with a digit. You can assume keywords cannot be
                  identifiers, so 'self' cannot be an identifier, etc'.
        """
        # Your code goes here!
        return self.word

    def int_val(self) -> int:
        """
        Returns:
            str: the integer value of the current token.
            Should be called only when token_type() is "INT_CONST".
            Recall that integerConstant was defined in the grammar like so:
            integerConstant: A decimal number in the range 0-32767.
        """
        # Your code goes here!
        return self.word

    def string_val(self) -> str:
        """
        Returns:
            str: the string value of the current token, without the double 
            quotes. Should be called only when token_type() is "STRING_CONST".
            Recall that StringConstant was defined in the grammar like so:
            StringConstant: '"' A sequence of Unicode characters not including 
                      double quote or newline '"'
        """
        # Your code goes here!
        return self.word
