#board.py

import yaml
from py.helpers.myloggers import getLogger
LOG = getLogger(__name__)


class Board:
    def __init__(self, conffile):
        try:
            f = open(conffile, "r")
            record = yaml.load(f)
            f.close()
            self.board_size = record["board size"]
            self.x_shift = [(record["board"][2][i] - record["board"][1][i])/(self.board_size - 1) for i in range(3)]
            self.y_shift = [(record["board"][0][i] - record["board"][1][i])/(self.board_size - 1) for i in range(3)]
            self.reference_point = record["board"][1]
            self.drop_stones = record.get("drop stones", [round(self.reference_point[i] - 2 * self.x_shift[i] + 2 * self.y_shift[i], 1) for i in range(3)])
            self.max_height = max(
                record["board"][0][2],
                record["board"][1][2],
                record["board"][2][2],
                self.get_real_vertex([self.board_size, self.board_size])[2],
                self.drop_stones[2]
            )
            LOG.info(self.show())
        except Exception as e:
            LOG.error("Board not initialised: {}".format(str(e)))
            raise e

    #returns real vertex for logical vertex as 1-19
    def get_real_vertex(self, logical_vertex):
        x = logical_vertex[0] - 1
        y = logical_vertex[1] - 1

        if (type(x) is int) and (type(y) is int) and (x in range(self.board_size)) and (y in range(self.board_size)):
            real_vertex = [round(self.reference_point[i] + x * self.x_shift[i] + y * self.y_shift[i], 1) for i in range(3)]
            return real_vertex
        else:
            return None

    def show(self):
        return "Board size: {}. Ref.point: {}. Shifts x: {}, y: {}".format(self.board_size, str(self.reference_point), self.x_shift, self.y_shift)
