from random import random

import pygame
from pygame import QUIT
from unit import unit
from shapely.geometry import LineString, Polygon, Point
from draw import *
from draw import obstacle as Obstacle

pygame.init()
screen = pygame.display.set_mode((800, 600))
pygame.display.set_caption('Obstacles and Units')

maze = """
1111111111
1001000001
1011011101
1010000101
1010110101
1000100001
1110111101
1000000101
1011110101
1111111101
"""
obstacle_list = []
obstacle_list = []
for i, line in enumerate(maze.split()):
    for j, type in enumerate(line):
        print(type)
        if type == "1":
            obstacle_list.append(obstacle(i * 50 + 100, j * 50 + 100, 50, 50))

print("asd", obstacle_list)
enemy_list = []
# enemy_list = [unit(3, 0, 0, movespeed=5, chase=True),
#               unit(3, 1000, 1000, movespeed=4, chase=True),
#               unit(3, 0, 0, movespeed=6, chase=True),
#               unit(3, 0, 0, movespeed=3, chase=True)]

unit_list = [unit(3, 0, 0, movespeed=5)]
unit_list.extend(enemy_list)
temp_node = create_temp_nodes(obstacle_list, offset= 5)
temp_node = remove_redundant(temp_node, obstacle_list, offset= 6)
visibility = create_visibility_graph(temp_node, obstacle_list)
visibility_list = tuple(visibility.keys())
print(visibility)
running = True

destination = (1000, 1000)
tick = 0
clock = pygame.time.Clock()
frame_rate = 100
update_check = 10
count = 0

moving = True
while running:
    start_time = pygame.time.get_ticks()

    for event in pygame.event.get():
        if event.type == QUIT:
            running = False
        elif event.type == pygame.MOUSEBUTTONDOWN:
            if event.button == 1:  # Left mouse button
                x, y = event.pos
                path(unit_list[0], visibility, visibility_list, obstacle_list,
                     temp_node,
                     (x, y))
        elif event.type == pygame.KEYDOWN:
            if event.key == pygame.K_q:
                mouse_x, mouse_y = pygame.mouse.get_pos()
                unit_list[0].loc = (mouse_x, mouse_y)
            elif event.key == pygame.K_SPACE:
                moving = not moving
    unit_list[0].move()
    if moving:
        for units in unit_list[1:]:
            units.move()
    tick += 1
    if tick == update_check:
        tick = 0

    start_index = tick
    while start_index < len(enemy_list):
        path(enemy_list[start_index], visibility, visibility_list,
             obstacle_list,
             temp_node,
             tuple(unit_list[0].loc))
        start_index += update_check

    draw(obstacle_list, unit_list, temp_node, visibility, screen)
    elapsed_time = pygame.time.get_ticks() - start_time
    wait_time = max(0, int(1000 / frame_rate - elapsed_time))
    pygame.time.delay(wait_time)
    if wait_time == 0:
        count += elapsed_time - 1000 / frame_rate
        print(count)

pygame.quit()
