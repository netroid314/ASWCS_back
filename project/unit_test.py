import unittest
from projectManager import projectManager
import numpy as np
import threading as th

class CustomTests(unittest.TestCase): 

    def init(self):
        self.project_manager = projectManager()

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
        tmp_weight_1 = [np.random.rand(9)/10,np.random.rand(9)/10]
        tmp_weight_1 = np.array(tmp_weight_1, dtype=object)
        self.project_manager.update_gradient(self.user_1_index, tmp_weight_1)

        tmp_weight_2 = [np.random.rand(9)/10,np.random.rand(9)/10]
        tmp_weight_2 = np.array(tmp_weight_2, dtype=object)
        self.project_manager.update_gradient(self.user_3_index, tmp_weight_2)

        tmp_weight_3 = [np.random.rand(9)/10,np.random.rand(9)/10]
        tmp_weight_3 = np.array(tmp_weight_3, dtype=object)
        self.project_manager.update_gradient(self.user_2_index, tmp_weight_3)

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
        self.test_user_task_init()


        self.assertEqual(self.project_manager.get_step(), 0)

# unittest를 실행
if __name__ == '__main__':  
    unittest.main()