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
    hist_thickness = 1
    hist_style = 'default'
    img = None
    gray_img = None
    hist_img = None

    last_saved_image_id = 0
    last_exported_image_id = 0

    def show_image(self):
        frame = frame_from_video(self.video, self.slider.value() / self.slider_resolution)

        self.img = resize_image(frame, self.frame_width, self.frame_height)
        set_image(self.image_frame, self.img)

        self.gray_img = bgr2gray(self.img)
        set_image(self.image_gray_frame, gray2rgb(self.gray_img))

        self.hist_img = get_hist(
            self.gray_img,
            self.hist_width,
            self.frame_height,
            style=self.hist_style,
            color=self.hist_color,
            thick=self.hist_thickness,
        )
        set_image(self.image_hist_frame, self.hist_img)

    def edit_theme(self, style: str = None, color: str = None, thickness: int = None):
        if style:
            self.hist_style = style
        if color:
            self.hist_color = color
        if thickness:
            self.hist_thickness = thickness
        self.thread_pool.start(QtTask(self.show_image))  # update the histogram

    def export_grayscale(self, mode: int = 0):
        img = self.gray_img
        rows, cols = img.shape

        if mode == 0:  # as Bytes
            with open('output/exported_{}.txt'.format(self.last_exported_image_id), 'wb') as file:
                file.write(img.tobytes())
        elif mode == 1:  # as Numbers
            with open('output/exported_{}.txt'.format(self.last_exported_image_id), 'w') as file:
                for y in range(rows):
                    file.write(' '.join([str(img[y, x]) for x in range(cols)]) + '\n')
        else:
            raise ValueError('Invalid export mode')
        self.last_exported_image_id += 1
        self.log.appendPlainText('Изображение экспортировано')

    def save_hist(self):
        if self.hist_img is not None:
            cv2.imwrite('output/saved_{}_hist.png'.format(self.last_saved_image_id), self.hist_img)
        if self.img is not None:
            cv2.imwrite('output/saved_{}_frame.png'.format(self.last_saved_image_id), self.img)
        self.last_saved_image_id += 1
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
        self.btngroup3 = QButtonGroup()
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
        self.color_rdbtn_prnt = QRadioButton("Printable")
        self.color_rdbtn_prnt.toggled.connect(lambda: self.edit_theme(color='print'))
        self.thickness_lbl = QLabel("Select line width")
        self.color_rdbtn_1px = QRadioButton("1.0px")
        self.color_rdbtn_1px.setChecked(True)
        self.color_rdbtn_1px.toggled.connect(lambda: self.edit_theme(thickness=1))
        self.color_rdbtn_2px = QRadioButton("2.0px")
        self.color_rdbtn_2px.toggled.connect(lambda: self.edit_theme(thickness=2))
        self.btngroup1.addButton(self.style_rdbtn1)
        self.btngroup1.addButton(self.style_rdbtn2)
        self.btngroup2.addButton(self.color_rdbtn_red)
        self.btngroup2.addButton(self.color_rdbtn_green)
        self.btngroup2.addButton(self.color_rdbtn_blue)
        self.btngroup2.addButton(self.color_rdbtn_prnt)
        self.btngroup3.addButton(self.color_rdbtn_1px)
        self.btngroup3.addButton(self.color_rdbtn_2px)
        vbox_left.addStretch(1)
        vbox_left.addWidget(self.style_lbl)
        vbox_left.addWidget(self.style_rdbtn1)
        vbox_left.addWidget(self.style_rdbtn2)
        vbox_left.addWidget(self.color_lbl)
        vbox_left.addWidget(self.color_rdbtn_red)
        vbox_left.addWidget(self.color_rdbtn_green)
        vbox_left.addWidget(self.color_rdbtn_blue)
        vbox_left.addWidget(self.color_rdbtn_prnt)
        vbox_left.addWidget(self.thickness_lbl)
        vbox_left.addWidget(self.color_rdbtn_1px)
        vbox_left.addWidget(self.color_rdbtn_2px)
        vbox_left.addStretch(1)

        vbox_right = QVBoxLayout()
        self.save_lbl1 = QLabel('Save histogram to image')
        self.btn_save_hist = QPushButton('Save as .png')
        self.save_lbl2 = QLabel('Export greyscale image to file')
        self.btn_export_bytes = QPushButton('Export as Bytes')
        self.btn_export_numbers = QPushButton('Export as Numbers')
        self.btn_save_hist.clicked.connect(self.save_hist)
        self.btn_export_bytes.clicked.connect(lambda: self.export_grayscale(mode=0))
        self.btn_export_numbers.clicked.connect(lambda: self.export_grayscale(mode=1))
        self.log = QPlainTextEdit()
        self.log.setReadOnly(True)
        self.log.setMinimumSize(50, 100)
        vbox_right.addStretch(1)
        vbox_right.addWidget(self.save_lbl1)
        vbox_right.addWidget(self.btn_save_hist)
        vbox_right.addWidget(self.save_lbl2)
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