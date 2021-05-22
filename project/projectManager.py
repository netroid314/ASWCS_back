import numpy as np
import time
import math

STANDBY = 0
CHECKED = 1
INPROGRESS = 2
DONE = 3

SECOND = 1
MINUTE = 60

class projectManager:
    def __init__(self):
        self.id = 0
        self.finished = False
        self.time_threshold = 1 * MINUTE
        self.max_contributor = 0
        self.status = 'STANDBY'

        self.result_weight = np.array([])
        self.step_gradient = np.array([])

        # task_schedule => total task schedule list
        # task_step_schedule => current step tasks schedule list
        # task_step_time_stamp => current step task's start time
        self.task_schedule = {}
        self.task_step_schedule = {}
        self.task_step_time_stamp = {}

        # total_count => total task number
        # step_size => each step size
        # total_count % step_size should be zero (or not later)
        self.task_total_count = 0
        self.task_step_size = 0
        self.done_task_number = 0

        # current_step is literally current step
        # current_step_done_count is number of done tasks in current step
        self.current_step = 0
        self.current_step_done_count = 0
      
        # initialization validation tokens
        self.init_tok_step = False
        self.init_tok_gradient = False

        # Belows are for url link
        self.model_url = ""
        self.data_url = ""

    ###################################################################
    # Setting functions

    def set_total_step(self, total_task, step_size):
        self.task_total_count = total_task
        self.task_step_size = step_size

        self.set_max_contiributor(math.ceil(step_size/2))

        self.current_step = 0
        self.init_tok_step  = True

        for i in range(0,self.task_step_size):
            self.task_step_schedule[i] = STANDBY

        return self.init_tok_step

    def set_max_contiributor(self,max_number):
        self.max_contributor = max_number
        return self.max_contributor

    def set_weight(self, initial_weight):
        self.result_weight = initial_weight
        self.step_gradient = self.result_weight - initial_weight
        self.init_tok_gradient = True

        return self.init_tok_gradient

    def set_current_step(self, step):
        self.current_step = step
        self.current_step_done_count = 0

    def start_project(self):
        self.status = 'INPROGRESS'
    ##################################################################
    # Get functions

    def get_step(self):
        return self.current_step

    def get_total_task_number(self):
        return self.task_total_count

    # Caution! this function is very important for making shedule for project.
    # Modify this carefully to avoid loop holes or other problems
    # currently, max paritipant = task step size
    def get_task_index(self):
        # Later, change for loop and if statement into filter based iteration
        if(self.is_project_finished()):
            return -1
        
        if(self.is_max_contributor()):
            return -1
            
        for i in range(0, self.task_step_size):
            if(self.task_step_schedule[i] == STANDBY):
                self.task_step_schedule[i] = CHECKED
                self.task_step_time_stamp[i] = time.time()
                return self.current_step * self.task_step_size + i

        for i in range(0, self.task_step_size):
            if(self.task_step_schedule[i] == INPROGRESS and self.task_time_limit_check(self.task_step_time_stamp[i])):
                return self.current_step * self.task_step_size + i

        for i in range(0, self.task_step_size):
            if(self.task_step_schedule[i] == CHECKED and self.task_time_limit_check(self.task_step_time_stamp[i])):
                return self.current_step * self.task_step_size + i 

        return -1

    def get_result_weight(self):
        return self.result_weight

    def get_pariticipants_number(self):
        count = 0
        for key in self.task_step_schedule:
            if(self.task_step_schedule[key] == INPROGRESS):
                count += 1
        return count

    ##################################################################
    # Update and Perform related functions

    def start_task(self, task_index):
        if(task_index < 0):
            return -1
        self.task_step_schedule[task_index % self.task_step_size] = INPROGRESS
        self.task_step_time_stamp[task_index % self.task_step_size] = time.time()

    def update_total_gradient(self, gradient):
        self.result_weight += gradient

        return True

    def update_gradient(self, task_number,gradient, time = -1):
        task_number = int(task_number)
        step = math.floor(task_number / self.task_step_size)
        if(step != self.current_step):
            print("project id: ",self.id,' # Task abandoned: Incorrect Step')
            return -1

        if(self.task_step_schedule[task_number % self.task_step_size] == DONE):
            print("project id: ",self.id,' # Task abandoned: Duplicated approach at ' + str(task_number))
            return -1

        self.step_gradient += gradient
        self.current_step_done_count += 1

        if(self.is_new_shortest_time(time)): self.time_threshold = time

        self.task_step_schedule[task_number % self.task_step_size] = DONE
        self.done_task_number += 1
        print("project id: ",self.id," # gradient updated at ",task_number)
        if(self.is_step_done()):
            for key in self.task_step_schedule:
                self.task_step_schedule[key] = STANDBY
            self.step_gradient /= self.current_step_done_count
            self.set_current_step(self.current_step + 1)
            self.update_total_gradient(self.step_gradient)
            self.step_gradient *= 0
            self.current_step_done_count = 0

        return self.current_step_done_count

    ###################################################################
    # logical functions

    def is_max_contributor(self):
        return self.get_pariticipants_number() >= self.max_contributor

    def is_step_done(self):
        return self.current_step_done_count == self.task_step_size

    def is_project_available(self):
        return not(self.is_max_contributor() or self.is_project_finished() or (self.get_task_index() == -1))

    def task_time_limit_check(self, task_time):
        return (time.time() - task_time) > (self.time_threshold * 1.5)

    def task_search_limit_check(self, task_time):
        return (time.time() - task_time) > 3 * SECOND

    def is_project_finished(self):
        if( self.done_task_number >= self.task_total_count):
            self.finished = True
            self.status = 'DONE'
        else:
            self.finished = False
        return self.finished

    def is_new_shortest_time(self,time):
        return (time > -1) and (time < self.time_threshold)