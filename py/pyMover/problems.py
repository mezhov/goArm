from py.pyMover.goArm import GoArm
from py.helpers import myloggers
import yaml
LOG = myloggers.getLogger(__name__)


class ProblemCollection:
    problems_file = r'C:\work\goArm\experiments\goArm\problems\problems.yaml'
    problems = {}
    counter = {}

    def __init__(self):
        #read problems here
        self.problems = yaml.load(open(self.problems_file))
        self.counter = {level: 0 for level in self.problems.keys()}

    def get_next_problem(self, level):
        if self.counter[level] >= len(self.problems[level]):
            self.counter[level] = -1
        self.counter[level] += 1
        return self.problems[level][self.counter[level]-1]


if __name__ == "__main__":

    myArm = GoArm()
    problems = ProblemCollection()

    def print_menu():
        print("##############")
        print("1 - 10 kyu problem")
        print("2 - 1 kyu problem")
        print("3 - 1 dan problem")
        print("q - exit")
        print("##############")

    user_input = None
    while user_input != 'q':
        print_menu()
        user_input = input("Your choice: ")
        if user_input in ['1', '2', '3']:
            try:
                problem = problems.get_next_problem(int(user_input))
                LOG.info("Got the problem for you. playing")
                myArm.put_stones(problem)
            except:
                LOG.error("Oops, failure...")
