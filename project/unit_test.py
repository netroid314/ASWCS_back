import unittest
from projectManager import projectManager
import numpy as np
import threading as th
import time

class ProjectManagerTests(unittest.TestCase): 

    def init(self):
        self.project_manager = projectManager()

    def get_random_gradient(self):
        tmp_weight = [np.random.rand(9)/10, np.random.rand(9)/10]
        tmp_weight = np.array(tmp_weight, dtype=object)
        return tmp_weight

    def update_gradient(self, index, gradient):
        self.project_manager.update_gradient(index, gradient)

    def timed_update_gradient(self, index, gradient, timer):
        th.Timer(timer, (lambda lamda_index,lamda_gradient: self.update_gradient(lamda_index,lamda_gradient)),(index, gradient)).start()

    def test_project_initialization(self):
        self.init()
        self.assertEqual(self.project_manager.id, 0)

    def test_poject_step_initialization(self):
        self.test_project_initialization()
        self.project_manager.set_total_step(12,3)
        self.assertEqual(self.project_manager.task_step_size, 3)

    def test_project_weight_initialization(self):
        self.test_poject_step_initialization()
        tmp_weight = [np.random.rand(9)/10, np.random.rand(9)/10]
        tmp_weight = np.array(tmp_weight, dtype=object)
        self.project_manager.set_weight(tmp_weight)

        self.assertEqual(np.array_equal(self.project_manager.result_weight, tmp_weight), True)

    def test_user_task_init(self):
        self.test_project_weight_initialization()

        self.user_1_index = self.project_manager.get_task_index()
        self.project_manager.start_task(self.user_1_index)

        self.user_2_index = self.project_manager.get_task_index()
        self.project_manager.start_task(self.user_2_index)

        self.user_3_index = self.project_manager.get_task_index()
        self.project_manager.start_task(self.user_3_index)

        self.assertEqual(self.project_manager.task_step_schedule[2], 0)

    def schdule_simulation_without_time_variation(self):
        tmp_weight_1 = self.get_random_gradient()
        self.user_1_index = self.project_manager.get_task_index()
        self.project_manager.start_task(self.user_1_index)
        self.project_manager.update_gradient(self.user_1_index, tmp_weight_1)

        tmp_weight_2 = self.get_random_gradient()
        self.user_2_index = self.project_manager.get_task_index()
        self.project_manager.start_task(self.user_2_index)
        self.project_manager.update_gradient(self.user_2_index, tmp_weight_2)

        tmp_weight_3 = self.get_random_gradient()
        self.user_3_index = self.project_manager.get_task_index()
        self.project_manager.start_task(self.user_3_index)
        self.project_manager.update_gradient(self.user_3_index, tmp_weight_3)

    def test_schdule_simulation_single(self):
        self.test_project_weight_initialization()
        self.schdule_simulation_without_time_variation()
        
        self.assertEqual(self.project_manager.get_step(), 1)

    def test_schdule_simulation_multiple(self):
        self.test_project_weight_initialization()
        self.schdule_simulation_without_time_variation()
        self.schdule_simulation_without_time_variation()
        self.schdule_simulation_without_time_variation()
        self.schdule_simulation_without_time_variation()
        
        self.assertEqual(self.project_manager.is_project_finished(), True)

    def test_schdule_simulation_with_time_variation_case_1(self):
        # Situation 1
        # user 1 did job quickly, user 2 and 3 did job slowly
        # user 1 also takes job of user 2 based on session time
        # user 1 did first ad second task and user 3 did third task.
        # user 2's job is abandoned
        self.test_project_weight_initialization()

        self.user_1_index = self.project_manager.get_task_index()
        self.project_manager.start_task(self.user_1_index)
        self.update_gradient(self.user_1_index, self.get_random_gradient())

        self.user_2_index = self.project_manager.get_task_index()
        self.project_manager.start_task(self.user_2_index)

        self.user_3_index = self.project_manager.get_task_index()
        self.project_manager.start_task(self.user_3_index)
        
        self.timed_update_gradient(self.user_2_index, self.get_random_gradient(),7)
        self.timed_update_gradient(self.user_3_index, self.get_random_gradient(),5)

        time.sleep(3)
        self.user_1_index = self.project_manager.get_task_index()
        self.project_manager.start_task(self.user_1_index)
        self.timed_update_gradient(self.user_1_index, self.get_random_gradient(),1)

        time.sleep(5)
        self.assertEqual(self.project_manager.get_step(), 1)
        

# execute unit test
if __name__ == '__main__':  
    unittest.main()