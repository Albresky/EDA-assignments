'''
Copyright (c) 2024 by Albresky, All Rights Reserved. 

Author: Albresky albre02@outlook.com
Date: 2024-12-21 20:04:49
LastEditTime: 2024-12-22 19:20:27
FilePath: /EDA-assignments/lab2/floorplan/src/main.py

Description: The main function of floorplanner
'''

import os,sys

sys.path.append(os.path.join(os.path.dirname(__file__), '.'))
sys.path.append(os.path.join(os.path.dirname(__file__), '..'))
sys.path.append(os.path.abspath(__file__))
os.chdir(sys.path[0])

import time, datetime
from fp_parser import parse_dotnet, parse_dotblock
from fp_units import Blocks, Nets, Terminals
from fp_floorplanner import FloorPlanner
from fp_utils import load_config, visualize

def main():
    cfg = load_config('./config.json')
    
    start_time = time.time()
    outline, blocks, terminals = parse_dotblock(cfg['file']['blocks'])
    nets = parse_dotnet(cfg['file']['nets'], blocks, terminals)

    # 初始化 FloorPlanner
    floorplanner = FloorPlanner(outline, blocks, temperature=cfg['sa_params']['temperature'], alpha=cfg['sa_params']['alpha'])
    floorplanner.initialize()

    # 优化
    floorplanner.simulate_annealing(nets, max_iterations=cfg['sa_params']['iterations'])

    # 计算最终结果
    cost, area, wirelength, adjacent_long_edges = floorplanner.calculate_cost(nets)
    end_time = time.time()

    print(f"=============== Finish ==================")
    floorplanner.check_valid_all()

    # 输出结果
    output_name = f'output/floorplan_{datetime.datetime.now().strftime("%Y-%m-%d-%H:%M:%S")}.output'
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