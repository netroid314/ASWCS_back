import numpy as np


class projectManager:
    def _init_(self):
        self.result_gradient = np.array()
        self.step_gradient = np.array()
        self.task_schedule = {}
        self.task_total_count = 0
        self.task_step_count = 0
        self.current_step_count = 0
        self.current_step = 0
        self.init_tok_step = False
        self.init_tok_gradient = False

    def set_step(total_step,step):
        self.current_step_count = total_step
        self.current_step = step
        self.init_tok_step  = True

        for i in range(0,self.current_set_count):
            task_schedule[i] = 0
            """
            0 means 'Stand By'
            1 means 'In Progress'
            2 means 'Done'
            """

        return self.init_tok_step

    def set_gardient(initial_weight):
        self.result_gradient = initial_weight
        self.step_gradient = self.result_gradient - initial_weight
        self.init_tok_gradient = True

        return self.init_tok_gradient

    def update_total_gradient(gradient):
        self.result_gradient += gradient

        return True

    def gather_step_gradient(gradient):
        self.step_gradient += gradient
        self.current_step_count += 1
        
        if(self.is_step_done()):
            self.step_gradient /= self.current_step_count
            self.current_step_count = 0
            self.current_step += 1

        return current_step_count

    def is_step_done():
        return current_step_count == task_step_count


