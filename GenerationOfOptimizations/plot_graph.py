#-*- coding: utf-8 -*-
import matplotlib.pyplot as plt


ai = u"é"
aie = u"è"

def draw_graph_evolution(x_axe, y_axe):
    plt.plot(x_axe, y_axe)
    plt.xlabel('Le temps pris par le syst'+aie+'me')
    plt.ylabel('Le temps d\'ex'+ai+'cution du schedule')
    plt.title('La variation du temps d\'ex'+ai+'cution des schedule en fonction du temps pris par le syst'+aie+'me')
    plt.show()
