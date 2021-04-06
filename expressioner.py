# README: This module does not take in whole lines, it only accepts valid expressions as inputs.
# To decomment and check for errors, use the other modules part of AP language.

#TODO: ADD BASIC FUNCTION RECOGNITION
#TODO: Fix issue with { touching text and causing crashes

import copy
from memory import Memory

# Add relational operators
operators = {
    '+': lambda x,y: x + y,
    '-': lambda x,y: x - y,
    '/': lambda x,y: x / y,
    '*': lambda x,y: x * y,
    "OR": lambda x,y: x or y,
    "AND": lambda x,y: x and y,
    "NOT": lambda x: not x,
    '<': lambda x,y: x < y,
    "<=": lambda x,y: x <= y,
    '>': lambda x,y: x > y,
    ">=": lambda x,y: x >= y,
    '=': lambda x,y: x == y,
    "!=": lambda x,y: x != y,
    "<-": None,
    '{': None,
    '}': None

}

expression_markers = set(["<-", "REPEAT", "IF", "RETURN"])

class Expression:
    def __to_num(self, values: list) -> None:
        """
        Converts all the values into real numbers
        """
        i = 0
        while i < len(values):
            if values[i] == '' or values[i] == ' ':
                del values[i]
            if isinstance(values[i], str):
                if values[i].isdigit():
                    values[i] = int(values[i])
                else:
                    self.has_variables = True
            i += 1

    def __init__(self, values: list, operators: list) -> object:
        self.has_variables = False
        self.__to_num(values)
        self.values = values
        self.operators = operators

    def __handle_function(self, memory: object, function_mem: object, func: str, args: object):
        args = args.evaluate(memory, function_mem)
        try:
            val_list = args.values
            i = 0
            while i < len(val_list):
                if val_list[i] in memory:
                    val_list[i] = memory[val_list[i]]
                elif val_list[i] in function_mem:
                    val_list[i] = self.__handle_function(memory, function_mem, val_list[i], val_list[i + 1])
                    del val_list[i + 1]
                    continue
                elif isinstance(val_list[i], Expression):
                    val_list[i] = val_list[i].evaluate(memory, function_mem) 
                
                i += 1
        except:
            if type(args) != list:
                val_list = [args]
            else:
                val_list = args


        if func in Memory("function"):
            return function_mem[func](val_list)
        else: #user-defined functions
            return function_mem[func].run(val_list, function_mem)

    def __de_expressionate(self, memory: object, function_mem = Memory("function")) -> list:
        """
        Returns a list of values based on self's values where no value is an expression;
        all values have been evaluated into real numbers. Additionally, performs the 
        important task of converting variables into their actual values in memory.
        """
        i = 0
        temps = copy.deepcopy(self.values)
        while i < len(temps):

            if isinstance(temps[i], Expression):
                temps[i] = temps[i].evaluate(memory)

            if temps[i] in memory:
                temps[i] = memory[temps[i]]
                
            if temps[i] in function_mem:
                temps[i] = self.__handle_function(memory, function_mem, temps[i], temps[i+1])
                del temps[i+1]
                continue
            

            i += 1
        return temps

    def __perform_operation(self, index: int, values: list, operations: list) -> None:
        """
        Given an index and a list of values and operations, this performs the 
        desired operation between two values (index, index + 1) and collapses
        the list, removing one element from both.
        """
        values[index] = operators[operations[index]](values[index], values[index + 1])
        del operations[index]
        del values[index + 1]

    def __pass_1(self, values: list, operations: list):
        """
        Passes through the expression to find instances of multiplying and 
        dividing first before going on to addition and substraction.
        """
        i = 0
        while i < len(operations):
            if operations[i] == '*' or operations[i] == '/':
                self.__perform_operation(i, values, operations)
                continue
            else:
                i += 1

    def __pass_2(self, values: list, operations: list):
        """
        Passes through the operation to perform any addition and subtraction.
        """
        i = 0
        while i < len(operations):
            if operations[i] == '+' or operations[i] == '-':
                self.__perform_operation(i, values, operations)
                continue
            if operations[i] == "NOT":
                values[i] = operators[operations[i]](values[i])
                del operations[i] 
            else:
                i += 1

    def __pass_3(self, values: list, operations: list):
        """
        Goes through the expression to evaluate any logical statements
        """
        i = 0
        tier = set(["OR", "AND", '<', '>', "<=", ">=", "!=", '='])
        while i < len(operations):
            if operations[i] in tier:
                self.__perform_operation(i, values, operations)
                continue
        
            else:
                i += 1

    def evaluate(self, memory: object, function_mem = Memory("function")):
        temp_values = self.__de_expressionate(memory, function_mem)
        temp_ops = copy.deepcopy(self.operators)

        self.__pass_1(temp_values, temp_ops)
        self.__pass_2(temp_values, temp_ops)
        self.__pass_3(temp_values, temp_ops)

        if len(temp_values) == 1:
            return temp_values[0]
        else:
            return temp_values


def __find_indicators(expression: str, index: int, indicator_pair = ('(', ')')) -> str:
    """
    Given a string expression and a starting position, this function finds
    the location of the outermost indicator and where it stops.
    It then returns the mini-expression (without the indicator) and the stopping
    point.
    """

    indicators = 0
    has_indicators = False
    start = None
    for i in range(index, len(expression)):
        
        if expression[i] == indicator_pair[0]:
            if indicators == 0: #first indicator
                has_indicators = True
                start = i
            indicators += 1
        
        if expression[i] == indicator_pair[1]:
            indicators -= 1
        
        if indicators == 0 and has_indicators: # true if at the end of expression
            return (expression[start+1: i], i+1) #returns the stopping point and substring
    return None

def get_tokens(line: str) -> list:
    """
    Given an entire string expression, usually a single line of code, this
    function breaks it down into values and operators in a list format, 
    regardless of use of spacing in the expression.
    """
    len_line = len(line)
    line += ' '
    tokens = [""]
    i = 0
    while i < len_line:
        if line[i] == ' ' or line[i] == ',':
            tokens.append("")

        elif line[i:i+2] in operators:
            tokens[-1] += (line[i:i+2])
            i += 1

        elif line[i] in operators:
            tokens.append("")
            tokens[-1] = line[i]
            tokens.append("")

        elif line[i] == '(':
            expression, index = __find_indicators(line, i)
            tokens.append("({})".format(expression))
            i = index -1

        else:
            tokens[-1] += line[i]
        
        i += 1


    i = 0
    while i < len(tokens):
        if tokens[i] == ' ' or tokens[i] == '':
            del tokens[i]

        else: #could have two spaces back to back
            i+=1
        

    return tokens

def __find_expression(line: str) -> list:
    """
    Given the full string of a line, find the mathematical or logical expression 
    within it.
    """
    tokens = get_tokens(line)
    for i in range(len(tokens)):
        if tokens[i] in expression_markers:
            return tokens[i+1:]
    return tokens #the entire string is a mathematical or logical expression

def interpret_expression(expression, functions = Memory("function"), is_tokenized = False) -> object:
    """
    Given a string expression, this function separates it into a set of values
    and operations being performed on those values. The input expression can be a full
    string or it can already be tokenized, but is most be indicated in the is_tokenized
    argument.
    """
    values, operator_list = [], []
    if not is_tokenized:
        tokens = __find_expression(expression)
    else:
        tokens = expression

    for i in range(len(tokens)):
        if tokens[i] in operators:
            operator_list.append(tokens[i])
        
        elif tokens[i][0] == '(':
            values.append(interpret_expression(tokens[i][1:-1], functions))

        else:
            values.append(tokens[i])
    

    return Expression(values, operator_list)

def interpret_assignment(tokens, memory: object, function_mem = Memory('function'), is_tokenized = False):
    """
    evaluates the full assignment expression. Takes input as a string and the memory
    location that is to be updated.
    """
    if tokens[1] == "<-":
        memory[tokens[0]] = interpret_expression(tokens[2:], function_mem, is_tokenized = is_tokenized).evaluate(memory,function_mem)

    else:
        raise Exception("Incorrect placement of assignment operator")

if __name__ == "__main__":
    
    test_cases = [
        ["x <- 0 OR NOT 0", True],
        ["5 + 90 - (6-7*10)", 159],
        ["50 / 5", 10],
        ["7 > 0", True]
    ]

    def test_interpret(test_cases, memory: object):
        for case in test_cases:
            if interpret_expression(case[0]).evaluate(memory) != case[1]: 
                return False, case
        return True
    
    
    M1 = Memory()
    M1.storage = {'x': 145, 'y': 10}
    print(test_interpret(test_cases, M1))
    M1.display()

    print(get_tokens("DISPLAY()"))
