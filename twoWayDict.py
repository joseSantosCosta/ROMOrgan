class twoWayDict():
    def __init__(self,dictionary:dict):
        self.dictionary = dictionary
    
    def normalDict(self):
        return self.dictionary
    
    def inverseDict(self):
        inverseDict = {}
        for console, aliases in self.dictionary.items():
            for alias in aliases:
                inverseDict[alias.lower()] = console
        return inverseDict





    

    




    

