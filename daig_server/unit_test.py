import unittest
from scheduleManager import scheduleManager
import numpy as np
import threading as th
import time

class ProjectManagerTests(unittest.TestCase): 

    def init(self):
        self.schedule_manager = scheduleManager()

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

        new_project = self.schedule_manager.get_valid_project()
        new_task_1 = self.schedule_manager.get_valid_task(new_project)

        # need to work for several user allocation and task occupication

        self.assertEqual(new_task_1, 0)

# execute unit test
if __name__ == '__main__':  
    unittest.main()