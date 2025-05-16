import pygame, json
from sys import exit

from room import Room
from robot_esn import Robot
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
    font = pygame.font.SysFont('Arial', 18)

    room = Room(data["size"], data["colors"]["room"])

    obstacles = []
    for ob in data["obstacles"]:
        obstacles.append(Obstacle(*ob, data["colors"]["obstacle"]))

    robots = []
    for rb in data["robots"]:
        robots.append(Robot(*rb, data["rsize"], data["colors"]["robot"]))

    objects = [room] + obstacles + robots

    count = data['fps']
    start_ticks = pygame.time.get_ticks()
    goals_reached = 0

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

        goals_reached = sum(rob.reached_target() for rob in robots)
        screen.fill(data["colors"]["room"]) 

        for obj in objects:
            obj.draw(screen)

        elapsed_ms = pygame.time.get_ticks() - start_ticks
        elapsed_sec = elapsed_ms / 1000

        efficiency = goals_reached / elapsed_sec if elapsed_sec > 0 else 0

        stats_text = f"Достигнуто целей: {goals_reached} | Время: {elapsed_sec:.1f} с | Эффективность: {efficiency:.3f} целей/с"
        text_surface = font.render(stats_text, True, (0, 0, 0))
        screen.blit(text_surface, (10, 10))
        
        count -= 1
        if count < 0:
             count = data['fps']

        pygame.display.update()
        clock.tick(data["fps"])

#main("simple")
main(mission_circle(10))
#main(mission_circle_hole(2))