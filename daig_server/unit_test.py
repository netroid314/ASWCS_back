import unittest
from scheduleManager import scheduleManager
import numpy as np
import threading as th
import time

class ProjectManagerTests(unittest.TestCase): 

    def init(self):
        self.schedule_manager = scheduleManager()

    def get_random_gradient(self):
        tmp_weight = [np.random.rand(9)/10, np.random.rand(9)/10]
        tmp_weight = np.array(tmp_weight, dtype=object)
        return tmp_weight

    def test_initialization_new_project(self):
        self.init()

        tmp_init_weight = [np.random.rand(9)/10, np.random.rand(9)/10]
        tmp_init_weight = np.array(tmp_init_weight, dtype=object) 

        self.schedule_manager.init_project('100352',12,3,tmp_init_weight)

        self.assertEqual(self.schedule_manager.init_project('100352',30,6,tmp_init_weight), -1)

    def test_initialization_new_users(self):
        self.test_initialization_new_project()

        self.schedule_manager.add_user('100001')
        self.schedule_manager.add_user('100002')
        self.schedule_manager.add_user('100003')

        self.assertEqual(self.schedule_manager.get_available_users(), 3)

    def test_some_users_task_occupication(self):
        self.test_initialization_new_users()

        new_project = self.schedule_manager.get_valid_project()
        new_task_1 = self.schedule_manager.get_valid_task(new_project)
        self.schedule_manager.allocate_user('100001',new_project,new_task_1)

        self.assertEqual(self.schedule_manager.get_available_users(), 2)

    def test_three_users_task_process(self):
        self.test_initialization_new_users()

        new_project = self.schedule_manager.get_valid_project()
        new_task_1 = self.schedule_manager.get_valid_task(new_project)
        self.schedule_manager.allocate_user('100001',new_project,new_task_1)

        new_task_2 = self.schedule_manager.get_valid_task(new_project)
        self.schedule_manager.allocate_user('100002',new_project,new_task_2)
        
        new_task_3 = self.schedule_manager.get_valid_task(new_project)
        self.schedule_manager.allocate_user('100003',new_project,new_task_3)
        # need to work for several user allocation and task occupication

        tmp_gradient_1 = self.get_random_gradient()
        tmp_gradient_2 = self.get_random_gradient()
        tmp_gradient_3 = self.get_random_gradient()

        self.schedule_manager.update_project(new_project,new_task_1,tmp_gradient_1)
        self.schedule_manager.deallocate_user('100001')
        self.schedule_manager.update_project(new_project,new_task_2,tmp_gradient_2)
        self.schedule_manager.deallocate_user('100002')
        self.schedule_manager.update_project(new_project,new_task_3,tmp_gradient_3)
        self.schedule_manager.deallocate_user('100003')

        self.assertEqual(self.schedule_manager.project_list[new_project].get_task_index(), 3)
        self.assertEqual(self.schedule_manager.get_available_users(), 3)

# execute unit test
if __name__ == '__main__':  
    unittest.main()