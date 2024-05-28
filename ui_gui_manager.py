class UiGuiManager:
    def __init__(self, use_gui):
        self.use_gui = use_gui

    def prompt_for_username(self):
        if self.use_gui:
            # GUI logic to prompt for username
            pass
        else:
            # CLI logic to prompt for username
            return input("Enter a new package name: ")
