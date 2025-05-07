import pygame

class Room:
    """ помещение (прямоугольник, ограниченный стенками) """
    def __init__(self, size, color):
       self.size = size
       self.color = color 
    def draw(self, screen):
        pygame.draw.rect(screen, self.color, pygame.Rect(0, 0, self.size[0], self.size[1]))
    def check_collision(self, a, r):
        """ проверка столкновения робота (a, r) со стенками (a - положение, r - радиус) """
        if a[0] < r or a[0] > self.size[0] - r:
            return True
        if a[1] < r or a[1] > self.size[1] - r:
            return True
        return False