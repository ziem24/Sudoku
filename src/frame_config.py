from src import tk, MainGUI


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
