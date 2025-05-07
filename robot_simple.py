import pygame, math, random
from vector_utils import norm, distance, rotate, diff

class Robot:
    """ робот круглой формы """
    def __init__(self, pos, target, radius, color):
       self.pos = pos
       self.target = target
       self.radius = radius
       self.v0 = 100 # magic constant! 
       self.vmax = 200
       self.vel = rotate((self.v0, 0), random.uniform(0, 2 * math.pi))
       self.tcolor = 'Lightgrey'
       self.initcolor = color
       self.state = 0 # 0 - free, 1 - collided
    def check_collision(self, a, r):
        """ проверка столкновения с другим роботом """
        return distance(self.pos, a) < r + self.radius
    def update(self, room, obstacles, robots):
        """ обновление скорости """
        if distance(self.pos, self.target) < self.radius / 20:
            """ цель достигнута """
            self.vel = (0, 0)
            return
        if self.state == 1:
            """ столкновение - меняем скорость на случайную """
            self.vel = rotate((self.v0, 0), random.uniform(0, 2 * math.pi))
        else:
            """ направляем скорость на цель """
            self.vel = diff(self.target, self.pos) 
        """ ограничиваем скорость максимальным значением """
        l = norm(self.vel)
        if l > self.vmax:
            self.vel = (self.vel[0] / l * self.vmax, self.vel[1] / l * self.vmax)
    def move(self,  dt, objects):
        """ передвижение робота, детекция столкновения """
        pos = self.pos
        self.pos = (self.pos[0] + dt * self.vel[0], self.pos[1] + dt * self.vel[1])
        self.state = 0
        if self.is_collided(objects):
            """ если есть столкновением с любым объектом, отменяем перемещение """
            self.state = 1
            self.pos = pos
    def is_collided(self, objects):
        """ проверка столкновения с объектами из списка objects """
        for obj in objects:
            if obj == self:
                continue
            if obj.check_collision(self.pos, self.radius):
                return True
        return False 
    def color(self):
        """ Текущий цвет робота """
        if distance(self.pos, self.target) < self.radius / 5:
            return "Green"
        return self.initcolor
    def draw(self, screen):
        r = self.radius
        x, y = self.pos[0] - r, self.pos[1] - r
        pygame.draw.ellipse(screen, self.color(), pygame.Rect(x, y, 2 * r, 2 * r))
        r = self.radius
        x, y = self.target[0] - r, self.target[1] - r
        pygame.draw.ellipse(screen, self.tcolor, pygame.Rect(x, y, 2 * r, 2 * r), 2)
