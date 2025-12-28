from src import tk, MainGUI, SaveWindow, ImportWindow, ExportWindow, RenameWindow, DeleteWindow, RandomWindow


class ActionButton(tk.Button):
    def __init__(self, master: tk.Frame, text: str, row: int, column: int, command: callable):
        super().__init__(master=master, text=text, command=command, width=10)
        self.grid(row=row, column=column + 1, padx=5, pady=5)


class ActionFrame(tk.Frame):
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
            self._gui.set_info_text('board_solve', count, f'{dt:.3f}', count / dt)
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
