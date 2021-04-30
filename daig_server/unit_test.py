import unittest
from scheduleManager import scheduleManager
import numpy as np
import threading as th
import time

class ProjectManagerTests(unittest.TestCase): 

    def init(self):
        self.schedule_manager = scheduleManager()

    def test_initialization(self):
        self.init()

        tmp_init_weight = [np.random.rand(9)/10, np.random.rand(9)/10]
        tmp_init_weight = np.array(tmp_init_weight, dtype=object) 

        self.schedule_manager.init_project('100352',12,3,tmp_init_weight)

        self.assertEqual(self.schedule_manager.init_project('100352',30,6,tmp_init_weight), -1)


# execute unit test
if __name__ == '__main__':  
    unittest.main()