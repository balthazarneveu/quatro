from quatro.graphics.animation.butterfly_numpy import draw_butterfly
import numpy as np


def test_butterfly_drawing():
    img = np.zeros((100, 100, 3))
    draw_butterfly(img, 0.1, 0.5, 0.5)
    # from matplotlib import pyplot as plt
    # plt.imshow(img)
    # plt.show()
