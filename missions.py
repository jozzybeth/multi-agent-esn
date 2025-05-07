import math

def mission_circle(n: int):
    """ генерация миссии с круговым расположением n роботов, цели - напротив """
    def M():
        colors = {"room": "white", "obstacle": "black", "target": "lightgrey", "robot": "red"}
        data = {"size": (800, 800), "fps": 60, "rsize": 12, "colors": colors}
        data['obstacles'] = []
        data['robots'] = []
        da = 2 * math.pi / n
        for i in range(n):
            a = i * da
            r = [(400 + 200 * math.cos(a), 400 + 200 * math.sin(a)), (400 - 200 * math.cos(a), 400 - 200 * math.sin(a))]
            data['robots'].append(r)
        return data
    return M

def mission_circle_hole(n: int):
    """ генерация миссии с круговым расположением n роботов и препятствием в центре, цели - напротив """
    def M():
        colors = {"room": "white", "obstacle": "black", "target": "lightgrey", "robot": "red"}
        data = {"size": (800, 800), "fps": 60, "rsize": 12, "colors": colors}
        data['obstacles'] = [[(350, 350), (100, 100)]]
        data['robots'] = []
        da = 2 * math.pi / n
        for i in range(n):
            a = i * da
            r = [(400 + 200 * math.cos(a), 400 + 200 * math.sin(a)), (400 - 200 * math.cos(a), 400 - 200 * math.sin(a))]
            data['robots'].append(r)
        return data
    return M