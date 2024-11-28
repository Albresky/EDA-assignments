'''
Descripttion: The definition of classes for units in floorplan
Author: Albresky
Date: 2024-11-27 22:55:28
LastEditors: Albresky
LastEditTime: 2024-11-28 11:35:30
'''

class Block:
    def __init__(self, name, width, height) -> None:
        self.name = name
        self.width = width
        self.height = height
        self.x = 0
        self.y = 0

class Terminal:
    def __init__(self, name, x, y) -> None:
        self.name = name
        self.x = x
        self.y = y
        
class Net:
    def __init__(self, name:str, degree:int=0) -> None:
        self.name = name
        self.nodes = []
        self.degree = degree 
    
    def add_block(self, block) -> None:
        self.nodes.append(block)
        self.degree += 1
        
class Units:
    def __init__(self, units:list=[], num_units:int=0) -> None:
        if len(units) != num_units:
            raise ValueError(f'Length of units {len(units)} does not match num_units {num_units}')
        
        self.units = units
        self.num_units = num_units
        
    def add_unit(self, unit) -> None:
        self.units.append(unit)
        self.num_units += 1
    
    def get_units(self) -> list:
        return self.units

class Nets(Units):
    def __init__(self, nets:list=[], num_nets:int=0) -> None:
        super().__init__(nets, num_nets)

class Blocks(Units):
    def __init__(self, blocks:list=[], num_blocks:int=0) -> None:
        super().__init__(blocks, num_blocks)
        
class Terminals(Units):
    def __init__(self, terminals:list=[], num_terminals:int=0) -> None:
        super().__init__(terminals, num_terminals)
