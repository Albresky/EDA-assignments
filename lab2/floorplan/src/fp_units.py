'''
Descripttion: The definition of classes for units in floorplan
Author: Albresky
Date: 2024-11-27 22:55:28
LastEditors: Albresky
LastEditTime: 2024-12-13 14:55:00
'''

class Outline:
    def __init__(self, width:int=0, height:int=0) -> None:
        self.w = width
        self.h = height

    def set_height(self, height:int) -> None:
        self.h = height
    
    def set_width(self, width:int) -> None:
        self.w = width
        
    def set_size(self, width:int, height:int) -> None:
        self.w = width
        self.h = height
    
class Block:
    def __init__(self, name=None, width=None, height=None, x=0, y=0) -> None:
        self.name = name
        self.width = width
        self.height = height
        self.x = x
        self.y = y
        
        # 标记模块是否旋转
        self.rotated = False
        self.rotate_point = 0 # 0: 左下角, 1: 左上角, 2: 右上角, 3: 右下角
        self.placed = False
        
        # B*-树相关指针
        self.parent = None
        self.left = None
        self.right = None
        
    def updateAttr(self, block) -> None:
        if isinstance(block, Block):
            self.name = block.name
            self.width = block.width
            self.height = block.height
            self.x = block.x
            self.y = block.y
            self.rotated = block.rotated
            self.rotate_point = block.rotate_point
            self.placed = block.placed

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
    
    def get_nodes(self) -> list:
        return self.nodes
        
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
