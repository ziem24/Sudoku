import platform
from src import tk, MainGUI


class Cell(tk.Button):
    def __init__(self, master: tk.Frame, gui: MainGUI, index: int):
        width = {'Linux': 1, 'Windows': 2}.get(platform.uname().system, 1)
        super().__init__(width=width, height=1, master=master, text=' ', command=self.on_click)

        self._gui = gui
        self._board = gui.main_board
        self.index = index
        # scary math to see if it's in an odd-numbered sector
        self.uses_color_1 = bool((3 * (index // 27) + index % 9 // 3) % 2)
        self.configure(disabledforeground='black')
        self.bind('<KeyPress>', self.new_value)

    def on_click(self):
        self._gui.set_info_text('empty')
        self.focus_set()

    def new_value(self, event=None):
        if event.char.isdigit():
            if event.char == '0':
                self._gui.set_info_text('empty')
                self._board[self.index] = 0
                self['text'] = ' '
            elif self._board.is_cell_valid(self.index, int(event.char)):
                self._gui.set_info_text('empty')
                self._board[self.index] = int(event.char)
                self['text'] = event.char
            else:
                self._gui.set_info_text('invalid', event.char)

    def set_bg_color(self, color_1, color_2):
        self['bg'] = color_1 if self.uses_color_1 else color_2


class BoardFrame(tk.Frame):
    def __init__(self, gui: MainGUI):
        super().__init__()
        self._gui = gui
        self._board = gui.main_board
        self.cells = []

        for index in range(81):
            cell = Cell(self, gui, index)
            cell.grid(row=index // 9, column=index % 9)
            self.cells.append(cell)

    def set_state(self, state: str):
        for cell in self.cells:
            cell['state'] = state

    def set_theme(self, color_1: str, color_2: str):
        for cell in self.cells:
            cell.set_bg_color(color_1, color_2)

    def update_all(self):
        for index, cell in enumerate(self.cells):
            cell['text'] = self._board[index] if self._board[index] else ' '

    def update_after_solve(self, pre_solve_state: list[int]):
        for index, cell in enumerate(self.cells):
            cell['disabledforeground'] = 'black' if pre_solve_state[index] else 'blue'
            cell['text'] = self._board[index] if self._board[index] else ' '
