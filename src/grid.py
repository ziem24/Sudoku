import random
from time import perf_counter


class Grid():
    def __init__(self):
        self.grid = [0] * 81

    def __repr__(self) -> str:
        string = ''
        for row in range(3):
            for col in range(9):
                offset = col * 3 + row * 27
                string += f'{self.grid[offset]} {self.grid[offset + 1]} {self.grid[offset + 2]}'
                string += (' | ' if (col + 1) % 3 else '\n')
            string += ('——————+———————+——————\n' if row != 2 else '')

        return string.replace('0', '.')

    def __getitem__(self, key: int) -> int:
        return self.grid[key]

    def __setitem__(self, key: int, value: int):
        self.grid[key] = value

    def is_cell_valid(self, key: int, value: int) -> bool:
        # EXPERIMENT: RCB: 677k, RBC: 607k, CRB: 714k, CBR: 665k, BRC: 542k, BCR: 544k [iter/s]
        r = key // 9
        c = key % 9
        b = 27 * (r // 3) + 3 * (c // 3)
        row = (self.grid[9 * r + i] for i in range(9))
        column = (self.grid[9 * i + c] for i in range(9))
        box = (self.grid[9 * (i // 3) + b + i % 3] for i in range(9))

        return not (value in column or value in row or value in box)  # CRB: 714k, the fastest way probably

    def solve(self, preserve_placed: bool = True) -> tuple[int, float]:
        if 0 not in self.grid:
            return (0, 0.0001)

        if preserve_placed:
            cell_stack = [self.grid.index(0)]
        else:  # i dont remember why it even works
            cell_stack = [index for index, cell_value in enumerate(self.grid) if cell_value]

        last_zero = 80 - list(self.grid[::-1]).index(0)
        counter = 0
        n = 1
        time_start = perf_counter()

        while self.grid[last_zero] == 0 and n <= 9:
            current = cell_stack[-1]
            counter += 1

            if self.is_cell_valid(current, n):
                self.grid[current], n = n, 1
                if self.grid[last_zero] == 0:
                    cell_stack.append(self.grid.index(0))
            else:
                while n == 9 and len(cell_stack) > 1:
                    cell_stack.pop(-1)
                    current = cell_stack[-1]
                    n, self.grid[current] = self.grid[current], 0
                n += 1

        if n <= 9:
            return (counter, (perf_counter() - time_start))
        else:
            return (None, None)

    def generate_random(self, perc: int):
        self.grid = [0] * 81
        candidates = ['Rajski ogród']
        filled_cells = []

        while candidates and self.grid[80] == 0:
            filled_cells.append(self.grid.index(0))
            current = filled_cells[-1]
            candidates = [i for i in range(1, 10) if self.is_cell_valid(current, i)]
            self.grid[current] = random.choice(candidates) if candidates else 0

        self.solve(preserve_placed=False)
        self.grid = [0 if random.randint(1, 100) > int(perc) else i for i in self.grid]

    def import_(self, string: str) -> bool:
        if len(string) != 81 or not string.isdigit():
            return False

        self.grid, old_grid = [int(i) for i in string], self.grid
        for key in range(81):
            value, self.grid[key] = self.grid[key], 0
            bool_valid = self.is_cell_valid(key, value) or not value
            self.grid[key] = value
            if not bool_valid:
                self.grid = old_grid
                return False

        return True

    def export(self) -> str:
        return ''.join(str(i) for i in self.grid)

    def clear(self):
        self.grid = [0] * 81
