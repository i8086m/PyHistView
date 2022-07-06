import cv2
import numpy as np


def resize_image(img: np.ndarray, x: int, y: int) -> np.ndarray:
    return cv2.resize(img, (x, y))  # interpolation=cv2.THRESH_BINARY


def bgr2gray(img: np.ndarray) -> np.ndarray:
    return cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)


def gray2rgb(img: np.ndarray) -> np.ndarray:
    return cv2.cvtColor(img, cv2.COLOR_GRAY2RGB)


def get_color_from_name(name: str):
    if name == 'red':
        return (0, 0, 255)
    if name == 'green':
        return (0, 255, 0)
    if name == 'blue':
        return (255, 0, 0)
    return (255, 255, 255)


def get_hist(gray_img: np.ndarray, hist_w: int, hist_h: int, style: str = 'default', color: str = 'red') -> np.ndarray:
    hist = cv2.calcHist([gray_img], [0], None, [256], [0, 256])
    cv2.normalize(hist, hist, alpha=0, beta=hist_h, norm_type=cv2.NORM_MINMAX)
    bin_w = int(round(hist_w / 256))

    hist_img = np.zeros((hist_h, hist_w, 3), dtype=np.uint8)
    color_tuple = get_color_from_name(color)

    for i in range(0, 256):
        if style == 'default':
            cv2.line(hist_img, (bin_w * (i - 1), hist_h - int(hist[i - 1])),
                     (bin_w * i, hist_h - int(hist[i])),
                     color_tuple, thickness=1)
        elif style == 'alternative':
            cv2.rectangle(hist_img, (int(i * bin_w), hist_h - int(hist[i][0])), (int(i * bin_w + bin_w - 1), hist_h),
                          color_tuple, -1)
        else:
            raise NameError('Invalid style selected')
    return hist_img
