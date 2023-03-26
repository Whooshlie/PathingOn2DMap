import pygame
from pygame import QUIT
from unit import unit
from shapely.geometry import LineString, Polygon, Point
from collections import defaultdict
from math import sqrt
from queue import PriorityQueue
import copy


def euclidean_distance(p1, p2):
    return sqrt((p1[0] - p2[0]) ** 2 + (p1[1] - p2[1]) ** 2)


class obstacle():
    def __init__(self, x, y, size_x, size_y):
        self.loc = (x - size_x / 2, y - size_y / 2)
        self.size = (size_x, size_y)
        self.polygon = Polygon([
            (self.loc[0], self.loc[1]),
            (self.loc[0] + size_x, self.loc[1]),
            (self.loc[0] + size_x, self.loc[1] + size_y),
            (self.loc[0], self.loc[1] + size_y)
        ])

    def is_inside(self, point):
        return self.polygon.contains(Point(point))


def point_inside(point, obstacle_list):
    for obstacle_node in obstacle_list:
        if obstacle_node.is_inside(point):
            return True
    return False


def remove_redundant(temp_node, obstacle_list, offset=6):
    new_temp_node = []
    lst = [(offset, offset), (offset, -offset), (-offset, offset),
           (-offset, -offset)]
    for node in temp_node:
        check = 0
        for line in lst:
            x = node[0] + line[0]
            y = node[1] + line[1]
            if point_inside((x, y), obstacle_list):
                check += 1
        if check < 2:
            new_temp_node.append(node)
    return new_temp_node

def reconstruct_path(came_from, current):
    path = [current]
    while current in came_from:
        current = came_from[current]
        path.append(current)
    return path[::-1]


def a_star(start, goal, visibility_graph):
    open_set = PriorityQueue()
    open_set.put((0, start))

    came_from = {}
    g_score = {node: float("inf") for node in visibility_graph}
    g_score[start] = 0

    f_score = {node: float("inf") for node in visibility_graph}
    f_score[start] = euclidean_distance(start, goal)

    while not open_set.empty():
        _, current = open_set.get()

        if current == goal:
            return reconstruct_path(came_from, current)

        for neighbor, distance in visibility_graph[current].items():
            tentative_g_score = g_score[current] + distance

            if tentative_g_score < g_score[neighbor]:
                came_from[neighbor] = current
                g_score[neighbor] = tentative_g_score
                f_score[neighbor] = g_score[neighbor] + euclidean_distance(
                    neighbor, goal)
                open_set.put((f_score[neighbor], neighbor))

    return []  # No path found

def path(unit_check: unit, vis_list, vis_start, obs_list, temp_nod,
         destination):

    if can_draw_line(unit_check.loc, destination, obs_list):
        unit_check.path = [destination]
        return
    elif len(unit_check.path) > 1 and can_draw_line(unit_check.path[-2], destination, obs_list):
        unit_check.path[-1] = destination
        return

    updated_visibility_graph = add_temporary_nodes_to_graph(vis_list, temp_nod,
                                                            [(unit_check.loc[0],
                                                              unit_check.loc[
                                                                  1]),
                                                             destination],
                                                            obs_list)

    pathing = a_star((unit_check.loc[0], unit_check.loc[1]), destination,
                     updated_visibility_graph)

    unit_check.path = pathing


def add_temporary_nodes_to_graph(graph, temp_nodes, new_nodes, obstacle_list):
    updated_graph = copy.deepcopy(graph)
    updated_new = []
    for new_node in new_nodes:
        for temp_node in temp_nodes:
            if can_draw_line(new_node, temp_node, obstacle_list):
                distance = euclidean_distance(new_node, temp_node)
                updated_graph[new_node][temp_node] = distance
                updated_graph[temp_node][new_node] = distance
        for temp_node in updated_graph:
            if can_draw_line(new_node, temp_node, obstacle_list):
                distance = euclidean_distance(new_node, temp_node)
                updated_graph[new_node][temp_node] = distance
                updated_graph[temp_node][new_node] = distance
        updated_new.append(new_node)
    return updated_graph


def can_draw_line(p1, p2, obstacle_list):
    line = LineString([p1, p2])
    for obstacles in obstacle_list:
        if line.intersects(obstacles.polygon):
            return False
    return True


def create_visibility_graph(temp_nodes, obstacle_list):
    graph = defaultdict(dict)
    for i, node1 in enumerate(temp_nodes):
        for j, node2 in enumerate(temp_nodes):
            if i != j and can_draw_line(node1, node2, obstacle_list):
                distance = euclidean_distance(node1, node2)
                graph[node1][node2] = distance
                graph[node2][node1] = distance
    return graph


def draw(obstacle_list, unit_list, temp_node, visibility_graph, screen):
    screen.fill((255, 255, 255))  # Clear the screen with a white background

    # Draw obstacles
    for obstacles in obstacle_list:
        pygame.draw.rect(screen, (0, 0, 255),
                         pygame.Rect(obstacles.loc[0], obstacles.loc[1],
                                     obstacles.size[0], obstacles.size[1]))
    for temp in temp_node:
        pygame.draw.circle(screen, (0, 255, 0), temp, 3)

    for node1, connections in visibility_graph.items():
        for node2 in connections:
            pygame.draw.line(screen, (0, 0, 255), node1, node2, 1)

    # Draw units
    for units in unit_list:
        pygame.draw.circle(screen, (255, 0, 0), units.loc, units.size)
        if len(units.path) != 0:
            pygame.draw.line(screen, (0, 255, 255), units.path[0], units.loc, 1)

        for i in range(1, len(units.path)):
            pygame.draw.line(screen, (0, 255, 255), units.path[i],
                             units.path[i - 1], 1)
            pygame.draw.circle(screen, (0, 255, 255), units.path[i], 3)

    pygame.display.flip()  # Update the display


def create_temp_nodes(obstacle_list, offset=5):
    temp_nodes = []

    for obstacles in obstacle_list:
        x = obstacles.loc[0] - offset
        y = obstacles.loc[1] - offset
        size_x = obstacles.size[0] + 2 * offset
        size_y = obstacles.size[1] + 2 * offset
        temp_nodes.extend([(x, y), (x + size_x, y), (x, y + size_y),
                           (x + size_x, y + size_y)])
    valid_temp_nodes = []

    for temp_node in temp_nodes:
        inside_obstacle = False

        for obstacle_node in obstacle_list:
            if obstacle_node.is_inside(temp_node):
                inside_obstacle = True
                break

        if not inside_obstacle:
            valid_temp_nodes.append(temp_node)

    return valid_temp_nodes
