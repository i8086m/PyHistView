from PyQt5.QtCore import QRunnable


class QtTask(QRunnable):
    def __init__(self, target):
        super().__init__()
        self.target = target

    def run(self):
        self.target()