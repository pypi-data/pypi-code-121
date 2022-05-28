"""Main Utility is a module that supports the Java Tokenizer (converted to specified grammar)
and file processing.
"""

import os
import re

import java_raw_tokenizer


########################
# Java_Tokenizer Class #
########################

class Java_Tokenizer:
    """Java_Tokenizer will function as a token converter to specific characters per grammar.

    """

    def __init__(self, tokens):
        """
        Args:
            tokens (list): A list that contains tokens processed from JavaRawTokenizer Class.

        """
        self.tokens = tokens
        
        self.reset()
        
        # keyword
        self.loop_statements = {'do', 'while', 'for'}
        self.decision_statements = {'if','else','switch'}
        
        # operators
        self.arithmetic_operators = {'+', '-', '*', '/', '%'}
        self.assignment_operators = {'=', '+=', '-=', '*=', '/=', '%='}
        self.logical_operators = {'&&', '||', '!'}
        self.comparison_operators = {'<', '>', '<=', '>=', '!=', '=='}
        self.incdec_operators = {'++', '--'}
        
        # literals
        self.numbers = {'DecimalFloatingPoint', 'DecimalInteger'}
        self.booleans = {'true', 'false'}
        
        self.tokenizer(tokens)
        
        # repeat for variable and functions
        self.reset(is_reset_vars=False)
        self.tokenizer(tokens)
    
    def reset(self, is_reset_vars = True):
        """Initialize tokens and clear variable / function names container.

        Args:
            is_reset_vars (bool): Is set to True, then variables_func list
                (which stores all variables and function in the code) will be cleared.

        """
        # keep track of index of sequence (used to change identifier to variable/func before operator)
        self.index = 0
        
        # keep track of line number, for adding the line sequence
        self.current_line = self.tokens[0].position.line
        self.current_line_tokens = ''
        
        self.line_sequence = []
        self.sequence = []
        
        if(is_reset_vars):
            self.variables_func = []
    
    def get_tokenized(self):
        """Get tokenized result in a sequence.

        Returns:
            list: Sequence of characters from tokenized result.

        """
        return self.sequence
    
    def get_tokenized_lines(self):
        """Get tokenized result in a lines sequence.

        Returns:
            list: A list of pairs of line and line number from tokenized result.

        """
        self.line_sequence = [x for x in self.line_sequence if len(x[0]) > 0]
        return self.line_sequence
    
    def get_variables_func(self):
        """Get variables and function/method names from the code.

        Returns:
            list: A list of variables and function names.

        """
        return self.variables_func
    
    def tokenizer(self, tokens):
        """Groups all raw tokens into the correct grammar token and append the letter tokens
        to the sequence and line_sequence

        Args:
            tokens (list): A list that contains tokens processed from JavaRawTokenizer Class.

        Returns:
            list: A list of variables and function names.

        """
        self.flag_type = False
        is_inside_parentheses = 0
        
        self.index = 0
        self.current_line_tokens = ''
        
        for tk in tokens:
            
            if(tk.value == '('):
                is_inside_parentheses += 1
            elif(tk.value == ')'):
                is_inside_parentheses -= 1
            
            grammar = tk.__class__.__name__
            if(grammar == 'Identifier'):
                char_token = self.check_identifier(tk)
            
            elif(grammar == 'Keyword'):
                char_token = self.check_keyword(tk)
                
            elif(grammar == 'BasicType'):
                char_token = 'E'
                
                # after a type, the next token will be a variable / function (MUST BE NEXT TOKEN)
                self.flag_type = True
                
            elif(grammar == 'Modifier'):
                char_token = 'F'
                
                if(self.flag_type == True):
                    self.flag_type = False
            
            elif(grammar == 'Separator'):
                char_token = 'K'
                
                if(self.flag_type == True):
                    self.flag_type = False
            
            elif(grammar == 'Operator'):
                char_token = self.check_operator(tk)
                
                if(self.flag_type == True):
                    self.flag_type = False
            
            else:
                # literals
                char_token = self.check_literals(tk)
                
                if(self.flag_type == True):
                    self.flag_type = False
            
            # append to sequence
            self.sequence.append(char_token)
            

            # prepare append to line sequence (sequence of tokens seperated by line)
            # if the token before this is semicolon, then force it to be a newline (except for firstline and if the ; inside parentheses)
            if(tk.position.line == self.current_line and (tokens[self.index-1].value != ';' or self.index == 0 or is_inside_parentheses != 0)):
                self.current_line_tokens += char_token
            else:
                self.line_sequence.append([self.current_line_tokens, self.current_line])
                self.current_line = tk.position.line
                
                
                self.current_line_tokens = char_token
            
            if(self.index == len(tokens) - 1):
                self.line_sequence.append([self.current_line_tokens, self.current_line])
            
            self.index += 1
                
                
    def check_identifier(self, token):
        """Checks identifier group.
        Identifier consists of 2 characters, here are the characters and it's grammar category:
        - A: Variable/Function Name
        - B: IdentifierOthers (Might be a method or library name)

        Args:
            token (JavaRawTokenizer): Token processed from JavaRawTokenizer class.

        Returns:
            string: A string with length of 1, corresponding character for the token.

        """
        if(token.value in self.variables_func or self.flag_type):
            if(self.flag_type):
                self.variables_func.append(token.value)
                self.flag_type = False
            return 'A'
                
        else:
            return 'B'
        
    def check_keyword(self, token):
        """Checks keyword group.
        Keyword consists of 4 characters, here are the characters and it's grammar category:
        - C: Variable/Function Name
        - D: DecisionStatement
        - E: BasicType
        - F: KeywordOthers

        Args:
            token (JavaRawTokenizer): Token processed from JavaRawTokenizer class.

        Returns:
            string: A string with length of 1, corresponding character for the token.

        """
        value = token.value
        
        if(value in self.loop_statements):
            return 'C'
        elif(value in self.decision_statements):
            return 'D'
        else:
            if(value == 'void'):
                self.flag_type = True
            return 'F'
        
    def __change_current_line_token(self, neg_index, replacement_token):

        if(neg_index == -1):
            self.current_line_tokens = self.current_line_tokens[:neg_index] + replacement_token
        else:
            self.current_line_tokens = self.current_line_tokens[:neg_index] + replacement_token + self.current_line_tokens[neg_index + 1:]
    
    def check_literals(self, token):
        """Checks literals group.
        Literals consists of 4 characters, here are the characters and it's grammar category:
        - G: String
        - H: Number
        - I: Boolean
        - J: Null

        Args:
            token (JavaRawTokenizer): Token processed from JavaRawTokenizer class.

        Returns:
            string: A string with length of 1, corresponding character for the token.

        """
        value = token.value
        
        if(token.__class__.__name__ == 'String'):
            return 'G'
        elif(token.__class__.__name__ in self.numbers):
            return 'H'
        elif(value in self.booleans):
            return 'I'
        else:
            return 'J'

    def check_operator(self, token):
        """Checks operator group.
        Operator consists of 6 characters, here are the characters and it's grammar category:
        - L: ArithmeticOperator
        - M: AssignmentOperator
        - N: LogicalOperator
        - O: ComparisonOperator
        - P: IncrementDecrementOperator
        - Q: OperatorOthers

        Args:
            token (JavaRawTokenizer): Token processed from JavaRawTokenizer class.

        Returns:
            string: A string with length of 1, corresponding character for the token.

        """
        value = token.value
        
        if(value in self.arithmetic_operators):
            return 'L'
        elif(value in self.assignment_operators):
            
            # if it's assign operator (=), high possibility that the token before this is a variable
            if(value == '='):
                curIndex = self.index
                neg_index = 0
                
                # loop until found identifier, example: [i] = 30 (have to found i), stop until it found
                # or until changing different line
                current_line = self.tokens[curIndex].position.line
                while(True):
                    curIndex -= 1
                    neg_index -= 1
                    checkToken = self.tokens[curIndex]
                    check_line = checkToken.position.line
                    
                    if(check_line != current_line):
                        break
                    
                    if(checkToken.__class__.__name__ == 'Identifier'):
                        self.sequence[curIndex] = 'A'
                        self.__change_current_line_token(neg_index, 'A')
                        
                        if(checkToken.value not in self.variables_func):
                            self.variables_func.append(checkToken.value)
                        break
                        
            return 'M'
        
        elif(value in self.logical_operators):
            return 'N'
        elif(value in self.comparison_operators):
            return 'O'
        elif(value in self.incdec_operators):
            return 'P'
        else:
            return 'Q'




###################################
# File Processing and Initializer #
###################################

def get_all_filepaths(target_dir):
    """Get all filepaths from the specified Directory.

    Args:
        target_dir (str): A directory name/path.

    Returns:
        generator: Generator object for filepaths inside a directory.

    """
    for root, dirs, files in os.walk(target_dir, topdown=True):
        for file in files:
            current_filepath = os.path.join(root,file)
            current_filepath = os.path.abspath(current_filepath)
            yield current_filepath


def preprocess(code_string):
    """Preprocess will scan a line of code and remove any common codes.

    Args:
        code_string (str): A line of raw code.

    Returns:
        str: Preprocessed line of code.

    """
    # remove package declaration
    code_string = re.sub('package .*\n','\n', code_string)
    
    # remove class name declaration
    code_string = re.sub('public class .*\n','\n', code_string)
    
    # remove main function declaration
    code_string = re.sub('public .* main.*\n','\n', code_string)
    
    # remove curly brackets
    code_string = re.sub('[{}]','', code_string)
    
    return code_string


def get_processed_code(filepath):
    """Get processed code and raw code.

    Args:
        filepath (str): Path to the java code file.

    Returns:
        tuple: Contains raw_code, tokens, jtokenizer.
            raw_code = Raw code (str)
            tokens = A list that contains tokens processed from JavaRawTokenizer Class (list)
            jtokenizer = Object of Class Java_Tokenizer (Java_Tokenizer)

    """
    preprocessed_code = ''
    with open(filepath, 'r', encoding='utf8') as code:
        raw_code = code.read()
        for i, line in enumerate(raw_code.split('\n')):
            line += '\n'
            line = preprocess(line)
            if(len(line) == 0):
                line = ' \n'
            preprocessed_code += line
    
    tokens = java_raw_tokenizer.tokenize(preprocessed_code)
    jtokenizer = Java_Tokenizer(tokens)
    
    return (raw_code, jtokenizer)


def generate_init_data(filepaths):
    """Generate init data for calculating features.

    Args:
        filepaths (list/generator): Contains filepaths of codes from the same source of question
            or same problem number.

    Returns:
        generator: Generator object for init data. 
            Init data contains (filename, raw_code, line_sequence, line_num, raw_line_sequence, sequence, lines_length)

    """
    for filepath in filepaths:
        try:
            (raw_code, jtokenizer) = get_processed_code(filepath)
        except Exception as e:
            print('Error file: ', filepath)
            print(e)
            continue

        filename = os.path.basename(filepath)
        sequence = jtokenizer.get_tokenized()
        sequence = ''.join(sequence)
        line_sequence = jtokenizer.get_tokenized_lines()
        raw_line_sequence = raw_code.split('\n')

        # skip empty files
        if(len(sequence)) == 0:
            print('empty file: ', filepath)
            continue

        #separate line seq and line num
        line_num = [x[1] for x in line_sequence]
        line_sequence = [x[0] for x in line_sequence]

        yield (filename, raw_code, line_sequence, line_num, raw_line_sequence, sequence, len(line_sequence))
