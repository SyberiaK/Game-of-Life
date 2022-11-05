import os
import time


class Field:
    class Cell:
        DEAD = 0
        ALIVE = 1

        def __init__(self, pos_x: int, pos_y: int, state: int = DEAD):
            if state not in (self.DEAD, self.ALIVE):
                raise ValueError('Cell can only be DEAD (0) or ALIVE (1)')
            self.__pos = self.__pos_x, self.__pos_y = pos_x, pos_y
            self.__state = state

        def get_pos(self): return self.__pos
        def get_pos_x(self): return self.__pos_x
        def get_pos_y(self): return self.__pos_y

        def get_state(self): return self.__state

        def set_state(self, state: int):
            if state not in (self.DEAD, self.ALIVE):
                raise ValueError('Cell can only be DEAD (0) or ALIVE (1)')
            self.__state = state

    def __init__(self, size_x: int = 25, size_y: int = 25):
        self.__size = self.__size_x, self.__size_y = size_x, size_y
        self.matrix = [[self.Cell(x, y) for x in range(size_x)] for y in range(size_y)]
        self.buffer = ...

    def get_size(self): return self.__size
    def get_size_x(self): return self.__size_x
    def get_size_y(self): return self.__size_y

    def alive_nearby(self, cell: Cell):
        x, y = cell.get_pos()
        max_x, max_y = self.get_size()

        an = 0
        for ry in range(-1, 2):
            for rx in range(-1, 2):
                if (ry, rx) != (0, 0) and \
                        self.matrix[(y + ry) % max_y][(x + rx) % max_x].get_state() == self.Cell.ALIVE:
                    an += 1
        return an

    def check_cell(self, cell: Cell):
        state = cell.get_state()
        an = self.alive_nearby(cell)

        if (state == 0 and an == 3) or (state == 1 and an in (2, 3)):
            return self.Cell.ALIVE
        return self.Cell.DEAD

    def step(self):
        self.buffer = [[self.Cell(x, y) for x in range(self.__size_x)] for y in range(self.__size_y)]

        for y, row in enumerate(self.matrix):
            for x, cell in enumerate(row):
                state = self.check_cell(cell)
                self.buffer[y][x].set_state(state)

        self.matrix = self.buffer[:]

    def get_alives(self):
        alives = []
        for y, row in enumerate(self.matrix):
            if all(c.get_state == self.Cell.DEAD for c in row):
                continue
            for x, cell in enumerate(row):
                if cell.get_state() == self.Cell.ALIVE:
                    alives.append((x, y))

        return alives