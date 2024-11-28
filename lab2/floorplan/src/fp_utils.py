'''
Descripttion: Utils like configurations and visualization
Author: Albresky
Date: 2024-11-27 22:56:01
LastEditors: Albresky
LastEditTime: 2024-11-28 13:13:36
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

    x_cor = []
    y_cor = []
    width = []
    height = []


    with open(filename) as f:
        cost = float(f.readline().split(' ')[-1])
        hpwl = float(f.readline().split(' ')[-1])
        area = int(f.readline().split(' ')[-1])
        xlength = int(f.readline().split(' ')[-1])
        ylength = int(f.readline().split(' ')[-1])
        runtime = float(f.readline().split(' ')[-1])
        
        print('#'*10 + ' Floorplan Information ' + '#'*10)
        print(f'Cost: {cost}')
        print(f'HPWL: {hpwl}')
        print(f'Area: {area}')
        print(f'X-Length: {xlength}')
        print(f'Y-Length: {ylength}')
        print(f'Runtime: {runtime} seconds')
        print('#'*(20+len(' Floorplan Information ')))

        for line in f.readlines():
            s = line.split(' ')
            x_cor.append(float(s[1]))
            y_cor.append(float(s[2]))
            width.append(float(s[3])-float(s[1]))
            height.append(float(s[4])-float(s[2]))


    for i,j,k,l in zip(x_cor, y_cor, width, height):
        rect1 = matplotlib.patches.Rectangle((i, j), 
                                         k, l,   
                                         color ='red',
                                         fill=False)
        ax.add_patch(rect1)


    ax.set_aspect('equal', adjustable='box')
    border=max(xlength,ylength)  
    plt.xlim([0, border+200]) 
    plt.ylim([0, border+200]) 
    
    plt.show()
    plt.savefig(f'{filename}.png')
    pass
