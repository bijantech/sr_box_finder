from sewar.full_ref import msssim

import os
import numpy as np
from PIL import Image

class Tester:
    def __init__(self, *args, **kwargs):
        super(Tester, self).__init__(*args, **kwargs)
        self.RESOURCES_DIR = os.path.join(os.path.dirname(__file__), "../data")
        self.IMAGES = {
            "TSLA": "TSLA.png",
            "TSLA_copy": "TSLA_copy.png",
            "box1": "box1.png",
            "box2": "box2.png",
            "box3": "box3.png",
        }
        self.eps = 10e-4

    def read(self, key):
        return np.asarray(
            Image.open(os.path.join(self.RESOURCES_DIR, self.IMAGES[key]))
        )

    def path(self, key):
        return os.path.join(self.RESOURCES_DIR, self.IMAGES[key])

t = Tester()
img1 = t.read('box1')
img2 = t.read('box2')
img3 = t.read('box3')

dif1_2 = msssim(img1, img2)
dif2_3 = msssim(img2, img3)
dif1_3 = msssim(img1, img3)

print("1:2", dif1_2)
print("1:3", dif1_3)
print("2:3", dif2_3)

does_match = (dif1_2 > dif1_3) and (dif2_3 > dif1_3)

print(does_match)
