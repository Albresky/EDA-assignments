'''
Descripttion: The main function of floorplan
Author: Albresky
Date: 2024-11-28 12:03:13
LastEditors: Albresky
LastEditTime: 2024-11-28 13:08:00
'''
import os,sys

sys.path.append(os.path.join(os.path.dirname(__file__), '.'))
sys.path.append(os.path.join(os.path.dirname(__file__), '..'))

import time, datetime
from fp_parser import parse_dotnet, parse_dotblock
from fp_units import Blocks, Nets, Terminals
from fp_bstar import BStarTree
from fp_utils import load_config, visualize

def main():
    cfg = load_config('./config.json')
    
    start_time = time.time()
    outline, blocks, terminals = parse_dotblock(cfg['file']['blocks'])
    nets = parse_dotnet(cfg['file']['nets'], blocks, terminals)

    # 初始化 B*-树
    floorplanner = BStarTree(blocks, temperature=cfg['sa_params']['temperature'], alpha=cfg['sa_params']['alpha'])
    floorplanner.initialize()
    floorplanner.pack()

    # 优化
    floorplanner.simulate_annealing(outline, nets, max_iterations=cfg['sa_params']['iterations'])

    # 计算最终结果
    cost, area, wirelength = floorplanner.calculate_cost(nets)
    end_time = time.time()

    # 输出结果
    output_name = f'floorplan_{datetime.datetime.now().strftime("%Y-%m-%d-%H:%M:%S")}.output'
    with open(output_name, 'w') as f:
        f.write(f"Cost {cost}\n")
        f.write(f"Wirelength {wirelength}\n")
        f.write(f"Area {area}\n")
        f.write(f"Width {outline.w}\n")
        f.write(f"Height {outline.h}\n")
        f.write(f"RunTime {end_time - start_time}\n")
        for block in floorplanner.best_blocks:
            f.write(f"{block.name} {block.x} {block.y} {block.x + block.width} {block.y + block.height}\n")
    
    # 可视化
    visualize(output_name)
    
if __name__ == '__main__':
    main()
    pass