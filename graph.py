# -*- coding:utf-8 -*-


import numpy as np
import matplotlib.pyplot as plt
from mpl_toolkits.mplot3d import Axes3D


def paint(max_u=10000, max_v=10000):
    u = np.arange(1, max_u, 1)
    v = np.arange(1, max_v, 1)

    um = u.repeat(len(v)).reshape(len(u), len(v))
    vm = v.repeat(len(u)).reshape(len(v), len(u))

    # print(um.shape)
    # print(um)
    # print(vm.shape)
    # print(vm)

    n = um + vm.T
    # print(n.shape)
    # print(n)

    p = um / n
    # print(p.shape)
    # print(p)

    # p = u / n

    # p = np.arange(0, 1, 0.01)
    # n = np.arange(1, 100, 1)
    z = 1.96
    # print(len(n), n)
    # print(len(p), p)

    # y = (p + z ** 2 / (2 * n) - z * np.sqrt(p * (1 - p) / n + z ** 2 / (4 * n ** 2))) / (1 + z / n)
    y = (p + z ** 2 / (2 * n) - z * np.sqrt(p * (1 - p) / n + z ** 2 / (4 * n ** 2))) / (1 + z ** 2 / n)
    fig = plt.figure()
    ax = Axes3D(fig)
    # print(len(um), len(vm.T))
    # print(y.shape)
    ax.view_init(25, -137)
    ax.plot_surface(um, vm.T, y, cmap='rainbow')
    plt.show()


if __name__ == '__main__':
    paint()
