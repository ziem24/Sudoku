import random
from time import perf_counter

'''
BENCHMARK BOARD: 'very very hard'
    Previous solver: 35 - 40s
    BLAZINGLY FAST solver: 2.5 - 2.7s

BENCHMARK BOARD: 'wikipedia anti bf'
    Previous solver: ~ 800s
    BLAZINGLY FAST solver: ~ 65s
    MRV solver:
'''


class Board():
    def __init__(self):
        self.board = [0] * 81
        self.c_row = [i // 9 for i in range(81)]
        self.c_col = [9 + i % 9 for i in range(81)]
        self.c_reg = [18 + (i // 27 * 3) + (i % 9 // 3) for i in range(81)]
        self.use_MRV = False
        self.use_LCV = False

    def __repr__(self) -> list[int]:
        return self.board

    def __str__(self) -> str:
        string = ''
        for row in range(3):
            for col in range(9):
                offset = col * 3 + row * 27
                string += f'{self.board[offset]} {self.board[offset + 1]} {self.board[offset + 2]}'
                string += (' | ' if (col + 1) % 3 else '\n')
            string += ('——————+———————+——————\n' if row != 2 else '')

        return string.replace('0', '.')

    def __getitem__(self, key: int) -> int:
        return self.board[key]

    def __setitem__(self, key: int, value: int):
        self.board[key] = value

    def is_cell_valid(self, key: int, value: int) -> bool:
        # EXPERIMENT: RCB: 677k, RBC: 607k, CRB: 714k, CBR: 665k, BRC: 542k, BCR: 544k [iter/s]
        r = key // 9
        c = key % 9
        b = 27 * (r // 3) + 3 * (c // 3)
        row = (self.board[9 * r + i] for i in range(9))
        column = (self.board[9 * i + c] for i in range(9))
        box = (self.board[9 * (i // 3) + b + i % 3] for i in range(9))

        return not (value in column or value in row or value in box)  # CRB: 714k, the fastest way probably

    def heuristic_MRV(self, zeros: list[int], masks: list[int]):
        candidates = [masks[self.c_row[i]] & masks[self.c_col[i]] & masks[self.c_reg[i]] for i in zeros]
        candidate_pairs = [(bin(i).count('1'), j) for i, j in zip(candidates, zeros)]
        return [c[1] for c in sorted(candidate_pairs)]

    # WARNING: BLAZINGLY FAST !!!
    def solve(self, random_gen: bool = False) -> tuple[int, float]:
        time_start = perf_counter()
        if 0 not in self.board:
            return (0, 0.0001)

        n = 1
        counter = 0
        masks = [0x3FE] * 27
        mask_history = [0x3FE] * 81

        for i in range(81):
            bit_shift = ~(1 << self.board[i])
            masks[self.c_row[i]] &= bit_shift
            masks[self.c_col[i]] &= bit_shift
            masks[self.c_reg[i]] &= bit_shift

        if random_gen:
            zeros = list(range(81))
            zero_ptr = zeros.index(self.board.index(0))
        else:
            zeros = [key for key, value in enumerate(self.board) if value == 0]
            zero_ptr = 0
            if self.use_MRV:
                zeros = self.heuristic_MRV(zeros, masks)

        current = zeros[zero_ptr]
        max_zero_ptr = len(zeros) - 1

        while 0 <= zero_ptr <= max_zero_ptr:
            counter += 1
            possible = (
                mask_history[current]
                & masks[self.c_row[current]]
                & masks[self.c_col[current]]
                & masks[self.c_reg[current]]
            )  # THANK YOU FLAKE8

            if possible:
                n = bin(possible)[::-1].index('1')  # __builtin_ctz(possible)
                self.board[current] = n

                bit_shift = ~(1 << n)
                mask_history[current] &= bit_shift
                masks[self.c_row[current]] &= bit_shift
                masks[self.c_col[current]] &= bit_shift
                masks[self.c_reg[current]] &= bit_shift

                zero_ptr += 1
                if zero_ptr > max_zero_ptr:
                    break
                current = zeros[zero_ptr]
            else:
                mask_history[current] = 0x3FE
                zero_ptr -= 1
                if zero_ptr < 0:
                    break
                current = zeros[zero_ptr]
                n = self.board[current]
                self.board[current] = 0

                bit_shift = 1 << n
                masks[self.c_row[current]] |= bit_shift
                masks[self.c_col[current]] |= bit_shift
                masks[self.c_reg[current]] |= bit_shift

        if n <= 9:
            return (counter, (perf_counter() - time_start))
        else:
            return (None, None)

    def generate_random(self, perc: int):
        self.board = [0] * 81
        candidates = ['Rajski ogród']
        filled_cells = []

        while candidates and self.board[80] == 0:
            filled_cells.append(self.board.index(0))
            current = filled_cells[-1]
            candidates = [i for i in range(1, 10) if self.is_cell_valid(current, i)]
            self.board[current] = random.choice(candidates) if candidates else 0

        self.solve(random_gen=True)
        # self.board = [0 if random.randint(1, 100) > int(perc) else i for i in self.board]

    def import_(self, string: str) -> bool:
        if len(string) != 81 or not string.isdigit():
            return False

        self.board, old_grid = [int(i) for i in string], self.board
        for key in range(81):
            value, self.board[key] = self.board[key], 0
            bool_valid = self.is_cell_valid(key, value) or not value
            self.board[key] = value
            if not bool_valid:
                self.board = old_grid
                return False

        return True

    def export(self) -> str:
        return ''.join(str(i) for i in self.board)

    def clear(self):
        self.board = [0] * 81


if __name__ == "__main__":
    board = Board()
    board.board = [int(i) for i in "020000300000000010000400009203048090600000800890000000300007902702000401000000000"]
    print(str(board))
    board.generate_random(100)
    print(str(board))
