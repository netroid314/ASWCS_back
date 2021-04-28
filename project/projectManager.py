import numpy as np
import time

STANDBY = 0
INPROGRESS = 1
DONE = 2

SECOND = 1000
MINUTE = 60 * 1000

class projectManager:
    def __init__(self):
        self.id = 0
        self.finished = False
        self.time_threshold = 10*MINUTE

        self.result_gradient = np.array([])
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

    def set_total_step(total_task,step_size):
        self.task_total_count = total_task
        self.task_step_size = step

        self.current_step = 0
        self.init_tok_step  = True

        for i in range(0,self.task_step_size):
            task_step_schedule[i] = STANDBY

        return self.init_tok_step

    def set_gardient(initial_weight):
        self.result_gradient = initial_weight
        self.step_gradient = self.result_gradient - initial_weight
        self.init_tok_gradient = True

        return self.init_tok_gradient

    def set_current_step(step):
        self.current_step = step
        self.current_step_done_count = 0


    ##################################################################
    # Get functions

    def get_step():
        return self.current_step

    def get_task_index():
        for i in range(0, self.task_step_size):
            if(self.task_step_schedule[i] == STANDBY):
                return self.current_step * self.task_step_size + i

        for i in range(0, self.task_step_size):
            if(self.task_time_limit_check(self.task_step_time_stamp[i])):
                 return self.current_step * self.task_step_size + i

        return -1

    ##################################################################
    # Update and Perform related functions

    def start_task(task_index):
        self.task_step_schedule[task_index] = INPROGRESS
        self.task_step_time_stamp[task_index] = time.time()

    def update_total_gradient(gradient):
        self.result_gradient += gradient

        return True

    def update_step_gradient(task_number,gradient):
        self.step_gradient += gradient
        self.current_step_done_count += 1

        self.task_step_schedule[task_number] = DONE

        if(self.is_step_done()):
            self.step_gradient /= self.current_step_done_count
            self.set_current_step(self.current_step + 1)
            self.update_total_gradient(self.step_gradient)
            self.step_gradient *= 0

        return self.current_step_done_count

    ###################################################################
    # logical functions

    def is_step_done():
        return self.current_step_done_count == self.task_step_size

    def task_time_limit_check(task_time):
        return (time.time() - task_time) > self.time_threshold

    def is_project_finished():
        if((self.current_step * self.task_step_size) > self.task_total_count):
            self.finished = True
        else:
            self.finished = False
        return self.finished
