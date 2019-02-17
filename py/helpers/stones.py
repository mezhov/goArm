#stones.py

import yaml
from py.helpers.myloggers import getLogger
LOG = getLogger(__name__)


class Stones:
    stones = {"black": [], "white": []}
    counter = {"black": 0, "white": 0}

    def __init__(self, conffile):
        try:
            f = open(conffile, "r")
            record = yaml.load(f)
            f.close()
            self.stones = {"black": record["black_stone_matrix"], "white": record["white_stone_matrix"]}
            LOG.info("Stones initiated: {}".format(self.stones))
            self.max_height = max([x[2] for x in (self.stones['black'] + self.stones['white'])])

        except Exception as e:
            LOG.error("Stones not initialised: {}".format(str(e)))
            raise e

    def get_next_stone(self, colour):
        #doing ring list here
        if self.counter[colour] >= len(self.stones[colour]):
            self.counter[colour] = 0
        return self.stones[colour][self.counter[colour]]

    def move_done(self, colour):
        self.counter[colour] += 1
