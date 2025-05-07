import pygame, json
from sys import exit

from room import Room
from robot_simple import Robot
from obstacle import Obstacle
from missions import mission_circle, mission_circle_hole

def main(mission):
    pygame.init()

    if type(mission) == str:
        """ загрузка миссии из файла """
        with open(f"{mission}.json", encoding="utf-8") as f:
            data = json.load(f)
    else:
        data = mission() 

    screen = pygame.display.set_mode(data["size"])
    clock = pygame.time.Clock()
    dt = 1 / data["fps"]

    room = Room(data["size"], data["colors"]["room"])

    obstacles = []
    for ob in data["obstacles"]:
        obstacles.append(Obstacle(*ob, data["colors"]["obstacle"]))

    robots = []
    for rb in data["robots"]:
        robots.append(Robot(*rb, data["rsize"], data["colors"]["robot"]))

    objects = [room] + obstacles + robots

    count = data['fps']

    while True:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                exit()

        if count == 0:
            """ обновляем скорость (управление) раз в секунду (один раз в fps тиков) """
            for rob in robots:
                rob.update(room, obstacles, robots)

        """ обновляем положение fps на каждом тике """
        for rob in robots:
            rob.move(dt, objects)

        for obj in objects:
            obj.draw(screen)
        
        count -= 1
        if count < 0:
            count = data['fps']

        pygame.display.update()
        clock.tick(data["fps"])

#main("simple")
#main(mission_circle(20))
main(mission_circle_hole(20))