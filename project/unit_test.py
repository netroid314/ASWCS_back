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

    def update_gradient(self, step, index, gradient):
        self.project_manager.update_gradient(step, index, gradient)

    def timed_update_gradient(self, step, index, gradient, timer):
        th.Timer(timer, (lambda lamda_step,lamda_index,lamda_gradient: self.update_gradient(lamda_step,lamda_index,lamda_gradient)),(step, index, gradient)).start()
        print('time out with '+ str(step) + ':' +  str(index))

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
        self.project_manager.set_gardient(tmp_weight)

        self.assertEqual(np.array_equal(self.project_manager.result_gradient, tmp_weight), True)

    def test_user_task_init(self):
        self.test_project_weight_initialization()

        self.user_1_index = self.project_manager.get_task_index()
        self.project_manager.start_task(self.user_1_index)

        self.user_2_index = self.project_manager.get_task_index()
        self.project_manager.start_task(self.user_2_index)

        self.user_3_index = self.project_manager.get_task_index()
        self.project_manager.start_task(self.user_3_index)

        self.assertEqual(self.project_manager.get_task_index(), -1)

    def schdule_simulation_without_time_variation(self):
        tmp_weight_1 = self.get_random_gradient()
        self.project_manager.update_gradient(self.project_manager.current_step, self.user_1_index, tmp_weight_1)

        tmp_weight_2 = self.get_random_gradient()
        self.project_manager.update_gradient(self.project_manager.current_step, self.user_3_index, tmp_weight_2)

        tmp_weight_3 = self.get_random_gradient()
        self.project_manager.update_gradient(self.project_manager.current_step, self.user_2_index, tmp_weight_3)

    def test_schdule_simulation_single(self):
        self.test_user_task_init()
        self.schdule_simulation_without_time_variation()
        
        self.assertEqual(self.project_manager.get_step(), 1)

    def test_schdule_simulation_multiple(self):
        self.test_user_task_init()

        self.schdule_simulation_without_time_variation()
        self.schdule_simulation_without_time_variation()
        self.schdule_simulation_without_time_variation()
        self.schdule_simulation_without_time_variation()        
        
        self.assertEqual(self.project_manager.is_project_finished(), True)

    def test_schdule_simulation_with_time_variation(self):
        self.test_project_weight_initialization()

        self.user_1_index = self.project_manager.get_task_index()
        self.project_manager.start_task(self.user_1_index)

        self.user_2_index = self.project_manager.get_task_index()
        self.user_3_index = self.project_manager.get_task_index()

        self.project_manager.start_task(self.user_2_index)
        self.project_manager.start_task(self.user_3_index)
      
        self.update_gradient(0, self.user_1_index, self.get_random_gradient())
        
        self.timed_update_gradient(0, self.user_3_index, self.get_random_gradient(),1)
        self.timed_update_gradient(0, self.user_2_index, self.get_random_gradient(),2)


        time.sleep(3)
        self.assertEqual(self.project_manager.is_project_finished(), False)
        

# execute unit test
if __name__ == '__main__':  
    unittest.main()