import pygame, math, random
import numpy as np
from esn import EchoStateNetwork
from vector_utils import norm, distance, clamp, rotate, diff

class Robot:
    def __init__(self, pos, target, radius, color,
                 n_reservoir=600, min_samples=400):
        self.pos = pos
        self.target = target
        self.radius = radius
        self.initcolor = color

        self.v0 = 100
        self.vmax = 200
        self.vel = rotate((self.v0, 0), random.uniform(0, 2 * math.pi))

        self.feature_dim = 8  # [pos_x, pos_y, target_x, target_y, v_x, v_y, obstacle_x, obstacle_y]
        self.esn = EchoStateNetwork(
            n_inputs=self.feature_dim,
            n_reservoir=n_reservoir,
            n_outputs=2,
            spectral_radius=0.9,
            sparsity=0.3,
            leaking_rate=0.2
        )

        self.train_inputs = []
        self.train_outputs = []
        self.min_samples = min_samples
        
        self.state = 0

    def check_collision(self, a, r):
        return distance(self.pos, a) < r + self.radius

    def draw(self, screen):
        r = self.radius
        x, y = self.pos[0] - r, self.pos[1] - r
        pygame.draw.ellipse(screen, self.color(), pygame.Rect(x, y, 2 * r, 2 * r))
        x, y = self.target[0] - r, self.target[1] - r
        pygame.draw.ellipse(screen, 'Lightgrey', pygame.Rect(x, y, 2 * r, 2 * r), 2)

    def move(self, dt, objects):
        pos = self.pos
        self.pos = (self.pos[0] + dt * self.vel[0], self.pos[1] + dt * self.vel[1])
        self.state = 0
        if self.is_collided(objects):
            self.state = 1
            self.pos = pos

    def is_collided(self, objects):
        for obj in objects:
            if obj == self:
                continue
            if obj.check_collision(self.pos, self.radius):
                return True
        return False

    def color(self):
        if distance(self.pos, self.target) < self.radius / 5:
            return "Green"
        return self.initcolor
    
    def _nearest_entity_position(self, obstacles, robots, room):
        """ координаты ближайшего объекта (препятствия, робота или стены) """
        x, y = self.pos
        r = self.radius

        nearest = None
        min_dist = float('inf')

        # Препятствия
        for ob in obstacles:
            d = ob.dist(self.pos)
            if d < min_dist:
                min_dist = d
                px = clamp(ob.pos[0], ob.pos[0] + ob.size[0], x)
                py = clamp(ob.pos[1], ob.pos[1] + ob.size[1], y)
                nearest = (px, py)

        # Другие роботы
        for rob in robots:
            if rob is self:
                continue
            d = distance(self.pos, rob.pos) - rob.radius - r
            if d < min_dist:
                min_dist = d
                nearest = rob.pos

        # Стенки комнаты
        walls = [
            (r, y),  
            (room.size[0] - r, y), 
            (x, r), 
            (x, room.size[1] - r) 
        ]
        for wx, wy in walls:
            d = distance(self.pos, (wx, wy))
            if d < min_dist:
                min_dist = d
                nearest = (wx, wy)

        return nearest


    def _compute_feature(self, prev_vel, obstacles, robots, room):
        "Формирует вектор признаков (feature vector) для обучения или предсказания ESN."
        nearest = self._nearest_entity_position(obstacles, robots, room)
        return np.array([
            self.pos[0], self.pos[1],
            self.target[0], self.target[1],
            prev_vel[0], prev_vel[1],
            nearest[0], nearest[1]
        ]).reshape(-1)


    def train_esn(self, room, obstacles, robots, dt):
        "Обучает ESN на основе случайного движения робота в течение `min_samples` шагов."
        p = self.pos
        r = self.radius
        for _ in range(self.min_samples):
            prev_vel = self.vel

            if distance(self.pos, self.target) < self.radius / 20:
                """ цель достигнута """
                self.vel = (0, 0)
            elif self.state == 1:
                """ столкновение - меняем скорость на случайную """
                self.vel = rotate((self.v0, 0), random.uniform(0, 2 * math.pi))
            else:
                self.vel = diff(self.target, self.pos) 

            self.move(dt,obstacles + robots + [room])

            feat = self._compute_feature(prev_vel, obstacles, robots, room)
            self.train_inputs.append(feat)
            self.train_outputs.append(self.vel)

            l = norm(self.vel)
            if l > self.vmax:
                self.vel = (self.vel[0] / l * self.vmax,
                        self.vel[1] / l * self.vmax)
                
        X = np.array(self.train_inputs)
        Y = np.array(self.train_outputs)
        self.esn.fit(X, Y, reg=1e-5)
        # После обучения, возвращаем роботов в начало
        self.state = 0
        self.pos = p
        self.radius = r


    def update(self, room, obstacles, robots):
        "Обновление скорости на основе предсказания ESN"
        prev_vel = self.vel

        if distance(self.pos, self.target) < self.radius / 20:
            self.vel = (0.0, 0.0)
            return

        feat = self._compute_feature(prev_vel, obstacles, robots, room)

        pred = self.esn.predict(feat)
        self.vel = (float(pred[0]), float(pred[1]))

        # ограничим по максимальной скорости
        l = norm(self.vel)
        if l > self.vmax:
            self.vel = (self.vel[0] / l * self.vmax,
                        self.vel[1] / l * self.vmax)
