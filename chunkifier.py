import expressioner
from expressioner import Expression
from memory import Memory
import os

class Chunk:
    def __init__(self, lines: list) -> object:
        self.lines = lines

    def run(self, memory: object, function_mem = Memory("function")) -> None:
        for line in self.lines:
            if line == [] or line == None:
                continue
            if isinstance(line, list):
                    if "<-" in line:
                        expressioner.interpret_assignment(line, memory, function_mem = function_mem, is_tokenized = True)
                    else:
                        expressioner.interpret_expression(line, function_mem, True).evaluate(memory, function_mem)
            else:
                line.run(memory, function_mem)
    
class REPEAT_UNTIL:
    def __get_conditional(self, declaration_line: list) -> object:
        """
        Given an opening line broken into tokens, this method will return
        the conditional as an expression object.
        """
        if declaration_line[-1] == '{':
            del declaration_line[-1]
        return expressioner.interpret_expression(declaration_line[2:], is_tokenized=True)

    def __init__(self, body: object, declaration_line: list) -> object:
        self.body = body
        self.condition = self.__get_conditional(declaration_line)
    
    def run(self, memory: object, function_mem = Memory("function")) -> None:
        """
        Runs the body however many times based on the conditional
        """
        while not self.condition.evaluate(memory, function_mem):
            self.body.run(memory, function_mem)

class REPEAT_TIMES:
    def __get_times(self, declaration_line: list) -> int:
        return int(declaration_line[1])

    def __init__(self, body: object, declaration_line: list) -> object:
        self.body = body
        self.num = self.__get_times(declaration_line)

    def run(self, memory: object, function_mem = Memory("function")) -> None:
        for _ in range(self.num):
            self.body.run(memory, function_mem)

class IF_ELSE_Statement:
    def __get_conditional(self, declaration_line: list) -> object:
        if declaration_line[-1] == '{':
            del declaration_line[-1]
        return expressioner.interpret_expression(declaration_line[1:], is_tokenized=True)

    def __init__(self, body: object, declaration_line: list, ELSE = None) -> object:
        self.body = body
        self.condition = self.__get_conditional(declaration_line)
        self.ELSE = ELSE
    
    def run(self, memory: object, function_mem = Memory("function")) -> None:
        if self.condition.evaluate(memory, function_mem):
            self.body.run(memory, function_mem)
        elif self.ELSE:
            self.ELSE.run(memory, function_mem)

class PROCEDURE:

    def __get_name_args(self, declaration_line: list) -> tuple:
        """
        Given the declaration line, this returns the name of the procedure
        and its arguments.
        """
        name = declaration_line[1] #PROCEDURE name
        args = expressioner.get_tokens(declaration_line[2][1:-1]) # (arg1, arg2, arg3)

        return (name, args)

    def __init__(self, body: object, declaration_line: list) -> object:
        self.body = body
        self.name, self.args = self.__get_name_args(declaration_line)

    def __handle_args(self, arguments: list) -> object:
        arg_memory = Memory()
        for i in range(len(self.args)):
            arg_memory[self.args[i]] = arguments[i]
        return arg_memory

    def run(self, args: list, function_mem = Memory("function")):
        """
        runs the procedure given the passed in arguments.
        """
        arg_memory = self.__handle_args(args)
        self.body.run(arg_memory, function_mem)
        if "RETURN" in arg_memory:
            return arg_memory["RETURN"]


chunk_types = set(["PROCEDURE", "IF", "REPEAT", "ELSE"])

def remove_n_line(tokens: list) -> list:
    if tokens[-1] == f"\n":
        del tokens[-1]

    elif tokens[-1][-1:] == f"\n":
        tokens[-1] = tokens[-1][:-1]
        
    return tokens

def convert_to_list(file_: object) -> list:
    """
    Turns the file into a list of tokens.
    """
    lines = []
    for line in file_:
        lines.append(remove_n_line(expressioner.get_tokens(line)))
    i = 0
    while i < len(lines):
        if lines[i] == []:
            del lines[i]
        else:
            i += 1
    return lines

#TODO: DOES NOT READ THE VERY FIRST LINE OF TEXT?!?!?!?!?!

def find_chunk(file_: object, line_index: int) -> tuple:
    """
    Given a starting position, this function finds the entire chunk that begins
    at that position.
    """
    chunk = []
    curlys = 1
    file_ = convert_to_list(file_)
    type_ = file_[0]
    if file_[line_index][-1] == '{':
        line_index += 1
    elif file_[line_index + 1][0] == '{':
        line_index += 2

    for i in range(line_index, len(file_)):
        for token in file_[i]:
            if token == '{':
                curlys += 1
            elif token == '}':
                curlys -= 1
        chunk.append(file_[i])
        if curlys == 0:
            if chunk[-1] == ['}']:
                del chunk[-1]
            return Chunk(chunk), type_, i
        elif curlys < 0:
            raise Exception("Curly Braces not formatted correctly")

