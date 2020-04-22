from typing import List, Callable
import jsonpickle as jp
import os
import re
from distutils.dir_util import copy_tree

class BaseDataItem:
    processed:bool = False
    data:'any'
    
class Persistence:

    pattern = re.compile("^\d+$")
    LOG_FILE_NAME = "Log.txt"

    def __init__(self, base_path:str, recover_task_run_id:int = None):        
        self._task_run_id = Persistence.get_new_task_run_id(base_directory)
        self.task_run_directory = os.path.join(base_path,str(self.task_run_id))
        os.mkdir(self.task_run_directory)

        if prev_task_run_id:
            recover_directory = os.path.join(base_path, recover_task_run_id) 
            if not os.path.exists(recover_directory):
                raise f"Cannot find directory for recovery task run id {recover_task_run_id} in {base_path}"        
            copy_tree(recover_directory, self.task_run_directory)
        
        self.log_file_path = os.path.join(self.task_run_directory, Persistence.LOG_FILE_NAME)
        open(self.log_file_path, "w").close()

    def append_to_logs(self, msg):
        with open(self.task_run_directory, "a") as f: 
            f.write(msg)
               
    @staticmethod
    def get_new_task_run_id(base_directory):
        return max([int(file) for file in os.listdir(base_directory) 
            if Persistence.pattern.fullmatch(file)])


class TaskExecutor:

    def __init__(self, base_path:str, inputs:List[BaseInput] = None, recover_task_run_id: int = None):
        self.inputs = inputs
        self.outputs = []
        self.persistence = Persistence(base_path, recover_task_run_id =recover_task_run_id)


    def start(self, task:Callable[[],BaseDataItem]):
        self.log()

    def then(self, task:Callable[[BaseDataItem],BaseDataItem]):
        
        return self

    def do_item(self, action:Callable[[BaseDataItem],None])
        for output in self.outputs:
            action(output)
        
        return self

    def do_items(self, action:Callable[[List[BaseDataItem]],None])
        action(self.outputs)
        return self

    def log(self, level:str, task:Callable, msg:str):
        

    def _execute(self):
        try:
            for input in self.inputs:
                self.output(self.execute(input))
                input.processed = True



