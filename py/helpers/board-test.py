from py.helpers.board import Board

b = Board(conffile=r'C:\work\goArm\experiments\goArm\env\env.yaml')
print(b.show())

test_array =[
    [[4, 0], None, 'out of index min'],
    [[1, 4], [13.1, 15.0, 16.9], 'normal vertex min'],
    [[10, 4], None, 'out of index max'],
    [[9, 1], [20.0, 21.0, 22.0], 'normal vertex max'],
    [[-1, 4], None, 'out of index'],
    [[1.1, 4], None, 'non int index']
]


def run_tests(test_array, function, test_pack_name=None):
    if test_pack_name:
        print(test_pack_name)
    for test in test_array:
        result = function(test[0])
        print("[{}] {}: {} -> {} ({} expected)".format('PASS' if result == test[1] else 'FAIL', test[2], test[0], result, test[1]))


run_tests(test_array, b.get_real_vertex, "Vertex transformation")

