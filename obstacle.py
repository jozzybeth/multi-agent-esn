import pygame
from vector_utils import distance, clamp

class Obstacle:
    """ препятствие прямоугольной формы """
    def __init__(self, pos, size, color):
       self.pos = pos
       self.size = size
       self.color = color 
    def draw(self, screen):
        pygame.draw.rect(screen, self.color, pygame.Rect(*self.pos, *self.size))
    def check_collision(self, a, r):
        """ проверка столкновения робота (a, r) с данным препятствием (a - положение, r - радиус) """
        return self.inside(a) or self.dist(a) < r
    def inside(self, a):
        """ находится ли робот 'внутри' препятствия """
        c = [a[i] > self.pos[i] and a[i] < self.pos[i] + self.size[i] for i in [0, 1]]
        return c[0] and c[1]
    def dist(self, a):
        """ расстояние от точки a до границы препятствия """
        d1 = distance(a, (clamp(self.pos[0], self.pos[0] + self.size[0], a[0]), self.pos[1]))
        d2 = distance(a, (clamp(self.pos[0], self.pos[0] + self.size[0], a[0]), self.pos[1] + self.size[1]))
        d3 = distance(a, (self.pos[0], clamp(self.pos[1], self.pos[1] + self.size[1], a[1])))
        d4 = distance(a, (self.pos[0] + self.size[0], clamp(self.pos[1], self.pos[1] + self.size[1], a[1])))
        return min(d1, d2, d3, d4)