from src import tk


class Window(tk.Tk):
    def __init__(self, gui: tk.Tk):
        super().__init__()
        self.protocol('WM_DELETE_WINDOW', self.on_close)
        self.resizable(False, False)
        self.configure(padx=25, pady=15)
        self.title('')

        self._gui = gui
        self._board = gui.main_board
        self._board_frame = gui.board_frame
        self._pt_listbox = gui.pattern_frame
        self.selected_pattern = gui.action_frame.selected_pattern
        self.state_on_enter = gui.state

        self.bg = gui['bg']
        self['bg'] = gui['bg']
        self._gui.opened_window = self
        self._gui.set_info_text('empty')
        self._gui.set_states_on_event('open_win')
        self._pt_listbox.unfocus()

    def on_close(self):
        self.destroy()
        self._gui.set_states_on_event(self.state_on_enter)
        self._gui.opened_window = None


class EntryWindow(Window):
    def __init__(self, gui: tk.Tk, title: str = '', entry_width: int = 20):
        super().__init__(gui)

        self.title_label = tk.Label(self, text=title)
        self.title_label.grid(row=0, columnspan=3)
        self.title_label['bg'] = self.bg

        self.info_label = tk.Label(self)
        self.info_label.grid(row=2, columnspan=3)
        self.info_label['bg'] = self.bg

        self.entry = tk.Entry(self, width=entry_width)
        self.entry.grid(row=1, pady=15)
        self.entry.bind('<Return>', self.confirm)

        self.bt_confirm = tk.Button(self, text='Done', width=10, command=self.confirm)
        self.bt_confirm.grid(row=1, column=1, padx=10)

        self.bt_cancel = tk.Button(self, text='Cancel', width=10, command=self.on_close)
        self.bt_cancel.grid(row=1, column=2)

    def confirm(self, event=None):
        pass


class SaveWindow(EntryWindow):
    def __init__(self, gui: tk.Tk):
        super().__init__(gui, 'Save pattern as:')

    def confirm(self, event=None):
        prompt = self.entry.get()
        if self._pt_listbox.add_pattern(prompt):
            self._gui.set_info_text('pattern_save', prompt)
            self.on_close()
        elif prompt:
            self.info_label['text'] = f'Pattern \'{prompt}\' already exists!'
        else:
            self.info_label['text'] = 'Pattern name must be non-empty!'


class ImportWindow(EntryWindow):
    def __init__(self, gui: tk.Tk):
        super().__init__(gui, 'Import a sudoku pattern', entry_width=83)

    def confirm(self, event=None):
        prompt = self.entry.get()
        if self._board.import_(prompt):
            self._gui.set_info_text('pattern_import')
            self._board_frame.update_all()
            self.on_close()
        elif prompt:
            self.info_label['text'] = 'Invalid input!'


class ExportWindow(Window):
    def __init__(self, gui: tk.Tk):
        super().__init__(gui)

        self.title_label = tk.Label(self, text='Exported this pattern as a copyable string.')
        self.title_label.grid(row=0)
        self.title_label['bg'] = self.bg

        self.export_str = tk.Entry(self, width=83, justify='center')
        self.export_str.grid(row=1)
        self.export_str.insert(0, self._board.export())


class RenameWindow(EntryWindow):
    def __init__(self, gui: tk.Tk):
        super().__init__(gui)
        self.title_label['text'] = f'Rename \'{self.selected_pattern}\' to:'

    def confirm(self, event=None):
        prompt = self.entry.get()
        if self._pt_listbox.rename_pattern(self.selected_pattern, prompt):
            self._gui.set_info_text('pattern_rename', self.selected_pattern, prompt)
            self.on_close()
        elif prompt:
            self.info_label['text'] = f'Pattern \'{prompt}\' already exists!'
        else:
            self.info_label['text'] = 'Pattern name must be non-empty!'


class DeleteWindow(Window):
    def __init__(self, gui: tk.Tk):
        super().__init__(gui)

        self.title_label = tk.Label(self, text=f'Delete \'{self.selected_pattern}\'?')
        self.title_label.grid(row=0, columnspan=2)

        self.bt_confirm = tk.Button(self, text='Yes', width=10, command=self.del_confirm)
        self.bt_confirm.grid(row=1, column=0, padx=20)

        self.bt_cancel = tk.Button(self, text='No', width=10, command=self.del_cancel)
        self.bt_cancel.grid(row=1, column=1, padx=20)

    def del_confirm(self):
        self._gui.set_info_text('pattern_del_confirm', self.selected_pattern)
        self._pt_listbox.delete_pattern(self.selected_pattern)
        self.on_close()

    def del_cancel(self):
        self._gui.set_info_text('pattern_del_cancel')
        self.on_close()


class RandomWindow(EntryWindow):
    def __init__(self, gui: tk.Tk):
        super().__init__(gui, 'Enter what % of cells should be filled (0 <= x <= 100)')

    def confirm(self, event=None):
        prompt = self.entry.get()
        if prompt.isdigit() and 0 <= int(prompt) <= 100:
            self._gui.set_info_text('pattern_random')
            self._board.generate_random(int(prompt))
            self._board_frame.update_all()
            self.on_close()
        elif prompt:
            self.info_label['text'] = 'Invalid input!'
