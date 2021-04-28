import unittest
from projectManager import projectManager

class CustomTests(unittest.TestCase): 

    def init(self):
        self.project_manager = projectManager()

    def test_runs(self):
        self.init()
        self.assertEqual(self.project_manager.id, 0)


# unittest를 실행
if __name__ == '__main__':  
    unittest.main()