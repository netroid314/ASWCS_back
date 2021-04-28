from ..project import projectManager

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

    def start_project(project_id):
        if project_id in self.project_list:
            return -1

        new_project = projectManager()
        self.project_list[project_id] = new_project
        return 0

    def add_user(user_id):
        self.user_list[user_id] = STANDBY

    def learn_user(user_id):
        self.user_list[user_id] = INPROGRESS

    def get_valid_project():
        for project in self.project_list.keys():
            if(self.project_list[project])

