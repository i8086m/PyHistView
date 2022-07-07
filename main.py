from PyQt5.QtCore import Qt, QThreadPool
from PyQt5.QtWidgets import QSlider, QHBoxLayout, QPushButton, QVBoxLayout, QRadioButton, QLabel, QButtonGroup, \
    QPlainTextEdit
from PyQt5 import QtGui, QtWidgets

import sys

from classes.QtTask import QtTask
from utils.video import *
from utils.image import *


def set_image(frame: QtWidgets.QLabel, img: np.ndarray) -> None:
    image = QtGui.QImage(img.data, img.shape[1], img.shape[0], QtGui.QImage.Format_RGB888).rgbSwapped()
    frame.setPixmap(QtGui.QPixmap.fromImage(image))


class App(QtWidgets.QWidget):
    thread_pool = QThreadPool.globalInstance()

    video = 'video.mp4'
    slider_resolution = 60
    frame_width = 640
    frame_height = int(frame_width / get_video_aspect_ratio(video))

    hist_width = 256 * 3
    hist_color = 'red'
    hist_style = 'default'
    gray_img = None
    hist_img = None

    def show_image(self):
        frame = frame_from_video(self.video, self.slider.value() / self.slider_resolution)

        img = resize_image(frame, self.frame_width, self.frame_height)
        set_image(self.image_frame, img)

        self.gray_img = bgr2gray(img)
        set_image(self.image_gray_frame, gray2rgb(self.gray_img))

        self.hist_img = get_hist(
            self.gray_img,
            self.hist_width,
            self.frame_height,
            style=self.hist_style,
            color=self.hist_color,
        )
        set_image(self.image_hist_frame, self.hist_img)


    def edit_theme(self, style: str = None, color: str = None):
        if style:
            self.hist_style = style
        if color:
            self.hist_color = color
        self.thread_pool.start(QtTask(self.show_image))  # update the histogram

    def export_grayscale(self, mode: int = 0):
        img = self.gray_img
        rows, cols = img.shape

        if mode == 0:  # as Bytes
            with open('exported.txt', 'wb') as file:
                file.write(img.tobytes())
        elif mode == 1:  # as Numbers
            with open('exported.txt', 'w') as file:
                for y in range(rows):
                    file.write(' '.join([str(img[y, x]) for x in range(cols)]) + '\n')
        else:
            raise ValueError('Invalid export mode')
        self.log.appendPlainText('Изображение экспортировано')

    def save_hist(self):
        if self.hist_img is not None:
            cv2.imwrite('output.png', self.hist_img)
        self.log.appendPlainText('Гистограмма сохранена')

    def __init__(self, parent=None):
        super(App, self).__init__(parent)
        self.setWindowTitle('PyHistogramViewer [MAI]')

        hbox = QHBoxLayout()
        self.image_frame = QtWidgets.QLabel()
        self.image_frame.setAlignment(Qt.AlignLeft)
        self.image_gray_frame = QtWidgets.QLabel()
        self.image_gray_frame.setAlignment(Qt.AlignRight)
        hbox.addWidget(self.image_frame)
        hbox.addWidget(self.image_gray_frame)

        hbox2 = QHBoxLayout()
        self.image_hist_frame = QtWidgets.QLabel()
        self.image_hist_frame.setAlignment(Qt.AlignCenter)

        vbox_left = QVBoxLayout()
        self.btngroup1 = QButtonGroup()
        self.btngroup2 = QButtonGroup()
        self.style_lbl = QLabel("Select style")
        self.style_rdbtn1 = QRadioButton("Default")
        self.style_rdbtn1.setChecked(True)
        self.style_rdbtn1.toggled.connect(lambda: self.edit_theme(style='default'))
        self.style_rdbtn2 = QRadioButton("Alternative")
        self.style_rdbtn2.toggled.connect(lambda: self.edit_theme(style='alternative'))
        self.color_lbl = QLabel("Select color")
        self.color_rdbtn_red = QRadioButton("Red")
        self.color_rdbtn_red.setChecked(True)
        self.color_rdbtn_red.toggled.connect(lambda: self.edit_theme(color='red'))
        self.color_rdbtn_green = QRadioButton("Green")
        self.color_rdbtn_green.toggled.connect(lambda: self.edit_theme(color='green'))
        self.color_rdbtn_blue = QRadioButton("Blue")
        self.color_rdbtn_blue.toggled.connect(lambda: self.edit_theme(color='blue'))
        self.btngroup1.addButton(self.style_rdbtn1)
        self.btngroup1.addButton(self.style_rdbtn2)
        self.btngroup2.addButton(self.color_rdbtn_red)
        self.btngroup2.addButton(self.color_rdbtn_green)
        self.btngroup2.addButton(self.color_rdbtn_blue)
        vbox_left.addStretch(1)
        vbox_left.addWidget(self.style_lbl)
        vbox_left.addWidget(self.style_rdbtn1)
        vbox_left.addWidget(self.style_rdbtn2)
        vbox_left.addWidget(self.color_lbl)
        vbox_left.addWidget(self.color_rdbtn_red)
        vbox_left.addWidget(self.color_rdbtn_green)
        vbox_left.addWidget(self.color_rdbtn_blue)
        vbox_left.addStretch(1)

        vbox_right = QVBoxLayout()
        self.btn_save_hist = QPushButton('Save histogram as image')
        self.btn_export_bytes = QPushButton('Export as Bytes')
        self.btn_export_numbers = QPushButton('Export as Numbers')
        self.btn_save_hist.clicked.connect(self.save_hist)
        self.btn_export_bytes.clicked.connect(lambda: self.export_grayscale(mode=0))
        self.btn_export_numbers.clicked.connect(lambda: self.export_grayscale(mode=1))
        self.log = QPlainTextEdit()
        self.log.setReadOnly(True)
        self.log.setMinimumSize(50, 100)
        vbox_right.addStretch(1)
        vbox_right.addWidget(self.btn_save_hist)
        vbox_right.addWidget(self.btn_export_bytes)
        vbox_right.addWidget(self.btn_export_numbers)
        vbox_right.addWidget(self.log)
        vbox_right.addStretch(1)

        hbox2.addLayout(vbox_left)
        hbox2.addWidget(self.image_hist_frame)
        hbox2.addLayout(vbox_right)

        self.slider = QSlider(Qt.Horizontal)
        self.slider.setMinimum(0)
        self.slider.setMaximum(get_video_duration(self.video) * self.slider_resolution)

        self.slider.valueChanged.connect(lambda: self.thread_pool.start(QtTask(self.show_image)))

        self.layout = QtWidgets.QVBoxLayout()
        self.layout.addLayout(hbox)
        self.layout.addLayout(hbox2)
        # self.layout.addWidget(self.image_hist_frame)
        self.layout.addWidget(self.slider)

        self.setLayout(self.layout)

        self.thread_pool.globalInstance().start(QtTask(self.show_image))


if __name__ == '__main__':
    app = QtWidgets.QApplication(sys.argv)
    display_image_widget = App()
    display_image_widget.show()
    sys.exit(app.exec_())
