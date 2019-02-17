import yaml
file = r'problems.yaml'

problems = {1: [{'black': [[3, 1], [1, 4], [2, 4], [3, 4], [4, 4], [5, 4], [5, 3], [6, 2], [7, 3]],
                 'white': [[1, 2], [1, 3], [3, 2], [3, 3], [4, 3], [5, 2], [5, 1]]},
                {'black': [[1, 3], [2, 3], [4, 3], [4, 2], [4, 1]],
                 'white': [[1, 4], [2, 4], [3, 4], [4, 4], [5, 4], [5, 3], [5, 2], [5, 1]]},
                {'black': [[1, 1], [1, 2], [2, 2], [3, 2], [5, 1], [5, 2], [5, 3]],
                 'white': [[2, 1], [2, 4], [3, 3], [4, 4], [5, 4], [6, 4], [6, 3], [6, 2], [6, 1]]}
                ],
            2: [{'black': [],
                 'white': []},
                {'black': [],
                 'white': []},
                {'black': [],
                 'white': []}
                ],
            3: [{'black': [],
                 'white': []},
                {'black': [],
                 'white': []},
                {'black': [],
                 'white': []}
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
