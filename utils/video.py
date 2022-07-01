import cv2
import numpy as np
from math import floor


def frame_from_video(name: str, time: int) -> np.ndarray:
    vidcap = cv2.VideoCapture(name)
    vidcap.set(cv2.CAP_PROP_POS_MSEC, (time * 1000))
    success, img = vidcap.read()
    if success:
        return img
    raise IOError('Unable to open file')


def get_video_duration(name: str) -> int:
    vidcap = cv2.VideoCapture(name)
    if vidcap.isOpened():
        fps = vidcap.get(cv2.CAP_PROP_FPS)
        frame_count = int(vidcap.get(cv2.CAP_PROP_FRAME_COUNT))
        return floor(frame_count / fps) - 1
    raise IOError('Unable to open file')


def get_video_aspect_ratio(name: str) -> float:
    vidcap = cv2.VideoCapture(name)
    if vidcap.isOpened():
        width = vidcap.get(cv2.CAP_PROP_FRAME_WIDTH)
        height = vidcap.get(cv2.CAP_PROP_FRAME_HEIGHT)
        return width / height
    raise IOError('Unable to open file')
