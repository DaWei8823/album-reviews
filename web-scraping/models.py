from typing import List
import jsonpickle as jp

class BaseInput:
    processed:bool = False
    
class Persistence:


class BaseTask:

    def __init__(self, input:List[BaseInput], persistence):
        self.inputs = inputs
        self.output = []
        self.persistence = persistence

    def _execute(self):        
        try:
            for input in self.inputs:
                self.output(self.execute(input))
                input.processed = True
            


