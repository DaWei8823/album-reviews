from typing import List, Callable
import jsonpickle as jp
import os
import re
from distutils.dir_util import copy_tree
import datetime as dt
from inspect import signature
import requests as re 

class BaseDataItem:
    
    def __init__(self)
        self.processed = False   
        self.data = None
        self.source_url = None
        self.target_urls = []

class Persistence:

    pattern = re.compile("^\d+$")
    LOG_FILE_NAME = "Log.txt"

    def __init__(self, base_path:str, recover_task_run_id:int = None):        
        self._task_run_id = Persistence.get_new_task_run_id(base_directory)
        self.task_run_directory = os.path.join(base_path,str(self.task_run_id))
        os.mkdir(self.task_run_directory)

        if prev_task_run_id:
            recover_directory = os.path.join(base_path, recover_task_run_id) 

        self.log_file_path = os.path.join(self.task_run_directory, Persistence.LOG_FILE_NAME)
        open(self.log_file_path, "w").close()

    def log(self, msg):
        with open(self.task_run_directory, "a") as f: 
            f.write(msg)
    
    def get_data(self, task_name):
        with open(os.path.join(self.task_run_directory, task_name), "r") as f:
            return jp.decode(f.read())


    @staticmethod
    def copy_files_from_recovery_directory(recover_directory):
        if not os.path.exists(recover_directory):
                raise Exception(f"Cannot find directory for recovery task run id {recover_task_run_id} in {base_path}")      
        copy_tree(recover_directory, self.task_run_directory)

    @staticmethod
    def get_new_task_run_id(base_directory):
        return max([int(file) for file in os.listdir(base_directory) 
            if Persistence.pattern.fullmatch(file)])


class ScriptBuilder:

    log_level_info = "INFO"
    log_level_error = "ERROR"

    def __init__(self, base_path:str, inputs:List[BaseInput] = None, recover_task_run_id: int = None):
        self.tasks = []
        self.recovered_from_previous_run = recover_task_run_id != None
        self.persistence = Persistence(base_path, recover_task_run_id =recover_task_run_id)
        self.inputs = []
        self.outputs = []

    def start(self, task:Callable[[],BaseDataItem]):
        if tasks:
            raise Exception(f"Task: {tasks[0].__name__} already at start")        
        if len([signature(task).parameters]) > 0:
            raise Exception(f"cannot start with {task.__name__} because it takes arguments")        
        self.tasks.append(task)    

    def then(self, task:Callable[[BaseDataItem],BaseDataItem]):
        self.tasks.append(task)

    def execute(self):
        if not self.tasks:
            raise Exception("No tasks to run!")

        start_task = tasks[0]
        if self.recovered_from_previous_run:
            inputs = self.get_data(start_task)
        else:
            log(ScriptBuilder.log_level_info, start_task, "starting")
            try:
                inputs = start_task()
            except Exception as e:
                self.log(ScriptBuilder.log_level_error,f"Error executing task {start_task.__name}")
                self.log(ScriptBuilder.log_level_error, e.msg)
                raise 

        if not (isinstance(inputs, list) and len(inputs)>0 and isinstance(inputs[0], BaseDataItem):
            raise Exception(f"starting task: {start_task.__name__} must return a non-empty list of data items")

        outputs = []


    def get_data(self, task:Callable):
        return self.persistence.get_data(task.__name__)            

    def log(self, level:str, task:Callable, msg:str):
        timestamp = dt.datetime.now().strftime("%Y-%m-%dT%H:%M:%S:%f")
        full_msg = f"{timestamp} {level} {task.__name__} {msg}"
        print(full_msg)
        self.persistence.log(full_msg)

    def _execute(self):
        try:
            for input in self.inputs:
                self.output(self.execute(input))
                input.processed = True



        

