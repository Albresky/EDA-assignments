'''
Descripttion: Utils like configurations and visualization
Author: Albresky
Date: 2024-11-27 22:56:01
LastEditors: Albresky
LastEditTime: 2024-12-13 14:49:39
'''

def load_config(filename:str) -> dict:
    import json

    with open(filename, 'r') as f:
        config = json.load(f)
    return config

def visualize(filename:str) -> None:
    import matplotlib 
    import matplotlib.pyplot as plt 
    
    fig = plt.figure() 

    ax = fig.add_subplot(111)
    
    node_names = []
    x_cor = []
    y_cor = []
    width = []
    height = []

    colors = []
    
    def sel_color(colors) -> str:
        import random
        color = '#'
        for i in range(6):
            color += random.choice('0123456789ABCDEF')
        if color not in colors:
            colors.append(color)
            return color
        else:
            return sel_color(colors)
    

    with open(filename) as f:
        next(f)
        next(f)
        next(f)
        xlength = int(f.readline().split(' ')[-1])
        ylength = int(f.readline().split(' ')[-1])
        next(f)

        for line in f.readlines():
            s = line.split(' ')
            node_names.append(str(s[0]))
            x_cor.append(float(s[1]))
            y_cor.append(float(s[2]))
            width.append(float(s[3])-float(s[1]))
            height.append(float(s[4])-float(s[2]))


    for x,y,w,h,n in zip(x_cor, y_cor, width, height, node_names):
        rect1 = matplotlib.patches.Rectangle((x, y), 
                                         w, h,   
                                         facecolor = sel_color(colors),
                                         fill=True)

        if w>h:
            ax.text(x+w/2, y+h/2, n, ha='center', va='center', fontsize=10, color='white', fontweight='bold')
        else:
            ax.text(x+w/2, y+h/2, n, ha='center', va='center', fontsize=10, color='white', fontweight='bold', rotation=90)

        ax.add_patch(rect1)

    # set canvas size to high resolution
    scale = 15
    fig.set_size_inches(scale, 1.0*scale*ylength/xlength)
    ax.set_aspect('equal', adjustable='box')
    
    for i in range(0, ylength, 100):
        plt.plot([0, xlength], [i, i], 'k--', lw=0.5)
    for i in range(0, xlength, 100):
        plt.plot([i, i], [0, ylength], 'k--', lw=0.5)
    limlen = max(xlength, ylength)
    plt.xlim([0, limlen+300]) 
    plt.ylim([0, limlen+300]) 

    plt.show()
    plt.savefig(f'{filename}.png')
    pass
