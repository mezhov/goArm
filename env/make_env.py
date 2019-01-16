import yaml, json

def dump_file(record, filename, type):
    if type in ["json", "yaml"]:
        f = open("{}.{}".format(filename, type), "w+")
        s = yaml.dump(record) if type == "yaml" else json.dumps(record)
        f.write(s)
        f.close()
        return True
    else:
        return False

#   3 points to set a board
#   A......
#   .......
#   .......
#   B.....C
A = [10, 10, 10]
B = [15, 15, 15]
C = [20, 20, 20]
board_size = 9

black_stone_matrix = [[1, 1, 1],
                      [1, 1.1, 1],
                      [1, 1.2, 1],
                      [1, 1.3, 1],
                      [1, 1.4, 1],
                      [1, 1.5, 1],
                      [1, 1.6, 1]]
white_stone_matrix = [[2, 1, 1],
                      [2, 1.1, 1],
                      [2, 1.2, 1],
                      [2, 1.3, 1],
                      [2, 1.4, 1],
                      [2, 1.5, 1],
                      [2, 1.6, 1]]

env = {"board": [A, B, C],
       "board size": board_size,
       "black_stone_matrix": [black_stone_matrix],
       "white_stone_matrix": [white_stone_matrix]}

dump_file(env, "env", "yaml")
dump_file(env, "env", "json")