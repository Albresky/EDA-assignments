'''
Copyright (c) 2024 by Albresky, All Rights Reserved. 

Author: Albresky albre02@outlook.com
Date: 2024-12-21 20:22:50
LastEditTime: 2024-12-22 19:19:38
FilePath: /EDA-assignments/lab2/floorplan/src/fp_floorplanner.py

Description: Floorplanner based on B*-tree, featured with and perturbation simulated annealing.
'''

import random
import math
from fp_units import Block, Nets
from fp_bstar import BStarTree

class FloorPlanner:
    def __init__(self, outline, blocks, temperature: int = 1000, alpha: float = 0.95) -> None:
        self.outline = outline
        self.blocks = blocks.get_units()
        self.bstar_tree = BStarTree(outline, blocks)
        self.temperature = temperature
        self.alpha = alpha
        self.best_blocks = None
        self.operations = []

    def initialize(self) -> None:
        # Sort the blocks from large to small based on area (width * height)
        self.blocks.sort(key=lambda block: block.width * block.height, reverse=True)
        placed_blocks = []

        for block in self.blocks:
            block.placed = False
            block.x = 0
            block.y = 0

            while not block.placed:
                self.adjust_position(block, max_trials=99, random_pos=False)

            if block.placed:
                print(f'[init] Block {block.name} placed at ({block.x}, {block.y})')
            else:
                print(f'[init] Block {block.name} cannot be placed')

            placed_blocks.append(block)

        # Set up the B*-tree structure
        self.bstar_tree.root = placed_blocks[0]
        for block in placed_blocks[1:]:
            self.bstar_tree.insert(self.bstar_tree.root, block)

    def adjust_position(self, block: Block, max_trials: int = 10, random_pos: bool = False) -> Block:
        best_block = Block()
        min_cost = float('inf')
        possible_positions = None

        if random_pos:
            possible_positions = self.get_rdm_pos(block)
        else:
            possible_positions = self.get_possible_positions(block)

        for pos in possible_positions:
            block.x, block.y = pos
            if self.check_valid(block):
                cost = self.calculate_cost_for_block(block)
                if cost < min_cost:
                    min_cost = cost
                    best_block.updateAttr(block)
            else:
                self.rotate_block(block)
                if self.check_valid(block):
                    cost = self.calculate_cost_for_block(block)
                    if cost < min_cost:
                        min_cost = cost
                        best_block.updateAttr(block)
                else:
                    self.rotate_block(block)

        if best_block.name and self.check_valid(best_block):
            best_block.placed = True
            block.updateAttr(best_block)
        elif max_trials > 0:
            max_trials -= 1
            self.adjust_position(block, max_trials, random_pos=True)

    '''
    Description: Get all possible positions for a block in the left space
    '''
    def get_possible_positions(self, block:Block) -> list:
        positions = []
        for other in self.blocks:
            if other.name != block.name and other.placed:
                positions.append((other.x + other.width, other.y))
                positions.append((other.x, other.y + other.height))
        if len(positions) == 0:
            positions.append((0, 0))
        # print(f'Possible positions for block {block.name}: {len(positions)}x')
        return positions
    
    def get_rdm_pos(self, block: Block) -> tuple:
        while True:
            x = random.randint(0, self.outline.w - block.width)
            y = random.randint(0, self.outline.h - block.height)

            for b in self.blocks:
                if b.name != block.name:
                    if not ((x > b.x) and (x < b.x + b.width) and y > b.y and y < b.y + b.height):
                        break
                else:
                    return (x, y)

    def check_valid(self, block: Block) -> bool:
        return self.is_block_within_outline(block) and not self.check_overlap(block)

    def is_block_within_outline(self, block: Block) -> bool:
        return (block.x >= 0) and (block.y >= 0) and (block.x + block.width <= self.outline.w) and (block.y + block.height <= self.outline.h)

    def check_overlap(self, block) -> bool:
        for other in self.blocks:
            if other.name != block.name and other.placed:
                if not (block.x + block.width <= other.x or block.x >= other.x + other.width or
                        block.y + block.height <= other.y or block.y >= other.y + other.height):
                    return True
        return False

    def simulate_annealing(self, nets: Nets, max_iterations: int = 1000) -> None:
        best_cost, _, _, _ = self.calculate_cost(nets)
        self.best_blocks = [block for block in self.blocks]

        for i in range(max_iterations):
            self.perturb()
            if self.check_valid_all():
                self.revert()
                continue
            cost, _, _, _ = self.calculate_cost(nets)
            delta = cost - best_cost
            if delta < 0 or random.random() < math.exp(-delta / self.temperature):
                if cost < best_cost:
                    best_cost = cost
                    self.best_blocks = [block for block in self.blocks]
            else:
                self.revert()
            self.temperature *= self.alpha

    def perturb(self) -> None:
        action = random.choice(['rotate', 'move'])
        if action == 'rotate':
            self.rotate_block()
        elif action == 'move':
            self.move_block(x=1, y=1)

    '''
    Description: Rotate the block for 90 degrees, rotate in the center of the block(x, y)
                 Rotated block positioned at the top or below the block.
    '''
    def rotate_block(self, block:Block=None) -> None:
        if block is None:
            block = random.choice(self.blocks)
        
        block.rotated = not block.rotated
        block.width, block.height = block.height, block.width
        self.operations.append(('rotate', block))
        return None    

    def revert(self) -> None:
        if not self.operations:
            return
        action = self.operations.pop()
        # Revert the last operation (swap, move, or rotate)

    def calculate_cost(self, nets: Nets, alpha=0.5, beta=0.5) -> tuple:
        # Calculate cost using area, wirelength, and adjacent long edges
        area, wirelength, adjacent_long_edges = self.calculate_area_wirelength_and_adjacent_edges(nets)
        cost = alpha * area + (1 - alpha) * wirelength - beta * adjacent_long_edges
        return cost, area, wirelength, adjacent_long_edges

    def calculate_area_wirelength_and_adjacent_edges(self, nets: Nets) -> tuple:
        # Calculate area, wirelength, and adjacent long edges here
        area = 0
        wirelength = 0
        adjacent_long_edges = 0
        return area, wirelength, adjacent_long_edges

    def calculate_cost_for_block(self, block) -> int:
        # 计算单个 block 的成本
        cost = 0
        for other in self.blocks:
            if other.name != block.name:
                cost += abs(block.x - other.x) + abs(block.y - other.y)
        return cost

    def check_valid_all(self) -> bool:
        for block in self.blocks:
            if not block.placed:
                print(f'Block {block.name} is not placed')
            if not self.check_valid(block):
                print(f'Block {block.name} is invalid @({block.x}, {block.y})')
