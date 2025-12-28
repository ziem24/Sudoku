import json
import platform
import tkinter as tk
from src.board import Board
from src.windows import SaveWindow, ImportWindow, ExportWindow, RenameWindow, DeleteWindow, RandomWindow


class MainGUI(tk.Tk):
    def __init__(self):
        super().__init__()

        self.resizable(False, False)
        self.config(padx=15, pady=15)
        self.title('Sudoku v2.0')
        self.protocol('WM_DELETE_WINDOW', self.on_close_mainWindow)
        self.current_state = 'normal'
        self.current_theme = -1  # incremented to 0 when calling set_next_theme
        self.opened_window = None
        self.main_board = Board()

        with open('src/_themes.json', 'r') as f:
            self.themes = json.load(f)

        self.board_frame = BoardFrame(self)
        self.board_frame.grid(row=0, column=0, padx=15, sticky='n')
        self.pattern_frame = PatternFrame(self)
        self.pattern_frame.grid(row=0, column=1, padx=15, sticky='n')
        self.action_frame = ActionButtonFrame(self)
        self.action_frame.grid(row=0, column=2, padx=15, sticky='n')
        self.config_frame = ConfigFrame(self)
        self.config_frame.grid(row=0, column=3, padx=15, sticky='n')
        self.info_label = tk.Label(self)
        self.info_label.grid(row=1, columnspan=4, pady=15)

        self.set_next_theme()
        self.set_info_text('init')
        self.set_states_on_event('normal')

    def set_next_theme(self):
        self.current_theme += 1
        self.current_theme %= len(self.themes)
        self.set_info_text('theme_change')
        theme = self.themes[self.current_theme]
        new_bg = theme['bg']

        self['bg'] = new_bg
        self.info_label['bg'] = new_bg

        self.board_frame.set_theme(theme['cells_1'], theme['cells_2'])
        self.action_frame.set_theme(new_bg)
        self.pattern_frame.set_theme(new_bg)
        self.config_frame.set_theme(new_bg)

    def set_states_on_event(self, new_state: str):
        self.state = new_state
        self.action_frame.bt_manual['state'] = 'disabled'  # REMOVE THIS FUCKING FUCK WHEN YOU BUILD THE MANUAL

        if new_state == 'normal':  # clear, undo solve, close window
            self.board_frame.set_state('normal')
            self.action_frame.set_states('disabled', ['undo'])
            self.config_frame.set_state('normal')
            self.pattern_frame.set_state('normal')

        elif new_state == 'solve':
            self.board_frame.set_state('disabled')
            self.action_frame.set_states('normal', ['save', 'export', 'undo', 'clear', 'theme', 'manual'])
            self.config_frame.set_state('disabled')
            self.pattern_frame.set_state('disabled')

        elif new_state == 'open_win':
            self.board_frame.set_state('disabled')
            self.action_frame.set_states('normal', [])
            self.config_frame.set_state('disabled')
            self.pattern_frame.set_state('disabled')

    def set_info_text(self, key: str, *args):
        args_0 = args[0] if len(args) >= 1 else None
        args_1 = args[1] if len(args) >= 2 else None
        args_2 = f'{args[2]:.1f}' if len(args) >= 3 else None

        label_dictionary = {
            'empty': '',
            'init': 'Click on a cell and press a number 0-9 on your keyboard to place it.',
            'invalid': f'{args_0} is not valid in this location!',
            'theme_change': f'{self.themes[self.current_theme]['name']} theme selected.',
            'board_clear': 'The board has been cleared.',
            'board_undo': 'Returned the board to its unsolved state.',
            'board_solve': f'Solved in {args_0} iteration(s) and {args_1}s ({args_2} iterations/s)',
            'board_fail': 'idk man seems kinda sus to me',
            'pattern_load': f'Loaded \'{args_0}\'.',
            'pattern_random': 'Generated a randomized sudoku.',
            'pattern_import': 'Imported a sudoku pattern.',
            'pattern_save': f'Saved this pattern as \'{args_0}\'.',
            'pattern_rename': f'Renamed \'{args_0}\' to \'{args_1}\'.',
            'pattern_del_confirm': f'Deleted \'{args_0}\'.',
            'pattern_del_cancel': 'Deletion cancelled.'
            }
        self.info_label['text'] = label_dictionary[key]

    def on_close_mainWindow(self):
        self.destroy()
        if self.opened_window is not None:
            self.opened_window.destroy()


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


class ActionButton(tk.Button):
    def __init__(self, master: tk.Frame, text: str, row: int, column: int, command: callable):
        super().__init__(master=master, text=text, command=command, width=10)
        self.grid(row=row, column=column+1, padx=5, pady=5)


class ActionButtonFrame(tk.Frame):
    def __init__(self, gui: MainGUI):
        super().__init__()

        self._gui = gui
        self._board = gui.main_board
        self._board_frame = gui.board_frame
        self._pt_listbox = gui.pattern_frame
        self.pre_solve_board = [0] * 81
        self.selected_pattern = None

        self.settings_label = tk.Label(self, text='Actions:')
        self.settings_label.grid(column=1, columnspan=2)

        self.empty_label = tk.Label(self, text=' ')
        self.empty_label.grid(row=4, columnspan=2)

        self.bt_save = ActionButton(self, 'Save as', 1, 0, lambda: SaveWindow(self._gui))
        self.bt_load = ActionButton(self, 'Load', 1, 1, self.on_press_load)
        self.bt_import = ActionButton(self, 'Import', 2, 0, lambda: ImportWindow(self._gui))
        self.bt_export = ActionButton(self, 'Export', 2, 1, lambda: ExportWindow(self._gui))
        self.bt_rename = ActionButton(self, 'Rename', 3, 0, lambda: self.open_onListbox(RenameWindow))
        self.bt_delete = ActionButton(self, 'Delete', 3, 1, lambda: self.open_onListbox(DeleteWindow))
        self.bt_solve = ActionButton(self, 'Solve', 5, 0, self.on_press_solve)
        self.bt_random = ActionButton(self, 'Random', 5, 1, lambda: RandomWindow(self._gui))
        self.bt_undo = ActionButton(self, 'Undo solve', 6, 0, self.on_press_undo)
        self.bt_clear = ActionButton(self, 'Clear', 6, 1, self.on_press_clear)
        self.bt_theme = ActionButton(self, 'Next theme', 7, 0, self._gui.set_next_theme)
        self.bt_manual = ActionButton(self, 'Manual', 7, 1, lambda: None)

    def set_theme(self, bg: str):
        self['bg'] = bg
        self.settings_label['bg'] = bg
        self.empty_label['bg'] = bg

    def set_states(self, state: str, new_state_buttons: list[str] = []):
        opposite_state = 'disabled' if state == 'normal' else 'normal'
        all_buttons = {
            'save': self.bt_save,
            'load': self.bt_load,
            'import': self.bt_import,
            'export': self.bt_export,
            'rename': self.bt_rename,
            'delete': self.bt_delete,
            'solve': self.bt_solve,
            'random': self.bt_random,
            'undo': self.bt_undo,
            'clear': self.bt_clear,
            'theme': self.bt_theme,
            'manual': self.bt_manual
            }

        for bt_name in all_buttons:
            all_buttons[bt_name]['state'] = state if bt_name in new_state_buttons else opposite_state

    def open_onListbox(self, new_window: tk.Tk):
        self.selected_pattern = self._pt_listbox.get_selection()
        if self.selected_pattern is not None:
            new_window(self._gui)

    def on_press_load(self):
        self.selected_pattern = self._pt_listbox.get_selection()
        if self.selected_pattern is not None:
            loaded_board = self._pt_listbox.patterns[self.selected_pattern]
            self._gui.set_info_text('pattern_load', self.selected_pattern)
            self._board.import_(loaded_board)
            self._board_frame.update_all()
            self._pt_listbox.unfocus()

    def on_press_solve(self):
        self.pre_solve_board = self._board.board.copy()  # copying values instead of a reference (important!!)
        count, dt = self._board.solve()
        if (count, dt) != (None, None):
            self._gui.set_info_text('board_solve', count, f'{dt:.3f}', count/dt)
            self._gui.set_states_on_event('solve')
            self._board_frame.update_after_solve(self.pre_solve_board)
        else:
            self._gui.set_info_text('board_fail')
        self._pt_listbox.unfocus()

    def on_press_clear(self):
        self._gui.set_states_on_event('normal')
        self._gui.set_info_text('board_clear')
        self._board.clear()
        self._board_frame.update_all()
        self._pt_listbox.unfocus()

    def on_press_undo(self):
        self._gui.set_states_on_event('normal')
        self._gui.set_info_text('board_undo')
        self._board.board, self.pre_solve_board = self.pre_solve_board, [0] * 81
        self._board_frame.update_all()
        self._pt_listbox.unfocus()


class PatternFrame(tk.Frame):
    def __init__(self, gui: MainGUI):
        super().__init__()

        self._gui = gui
        self.pattern_label = tk.Label(self, text='Your saved patterns:')
        self.pattern_label.grid(sticky='n')
        self.listbox = tk.Listbox(self, height=15)
        self.listbox.grid(row=1)

        with open('database.json', 'r') as f:
            self.patterns = json.load(f)
        self.update_patterns()

    def set_state(self, state: str):
        self.listbox['state'] = state

    def set_theme(self, bg: str):
        self['bg'] = bg
        self.pattern_label['bg'] = bg

    def get_selection(self) -> str:
        if self.listbox.curselection():
            return self.listbox.get(self.listbox.curselection())

    def unfocus(self):
        self.listbox.selection_clear(0, 'end')

    def update_patterns(self):
        old_state = self.listbox['state']
        self.listbox['state'] = 'normal'
        self.listbox.delete(0, 'end')
        self.patterns = {i: self.patterns[i] for i in sorted(self.patterns)}

        for pattern in self.patterns:
            self.listbox.insert('end', pattern)
        with open('database.json', 'w') as f:
            json.dump(self.patterns, f, indent=4)
        self.listbox['state'] = old_state

    def add_pattern(self, name: str) -> bool:
        add_successful = bool(name and name not in self.patterns)
        if add_successful:
            self.patterns[name] = self._gui.main_board.export()
            self.update_patterns()
        return add_successful

    def rename_pattern(self, name: str, new_name: str) -> bool:
        rename_successful = bool(new_name and name in self.patterns and new_name not in self.patterns)
        if rename_successful:
            self.patterns[new_name] = self.patterns[name]
            self.patterns.pop(name)
            self.update_patterns()
        return rename_successful

    def delete_pattern(self, name: str) -> bool:
        delete_successful = name and name in self.patterns
        if delete_successful:
            self.patterns.pop(name)
            self.update_patterns()
        return delete_successful


class ConfigBox(tk.Checkbutton):
    def __init__(self, master: tk.Frame, text: str, row: int, command: callable):
        self._var = tk.IntVar()
        self.value = self._var.get()
        super().__init__(master=master, text=text, variable=self._var, command=lambda: self.call(command))
        self.grid(row=row, sticky='w', padx=5, pady=5)

    def call(self, command: callable):
        self.value = self._var.get()
        command()


class ConfigFrame(tk.Frame):
    def __init__(self, gui: MainGUI):
        super().__init__()
        self._gui = gui
        self._board = gui.board_frame._board
        self._label = tk.Label(self, text="Settings:")
        self._label.grid()

        self.config_MRV = ConfigBox(self, "Use MRV heuristic", 1, self.set_use_MRV)
        self.config_options = (self.config_MRV,)

    def set_use_MRV(self):
        self._board.use_MRV = self.config_MRV.value

    def set_state(self, state: str):
        for opt in self.config_options:
            opt['state'] = state

    def set_theme(self, bg: str):
        self['bg'] = bg
        self._label['bg'] = bg
        for opt in self.config_options:
            opt['bg'] = bg
