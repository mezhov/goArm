import yaml
file = r'problems.yaml'

problems = {1: [{'black': [[3, 1], [1, 4], [2, 4], [3, 4], [4, 4], [5, 4], [5, 3], [6, 2], [7, 3]], 'white': [[1, 2], [1, 3], [3, 2], [3, 3], [4, 3], [5, 2], [5, 1]]},
                {'black': [[1, 3], [2, 3], [4, 3], [4, 2], [4, 1]], 'white': [[1, 4], [2, 4], [3, 4], [4, 4], [5, 4], [5, 3], [5, 2], [5, 1]]},
                {'black': [[1, 1], [1, 2], [2, 2], [3, 2], [5, 1], [5, 2], [5, 3]], 'white': [[2, 1], [2, 4], [3, 3], [4, 4], [5, 4], [6, 4], [6, 3], [6, 2], [6, 1]]},
                {'black': [[4, 0], [4, 1], [5, 1], [6, 1], [7, 0], [7, 2], [8, 0], [8, 2]], 'white': [[3, 1], [3, 2], [4, 2], [5, 2], [6, 0], [6, 2], [7, 3], [8, 3]]},
                {'black': [[4, 1], [4, 2], [5, 2], [6, 2], [7, 1], [8, 1]], 'white': [[3, 0], [3, 1], [3, 2], [3, 3], [4, 3], [5, 3], [6, 1], [7, 2], [7, 3]]},

                ],
            2: [{'black': [[4, 1], [5, 1], [6, 1]], 'white': [[3, 1], [3, 2], [4, 2], [5, 2], [6, 2]]},
                {'black': [[6, 1], [7, 3], [7, 4], [8, 2], [8, 4]], 'white': [[4, 1], [5, 0], [5, 2], [5, 3], [5, 5], [6, 4], [7, 5]]},
                {'black': [[5, 1], [6, 1], [7, 1], [7, 3], [7, 4]], 'white': [[4, 0], [4, 1], [4, 2], [5, 2], [6, 3], [6, 4], [7, 5], [8, 5]]}

                ],
            3: [{'black': [[3, 1], [4, 1], [4, 2], [5, 3], [5, 4], [6, 4], [7, 4]], 'white': [[3, 2], [4, 3], [5, 2], [5, 6], [6, 1], [6, 2], [6, 5], [7, 0], [7, 2], [7, 6], [8, 1]]},
                {'black': [[2, 0], [2, 1], [2, 2], [3, 3], [4, 3], [5, 3], [5, 5], [6, 4], [7, 2], [7, 5]], 'white': [[3, 1], [3, 2], [5, 2], [6, 1], [7, 1], [7, 3]]}

                ]
            }

#check no collisions occur (the same point twice in a problem)
def check_repetitions(problem):
    return True

filtered_problems = {}
for level in problems.keys():
    filtered_problems[level] = []
    for problem in problems[level]:
        if check_repetitions(problem):
            filtered_problems[level].append(problem)

fh = open(file, 'w+')
fh.write(yaml.dump(filtered_problems))
fh.close()
