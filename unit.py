import math


class unit:
    def __init__(self, size, loc_x: float, loc_y: float, chase=False,
                 movespeed=15):
        self.size = size
        self.loc = [loc_x, loc_y]
        self.path = []
        self.movespeed = movespeed
        self.chase = chase

    def move(self, move_decrease=0.0):
        if len(self.path) == 0:
            return
        dx = self.path[0][0] - self.loc[0]
        dy = self.path[0][1] - self.loc[1]
        distance = math.sqrt(dx * dx + dy * dy)


        if distance < self.movespeed - move_decrease:
            self.loc = self.path[0]
            self.path.pop(0)
            self.move(move_decrease=move_decrease + distance)

        else:
            self.loc = (
                self.loc[0] + (dx / distance) * (
                            self.movespeed - move_decrease),
                self.loc[1] + (dy / distance) * (
                            self.movespeed - move_decrease))
        return
