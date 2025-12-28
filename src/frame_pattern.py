from src import tk, json, MainGUI


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
