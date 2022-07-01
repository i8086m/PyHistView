from PyQt5.QtCore import Qt
from PyQt5.QtWidgets import QSlider, QHBoxLayout
from PyQt5 import QtGui, QtWidgets

import sys

from classes.QtThread import QtThread
from utils.video import *
from utils.image import *


def set_image(frame: QtWidgets.QLabel, img: np.ndarray) -> None:
    image = QtGui.QImage(img.data, img.shape[1], img.shape[0], QtGui.QImage.Format_RGB888).rgbSwapped()
    frame.setPixmap(QtGui.QPixmap.fromImage(image))


class App(QtWidgets.QWidget):
    video = 'video.mp4'
    slider_resolution = 100
    frame_width = 640
    frame_height = int(frame_width / get_video_aspect_ratio(video))
    hist_width = 256 * 3

    def show_image(self):
        frame = frame_from_video(self.video, self.slider.value() / self.slider_resolution)

        img = resize_image(frame, self.frame_width, self.frame_height)
        set_image(self.image_frame, img)

        gray_img = bgr2gray(img)
        set_image(self.image_gray_frame, gray2rgb(gray_img))

        hist_img = get_hist(gray_img, self.hist_width, self.frame_height)
        set_image(self.image_hist_frame, hist_img)

    def __init__(self, parent=None):
        super(App, self).__init__(parent)
        self.setWindowTitle('PyHistogramViewer [MAI]')

        self.image_thread = QtThread(target=self.show_image)
        print(self.frame_width, self.frame_height)

        hbox = QHBoxLayout()

        self.image_frame = QtWidgets.QLabel()
        self.image_frame.setAlignment(Qt.AlignLeft)
        self.image_gray_frame = QtWidgets.QLabel()
        self.image_gray_frame.setAlignment(Qt.AlignRight)

        hbox.addWidget(self.image_frame)
        hbox.addWidget(self.image_gray_frame)

        self.image_hist_frame = QtWidgets.QLabel()
        self.image_hist_frame.setAlignment(Qt.AlignCenter)

        self.slider = QSlider(Qt.Horizontal)
        self.slider.setMinimum(0)
        self.slider.setMaximum(get_video_duration(self.video) * self.slider_resolution)

        self.slider.valueChanged.connect(lambda: self.image_thread.start())

        self.layout = QtWidgets.QVBoxLayout()
        self.layout.addLayout(hbox)
        self.layout.addWidget(self.image_hist_frame)
        self.layout.addWidget(self.slider)

        self.setLayout(self.layout)

        self.show_image()


if __name__ == '__main__':
    app = QtWidgets.QApplication(sys.argv)
    display_image_widget = App()
    display_image_widget.show()
    sys.exit(app.exec_())
