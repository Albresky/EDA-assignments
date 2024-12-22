'''
Copyright (c) 2024 by Albresky, All Rights Reserved. 

Author: Albresky albre02@outlook.com
Date: 2024-12-21 20:04:49
LastEditTime: 2024-12-22 19:20:55
FilePath: /EDA-assignments/lab2/floorplan/src/fp_bstar.py

Description: BStarTree structure for units.
'''

import math, random, copy
from fp_units import Outline, Block, Nets, Blocks

class BStarTree:
    def __init__(self, outline: Outline, blocks: Blocks) -> None:
        self.outline = outline
        self.blocks = blocks.get_units()
        self.root = None
        self.block_dict = {block.name: block for block in self.blocks}
    
    def insert(self, parent, block) -> None:
        if random.choice([True, False]):
            if parent.left is None:
                parent.left = block
                block.parent = parent
            else:
                self.insert(parent.left, block)
        else:
            if parent.right is None:
                parent.right = block
                block.parent = parent
            else:
                self.insert(parent.right, block)
    
    def exchange_nodes(self, b1, b2) -> None:
        b1.parent, b2.parent = b2.parent, b1.parent
        b1.left, b2.left = b2.left, b1.left
        b1.right, b2.right = b2.right, b1.right
    
    def detach_node(self, node) -> None:
        parent = node.parent
        if parent:
            if parent.left == node:
                parent.left = None
            else:
                parent.right = None
        node.parent = None

    def attach_node(self, parent, node) -> None:
        if parent is None:
            self.root = node
            node.parent = None
        else:
            if not parent.left:
                parent.left = node
                node.parent = parent
            elif not parent.right:
                parent.right = node
                node.parent = parent
            else:
                self.attach_node(parent.left, node)

    def pack(self) -> None:
        def traverse_iter(node) -> None:
            stack = [(node, None, True)]
            while stack:
                current, parent, is_left_child = stack.pop()
                if parent is None:
                    current.x = 0
                    current.y = 0
                else:
                    if is_left_child:
                        current.x = parent.x + parent.width
                        current.y = parent.y
                    else:
                        current.x = parent.x
                        current.y = parent.y + parent.height

                if current.right:
                    stack.append((current.right, current, False))
                if current.left:
                    stack.append((current.left, current, True))

        if self.root:
            traverse_iter(self.root)
