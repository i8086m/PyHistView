from PyQt5 import QtCore


class QtThread(QtCore.QThread):
    def __init__(self, target, on_finished=None):
        super(QtThread, self).__init__()
        self.target = target
        if on_finished:
            self.finished.connect(on_finished)

    def run(self, *args, **kwargs):
        self.target(*args, **kwargs)