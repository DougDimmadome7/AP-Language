from memory import Memory
from chunkifier import Chunk
import chunkifier
import expressioner


class Interpreter:
    def __init__(self):
        self.variable_mem = Memory()
        self.function_mem = Memory("function")

    def convert(self, file_: str) -> list:
        """
        This method converts a file into the more readable token list form.
        In this form, the text is converted into a series of lists containing
        individual tokens of code.
        """
        file_ = open(file_, 'r')
        converted = []
        for line in file_:
            converted.append(chunkifier.remove_n_line(expressioner.get_tokens(line)))

        # Remove any blank lines.    
        i = 0
        while i < len(converted):
            if converted[i] == []:
                del converted[i]
            else:
                i += 1
        return converted

    def __is_chunk(self, line: list) -> bool:
        """
        given a line of PLTW code, returns whether or not the line contains the 
        start of a chunk.
        """
        if line[0] in chunkifier.chunk_types:
            return True

    def __find_type(self, line: list) -> str:
        """
        Given a first line, this method returns the block type.
        """
        if line == None:
            return
        if line[0] in chunkifier.chunk_types:
            if line[0] == "REPEAT":
                if line[1] == "UNTIL":
                    return "REPEAT UNTIL"
                return "REPEAT N TIMES"
            return line[0]
        else:
            return False

    def __find_else(self, code_lines: list, end: int) -> int:
        """
        This function finds the else statement associated with an if on the
        condition that it exists.
        """
        for line in range(end, len(code_lines)):
            for token in code_lines[line]:
                if token == "ELSE":
                    return line
        
        return False

    def __find_bounds(self, code_lines: list, chunk_start: int) -> int:
        """
        Given where a chunk starts, this returns the index where it ends as well.
        """
        braces = 0
        for i in range(chunk_start, len(code_lines)):
            for char in code_lines[i]:
                if char == '{':
                    braces += 1
                elif char == '}':
                    braces -= 1
            if braces == 0:
                return i
        raise Exception("ERROR: DOES NOT END!")

    def clean(self, chunk_lines: list) -> None:
        try:
            if chunk_lines[-1][-1] == "}":
                del chunk_lines[-1][-1]
            if chunk_lines[-1] == []:
                del chunk_lines
        except:
            pass
    
    #TODO: Make the __chunk handling of if else statements less jank.

    def __chunk(self, code_lines: list, declaration_line = None) -> object:
        """
        Breaks the code down into a large chunk, composed of several smaller chunks,
        such as conditionals, loops, or procedures. This allows the code to
        """
        i = 0
        has_else = False
        chunk_type = self.__find_type(declaration_line)
        chunk_lines = []
        while i < len(range(len(code_lines))):

            if self.__is_chunk(code_lines[i]): #if start of chunk
                end = self.__find_bounds(code_lines, i)

                if self.__find_type(code_lines[i]) == "IF" and self.__find_else(code_lines, end):
                    end = self.__find_bounds(code_lines, self.__find_else(code_lines, end))
                    chunk_lines.append(self.__chunk(code_lines[i + 1 : end + 1], code_lines[i]))
                
                elif self.__find_type(code_lines[i]) == "ELSE" and chunk_type == "IF":
                    else_body = self.__chunk(code_lines[i + 1: ])
                    has_else = True


                else:
                    chunk_lines.append(self.__chunk(code_lines[i + 1 : end + 1], declaration_line = code_lines[i]))
                i = end  

            elif isinstance(code_lines[i], list): #if just a normal body lines
                if code_lines[i][0] == "RETURN":
                    code_lines[i].insert(1, "<-")
                chunk_lines.append(code_lines[i])
            i += 1

        self.clean(chunk_lines)
        if chunk_type == "REPEAT UNTIL":
            return chunkifier.REPEAT_UNTIL(Chunk(chunk_lines), declaration_line)
        elif chunk_type == "REPEAT N TIMES":
            return chunkifier.REPEAT_TIMES(Chunk(chunk_lines), declaration_line)
        elif chunk_type == "IF":
            if has_else:
                return chunkifier.IF_ELSE_Statement(Chunk(chunk_lines), declaration_line, else_body)
            return chunkifier.IF_ELSE_Statement(Chunk(chunk_lines), declaration_line)

        elif chunk_type == "PROCEDURE":
            procedure = chunkifier.PROCEDURE(Chunk(chunk_lines), declaration_line)
            self.function_mem[procedure.name] = procedure 

        elif chunk_type == None:
            return Chunk(chunk_lines)
        
    def interpret(self, file_: str) -> None:
        """
        The main purpose of the class. Takes the name of a file and runs it.
        """
        code = self.convert(file_)
        chunked = self.__chunk(code)
        chunked.run(self.variable_mem, self.function_mem)
        


    


if __name__ == "__main__":
    I = Interpreter()
    I.interpret("fib.txt")