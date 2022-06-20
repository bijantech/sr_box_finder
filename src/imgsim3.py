import imgcompare
from imgcompare import is_equal
import os
import numpy as np
from PIL import Image

box1 = Image.open("data/box1.png").convert('RGB')
box2 = Image.open("data/box2.png").convert('RGB')
box3 = Image.open("data/box3.png").convert('RGB')
box4 = Image.open("data/box4.png").convert('RGB')
box5 = Image.open("data/box5.png").convert('RGB')

# print("same", imgcompare.image_diff_percent(box1, box1))
# print("some", imgcompare.image_diff_percent(box3, box2))
# print("none", imgcompare.image_diff_percent(box2, box1))
# print("none", imgcompare.image_diff_percent(box3, box1))
# print("toomuch", imgcompare.image_diff_percent(box4, box1))

# for x in range(100):
print("close", imgcompare.image_diff_percent(box5, box1))

# print(is_equal(box1, box5))
# print(is_equal(box5, box5))
