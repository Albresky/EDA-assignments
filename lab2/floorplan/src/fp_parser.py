'''
Copyright (c) 2024 by Albresky, All Rights Reserved. 

Author: Albresky albre02@outlook.com
Date: 2024-11-27 22:55:07
LastEditTime: 2024-12-22 19:22:28
FilePath: /EDA-assignments/lab2/floorplan/src/fp_parser.py

Description: Parsers for units from .block and .net files.
'''

from fp_units import *


def parse_dotblock(filename) -> tuple:
    blocks = Blocks()
    terminals = Terminals()
    outline = Outline()
    with open(filename, 'r') as f:
        lines = f.readlines()
    index = 0
    num_blocks = 0
    num_terminals = 0
    # Parse header information
    while index < len(lines):
        line = lines[index].strip()
        if not line:
            index += 1
            continue
        if line.startswith('Outline:'):
            _, width, height = line.split()
            outline.set_size(int(width), int(height))
        elif line.startswith('NumBlocks:'):
            _, num_blocks_str = line.split()
            num_blocks = int(num_blocks_str)
        elif line.startswith('NumTerminals:'):
            _, num_terminals_str = line.split()
            num_terminals = int(num_terminals_str)
            index += 1
            break
        index += 1
    # Parse blocks and terminals
    while index < len(lines):
        line = lines[index].strip()
        if not line:
            index += 1
            continue
        parts = line.split()
        if 'terminal' in parts:
            if len(parts) != 4:
                raise ValueError('Invalid terminal line: {}'.format(line))
            name = parts[0]
            x = int(parts[2])
            y = int(parts[3])
            terminal = Terminal(name, x, y)
            terminals.add_unit(terminal)
        else:
            if len(parts) != 3:
                raise ValueError('Invalid block line: {}'.format(line))
            name = parts[0]
            width = int(parts[1])
            height = int(parts[2])
            block = Block(name, width, height)
            blocks.add_unit(block)
        index += 1
    return outline, blocks, terminals

def parse_dotnet(filename:str, blocks:Blocks, terminals:Terminals) -> Nets:
    nets = Nets()
    block_dict = {block.name: block for block in blocks.get_units()}
    terminal_dict = {terminal.name: terminal for terminal in terminals.get_units()}
    with open(filename, 'r') as f:
        lines = f.readlines()
    index = 0
    net_id = 0
    while index < len(lines):
        line = lines[index].strip()
        if not line:
            index += 1
            continue
        if line.startswith('NumNets:'):
            index += 1
            continue
        elif line.startswith('NetDegree:'):
            parts = line.split()
            net_degree = int(parts[1])
            index += 1
            net = Net(f'Net{net_id}')
            net_id += 1
            for _ in range(net_degree):
                if index >= len(lines):
                    break
                member_line = lines[index].strip()
                if not member_line:
                    index += 1
                    continue
                if member_line in block_dict:
                    net.add_block(block_dict[member_line])
                elif member_line in terminal_dict:
                    net.add_block(terminal_dict[member_line])
                else:
                    print(f'Warning: Unknown block or terminal {member_line}')
                    pass
                index += 1
            nets.add_unit(net)
        else:
            index += 1
    return nets


if __name__ == '__main__':
    
    ######## Test parse_dotblock ########
    outline, blocks, terminals = parse_dotblock('../testcases/ami33.block')
    
    ######## Test parse_net_file ########
    nets = parse_dotnet('../testcases/ami33.nets', blocks, terminals)
    pass
