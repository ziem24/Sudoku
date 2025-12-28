from src import json, tk, Board, ActionFrame, BoardFrame, ConfigFrame, PatternFrame


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
        self.action_frame = ActionFrame(self)
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
