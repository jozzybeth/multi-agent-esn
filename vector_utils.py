import math
def norm(a):
    """ длина вектора a """
    return math.sqrt(a[0] ** 2 + a[1] ** 2)

def diff(a, b):
    """ разность векторов a - b"""
    return a[0] - b[0], a[1] - b[1]

def distance(a, b):
    """ расстояние между двумя точками """
    return norm(diff(a, b))

def clamp(a, b, x):
    """ обрезка величины x """
    if x < a: return a
    if x > b: return b
    return x

def rotate(v, a):
    """ поворот вектора v на угол a """
    c, s = math.cos(a), math.sin(a)
    return c * v[0] - s * v[1], s * v[0] + c * v[1]

def normalize(a):
    """ нормализация вектора """
    d = norm(a)
    return a[0] / d, a[1] / d