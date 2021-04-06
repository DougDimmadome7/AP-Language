import random as r

class Memory:
    def __init__(self, type = "default") -> object:
        self.storage = {}
        if type.lower() == 'default':
            pass
        elif type.lower() == 'function':
            self.storage["DISPLAY"] = lambda x: print(x[0])
            self.storage["INPUT"] = input
            self.storage["RANDOM"] = lambda x: r.randint(x[0],x[1]+1)
            self.storage["MOD"] = lambda x: x[0] % x[1]
            self.storage["INSERT"] = None
            self.storage["APPEND"] = None
            self.storage["REMOVE"] = None
            self.storage["LENGTH"] = None
        else:
            raise Exception("Invalid memory type")

    def __getitem__(self, index):
        return self.storage[index]
    
    def __setitem__(self, index, value):
        self.storage[index] = value

    def __iter__(self):
        for item in self.storage:
            yield item
    
    def __disp_negative(self, num: str) -> str:
        if type(num) == str:
            if num[0:3] == "(0-" and num[-1] == ')':
                return num[2:len(num)-1]
        return num

    def display(self):
        for i in self.storage:
            value = self.__disp_negative(self.storage[i])
            print("{}: {}".format(i, value))

