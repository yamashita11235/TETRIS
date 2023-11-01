from os import system

try:
  import cv2
except ModuleNotFoundError:
  system('py -m pip install opencv-python')
  import cv2

try:
  import numpy as np
except ModuleNotFoundError:
  system('py -m pip install numpy')
  import numpy as np

side_len = 640
h_side_len = side_len // 2
line_width = 320 // 15
h_line_width = line_width // 2
ptlist = [
  [(line_width, side_len - line_width), (h_side_len - line_width - h_line_width, h_side_len + line_width + h_line_width)],  # 左上
  [(line_width, h_side_len - line_width - h_line_width), (h_side_len - line_width - h_line_width, line_width)],  # 左下
  [(h_side_len + line_width + h_line_width, side_len - line_width), (side_len - line_width, h_side_len + line_width + h_line_width)],  # 右上
  [(h_side_len + line_width + h_line_width, h_side_len - line_width - h_line_width), (side_len - line_width, line_width)],  # 右下
]

img = np.zeros((side_len, side_len, 3), np.uint8)

cv2.rectangle(img, (0, side_len), (side_len, 0), (37, 193, 255), -1)
for pt1, pt2 in ptlist:
  cv2.rectangle(img, pt1, pt2, (0, 255, 255), -1)
cv2.line(img, (h_side_len, side_len), (h_side_len, 0), (13, 13, 13), line_width)
cv2.line(img, (0, h_side_len), (side_len, h_side_len), (13, 13, 13), line_width)

cv2.imshow("random_circle", img)

cv2.imwrite("icon.png", img)

cv2.waitKey(1000)
cv2.destroyAllWindows()