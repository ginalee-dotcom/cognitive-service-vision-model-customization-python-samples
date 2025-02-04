import argparse
import json

import cv2
import numpy as np


class CornerSelector:
    def __init__(self):
        self._image = None
        self._points = []

    def interactive_select(self, image):
        self._image = image
        window_name = 'Please select four corners in clockwise order'
        cv2.namedWindow(window_name)
        cv2.setMouseCallback(window_name, self._click_callback)

        while(True):
            cv2.imshow(window_name, self._image)
            cv2.waitKey(20)
            if len(self._points) == 4:
                cv2.destroyAllWindows()
                return np.array(self._points)

    def _click_callback(self, event, x, y, flags, param):
        if event == cv2.EVENT_LBUTTONDOWN:
            cv2.circle(self._image, (x, y), 5, (0, 0, 255), 2)
            self._points.append((x, y))


def image_resize(image, width = None, height = None, inter = cv2.INTER_AREA):
    dim = None
    (h, w) = image.shape[:2]

    if width is None and height is None:
        return image

    if width is None:
        r = height / float(h)
        dim = (int(w * r), height)
    else:
        r = width / float(w)
        dim = (width, int(h * r))

    resized = cv2.resize(image, dim, interpolation = inter)
    return resized, dim


def select_four_corners(intput_path):
    org_img = cv2.imread(intput_path)
    if org_img.shape[0] > org_img.shape[1]:
        img, dim = image_resize(org_img, height=1024)
    else:
        img, dim = image_resize(org_img, width=1024)
    corners = CornerSelector().interactive_select(img)
    corners_relative = []
    for corner in corners:
        tmp_x = corner[0]/dim[0]
        tmp_y = corner[1]/dim[1]
        corners_relative.append([tmp_x, tmp_y])

    return corners_relative


def convert_to_control_points_format(corner_points):
    control_points = {
        "topLeft": {
            "x": corner_points[0][0],
            "y": corner_points[0][1]
        },
        "topRight": {
            "x": corner_points[1][0],
            "y": corner_points[1][1]
        },
        "bottomRight": {
            "x": corner_points[2][0],
            "y": corner_points[2][1]
        },
        "bottomLeft": {
            "x": corner_points[3][0],
            "y": corner_points[3][1]
        }
    }

    return {'ControlPonts': control_points}


if __name__ == '__main__':
    parser = argparse.ArgumentParser(description='Select corners of an image interactively.')
    parser.add_argument('input_filename', type=str, help='Input image file')

    args = parser.parse_args()

    payload = convert_to_control_points_format(select_four_corners(args.input_filename))
    print(json.dumps(payload, indent=4))
