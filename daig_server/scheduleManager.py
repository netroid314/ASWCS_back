import sys
import os
import numpy as np
sys.path.append(os.path.dirname(os.path.abspath(os.path.dirname(__file__))))


from project.projectManager import projectManager

INVALID = -1
STANDBY = 0
INPROGRESS = 1

SECOND = 1000
MINUTE = 60 * 1000

class scheduleManager:

    # user list consists of pair between user identificator(id or serial number) and his state
    # which is like 'learning' and 'standby'
    user_list = {'dummy_user_no':['dummy_state','allocated_project','working_task']}
    project_list = {'project_id':'projectManager'}
    project_user_match_list = {'project_id':['users_list(not user list dictionary)']}

    def __init__(self):
        self.user_list = {}
        self.project_list = {}
        self.project_user_match_list = {}

    def init_project(self, project_id, total_step, step_size, weight, epoch, batch_size, max_contributor = -1, saved_step = INVALID):
        if project_id in self.project_list:
            return -1

        new_project = projectManager()
        self.project_list[project_id] = new_project
        self.project_list[project_id].id = project_id
        self.project_list[project_id].set_total_step(total_step,step_size,max_contributor)
        self.project_list[project_id].set_weight(weight)
        self.project_list[project_id].set_project_config(epoch = epoch, batch_size = batch_size)
        self.project_user_match_list[project_id] = []

        return 0

    def reset(self):
        self.user_list = {}
        self.project_list = {}
        self.project_user_match_list = {}

    ##################################################################
    # Various distributed learning purpose functions

    def add_user(self, user_id):
        self.user_list[user_id] = [STANDBY, '', -1]

    def allocate_user(self, user_id, project_id, task_index):
        self.user_list[user_id] = [INPROGRESS, project_id, task_index]
        self.project_list[project_id].start_task(task_index)

        if(not(user_id in self.project_user_match_list[project_id])):
            self.project_user_match_list[project_id].append(user_id)

    def deallocate_user(self, user_id):
        self.project_user_match_list[self.user_list[user_id][1]].remove(user_id)
        self.user_list[user_id] = [STANDBY, '', -1]

    def start_project(self, project_id):
        self.project_list[project_id].status = 'INPROGRESS'

    def pause_project(self,project_id):
        self.project_list[project_id].status = 'STANDBY'

    def update_project(self, project_id,task_no,gradient,time):
        return self.project_list[project_id].update_gradient(task_number = task_no, gradient = gradient, time = time)

    def start_project_task(self, project_id, task_no):
        self.project_list[project_id].start_task(task_no)

    ##################################################################
    # Get function for getting various overall projects information

    def get_valid_project(self):
        for project in self.project_list.keys():
            if(self.project_list[project].is_project_available()):
                return self.project_list[project].id
        return -1

    def get_valid_task(self, project_id):
        return self.project_list[project_id].get_task_index()

    def get_total_task_number(self, project_id):    
        return self.project_list[project_id].get_total_task_number()
    
    def get_project_weight(self, project_id):
        return self.project_list[project_id].get_result_weight()

    def get_project_result(self, project_id):
        if not(self.is_project_finished(project_id = project_id)):
            return np.array([-1])

        return self.project_list[project_id].get_result_weight()

    def get_user_allocated_project(self, user_id):
        return self.user_list[user_id][1]

    def get_total_users(self):
        return len(self.user_list)

    def get_available_users(self):
        return len(dict(filter(lambda user:user[1][0]==STANDBY,self.user_list.items())))

    def get_project_progress(self, project_id):
        return self.project_list[project_id].get_progress()

    ##################################################################
    # Belows are logicals

    def is_project_finished(self, project_id):
        return self.project_list[project_id].is_project_finished()
