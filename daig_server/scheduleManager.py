import sys
import os
sys.path.append(os.path.dirname(os.path.abspath(os.path.dirname(__file__))))


from project.projectManager import projectManager

STANDBY = 0
INPROGRESS = 1
DONE = 2

SECOND = 1000
MINUTE = 60 * 1000

class scheduleManager:

    # user list consists of pair between user identificator(id or serial number) and his state
    # which is like 'learning' and 'standby'
    user_list = {'dummy_user_no':'dummy_state'}
    project_list = {'project_id':'projectManager'}

    def __init__(self):
        self.user_list = {}
        self.project_list = {}

    def init_project(self, project_id, total_step, step_size, weight):
        if project_id in self.project_list:
            return -1

        new_project = projectManager()
        self.project_list[project_id] = new_project
        self.project_list[project_id].id = project_id
        self.project_list[project_id].set_total_step(total_step,step_size)
        self.project_list[project_id].set_gardient(weight)

        return 0

    def add_user(self, user_id):
        self.user_list[user_id] = 0

    def allocate_user(self, user_id, project_id, task_index):
        self.user_list[user_id] = project_id

    def update_project(self, project_id,task_no,gradient):
        self.project_list[project].update_step_gradient(task_no,gradient)

    def get_valid_project(self):
        for project in self.project_list.keys():
            if(self.project_list[project].get_task_index() > -1):
                return self.project_list[project].id
        return -1

    def get_valid_task(self, project_id):
        return self.project_list[project_id].get_task_index()

    def get_user_allocated_project(self, user_id):
        return self.user_list[user_id]

    