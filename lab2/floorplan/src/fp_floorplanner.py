'''
Copyright (c) 2024 by Albresky, All Rights Reserved. 

Author: Albresky albre02@outlook.com
Date: 2024-12-21 20:22:50
LastEditTime: 2024-12-24 22:22:38
FilePath: /EDA-assignments/lab2/floorplan/src/fp_floorplanner.py

Description: Floorplanner based on B*-tree, featured with and perturbation simulated annealing.
'''

import random
import math
from fp_units import Outline, Terminal, Terminals, Block, Blocks, Nets
from fp_bstar import BStarTree

class FloorPlanner:
    """The floorplanner class is used to place the blocks within the outline and optimize the floorplan using simulated annealing.
    """
    def __init__(self, 
                 outline:Outline, 
                 blocks:Blocks, 
                 terminals:Terminals, 
                 nets:Nets, 
                 temperature: int = 1000, 
                 alpha: float = 0.95
        ) -> None:
        """The constructor of the floorplanner.

        Args:
            outline (_type_): The Outline object.
            blocks (Blocks): The Blocks object.
            terminals (Terminals): The Terminals object.
            nets (Nets): The Nets object.
            temperature (int, optional): Parameter for simulated annealing. Defaults to 1000.
            alpha (float, optional): Parameter for simulated annealing. Defaults to 0.95.
        """
        self.outline = outline
        self.blocks = blocks.get_units()
        self.terminals = terminals.get_units()
        self.nets = nets.get_units()
        self.bstar_tree = BStarTree(outline, blocks)
        self.temperature = temperature
        self.alpha = alpha
        self.best_cost = float('inf')
        self.operations = []
        self.avg_wirelen = self.calculate_avg_wirelen()

    def initialize(self) -> None:
        """Initialize the floorplanner by placing the blocks within the outline,
        the initialization will find a valid position for each block.
        """
        # Sort the blocks from large to small based on area(width * height)
        self.blocks.sort(key=lambda block: block.width * block.height, reverse=True)
        placed_blocks = []

        for block in self.blocks:
            block.placed = False
            block.x = 0
            block.y = 0

            while not block.placed:
                self.adjust_position(block, max_trials=99, random_pos=False)

            placed_blocks.append(block)

        # Set up the B*-tree structure
        # self.bstar_tree.root = placed_blocks[0]
        # for block in placed_blocks[1:]:
        #     self.bstar_tree.insert(self.bstar_tree.root, block)

    def adjust_position(self, block: Block, max_trials: int = 10, random_pos: bool = False) -> Block:
        """Adjust the position of the block to find a valid position, adjust method: rotate.
                
        Args:
            block (Block): the block ref to adjust.
            max_trials (int, optional): Max trials to adjust the position. Defaults to 10.
            random_pos (bool, optional): Adjust the position randomly. Defaults to False.

        Returns:
            Block: The adjusted block ref.
        """
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
                cost, _, _ = self.calculate_cost()
                if cost <= min_cost:
                    min_cost = cost
                    best_block.updateAttr(block)
            else:
                self.rotate_block(block)
                if self.check_valid(block):
                    cost, _, _ = self.calculate_cost()
                    if cost <= min_cost:
                        min_cost = cost
                        best_block.updateAttr(block)
                else:
                    self.revert(block)

        if best_block.name and self.check_valid(best_block):
            best_block.placed = True
            block.updateAttr(best_block)
        elif max_trials > 0:
            max_trials -= 1
            self.adjust_position(block, max_trials, random_pos=True)

    def get_possible_positions(self, block:Block) -> list:
        """Get all possible positions for a block within left space.
        
        Args:
            block (Block): The block ref to get possible positions.

        Returns:
            list: A list of possible positions for the given block.
        """
        positions = []
        for other in self.blocks:
            if other.name != block.name and other.placed:
                positions.append((other.x + other.width, other.y))
                positions.append((other.x, other.y + other.height))
        if len(positions) == 0:
            positions.append((0, 0))
        return positions
    
    def get_rdm_pos(self, block: Block) -> tuple:
        """Get a random position for a block within the outline.
        
        Args:
            block (Block): The block ref to get a random position.

        Returns:
            tuple: A random coordinate (x, y) to place the block.
        """
        
        while True:
            x = random.randint(0, self.outline.w - block.width)
            y = random.randint(0, self.outline.h - block.height)

            for b in self.blocks:
                if b.name != block.name:
                    if not ((x > b.x) and (x < b.x + b.width) and y > b.y and y < b.y + b.height):
                        break
                else:
                    return (x, y)

    def check_valid(self, 
                    block: Block
    ) -> bool:
        """Check if the block is valid within the outline and does not overlap with other blocks.
        
        Args:
            block (Block): _description_

        Returns:
            bool: Whether the block is valid.
        """
        
        return self.is_block_within_outline(block) and not self.check_overlap(block)

    def check_valid_all(self) -> bool:
        """Check if all blocks are valid within the outline and do not overlap with each other.
        
        Returns:
            bool: Whether all blocks are valid.
        """
        
        isvalid = True
        for block in self.blocks:
            if not block.placed:
                print(f'Block {block.name} is not placed')
                return False
            if not self.check_valid(block):
                print(f'Block {block.name} is invalid @({block.x}, {block.y})')
                isvalid = False
        return isvalid

    def is_block_within_outline(self, 
                                block: Block
        ) -> bool:
        """Check if the block is within the outline.
        
        Args:
            block (Block): The block ref to check.

        Returns:
            bool: Whether the block is within the outline.
        """
        
        return (block.x >= 0) and (block.y >= 0) and (block.x + block.width <= self.outline.w) and (block.y + block.height <= self.outline.h)

    def check_overlap(self, 
                      block
        ) -> bool:
        """Check if the block overlaps with other blocks.
        Args:
            block (_type_): The block ref to check.

        Returns:
            bool: Whether the block overlaps with other blocks.
        """
        
        for other in self.blocks:
            if other.name != block.name and other.placed:
                if not (block.x + block.width <= other.x or block.x >= other.x + other.width or
                        block.y + block.height <= other.y or block.y >= other.y + other.height):
                    # print(f'Overlap between {block.name}@(x={block.x}, y={block.y}) and {other.name}@(x={other.x}, y={other.y})')
                    return True
        return False

    def simulate_annealing(self, 
                           max_iterations:int = 1000
        ) -> None:
        """The main function of simulated annealing, optimize the floorplan by perturbing the blocks.

        Args:
            max_iterations (int, optional): The max iterations of the simulated annealing. Defaults to 1000.
        """
        
        recent_costs = []
        
        for i in range(max_iterations):
            best_cost, _, _ = self.calculate_cost()
            for blk in self.blocks:
                self.perturb(blk)
                if not self.check_valid(blk):
                    self.revert(blk)
                    continue
                cost, _, _ = self.calculate_cost()
                delta = cost - best_cost
                if delta < 0 or random.random() < math.exp(-delta / self.temperature):
                    if cost <= best_cost:
                        best_cost = cost
                else:
                    self.revert(blk)
                self.temperature *= self.alpha

            self.best_cost = best_cost
                
            # Update the latest cost
            recent_costs.append(best_cost)
            if len(recent_costs) > 10:
                recent_costs.pop(0)

            # Check convergence
            if len(recent_costs) == 10 and abs(sum(recent_costs) - recent_costs[0]*10) < 1e-9:
                print(f"SA has converged at iteration {i} with cost {best_cost}")
                break
            print(f"SA[{i}] Cost={best_cost}")
            
        print(f'SA finished, {len(self.blocks)}')

    def perturb(self, 
                block:Block
        ) -> Block:
        """The perturbation function of the simulated annealing, perturb the block by rotating or moving at random.

        Args:
            block (Block): The block ref to perturb.

        Returns:
            Block: The perturbed block ref.
        """
        
        magic = random.randint(0, 100)
        
        # action == 'rotate'
        if magic < 10:
            self.rotate_block(block, first_try=True)
        # action == 'move'
        else:
            choice = random.randint(0, 1)
            if choice == 0:
                # down
                self.move_block(block, x=0, y=-1, first_try=True)
            elif choice == 1:
                # left
                self.move_block(block, x=-1, y=0, first_try=True)

    '''
    Description: Rotate the block for 90 degrees, rotate in the center of the block(x, y)
                 Rotated block positioned at the top or below the block.
    '''
    def rotate_block(self, 
                     block:Block=None, 
                     first_try=True
        ) -> None:
        """Rotate the block for 90 degrees, rotate in the center of the block(x, y).

        Args:
            block (Block, optional): The block ref to rotate. Defaults to None.
            first_try (bool, optional): Whether it is the first try to rotate the block. Defaults to True.
        """
        
        if block is None:
            block = random.choice(self.blocks)
        
        block.rotated = True
        block.width, block.height = block.height, block.width
        if first_try:
            self.operations.append(('rotate', block))

    def move_block(self, 
                   block:Block=None, 
                   x: int = 1, 
                   y: int = 1, 
                   first_try=True
        ) -> None:
        """The move function of the simulated annealing, move the block by step x, y.

        Args:
            block (Block, optional): The block ref to move. Defaults to None.
            x (int, optional): The x step to move. Defaults to 1.
            y (int, optional): The y step to move. Defaults to 1.
            first_try (bool, optional): Whether it is the first try to move the block. Defaults to True.
        """
        if block is None:
            block = random.choice(self.blocks)
        block.x += x
        block.y += y
        if first_try:
            self.operations.append(('move', block, x, y))
    
    def revert(self, 
               block:Block
        ) -> None:
        """The revert function of the simulated annealing, revert the last operation from rotate or move.

        Args:
            block (Block): The block ref to revert.
        """
        
        if not self.operations:
            return
        action = self.operations.pop()
        # Revert the last operation (swap, move, or rotate)
        if action[0] == 'rotate':
            self.rotate_block(block, first_try=False)
        elif action[0] == 'move':
            self.move_block(block, x=0-int(action[2]), y=0-int(action[3]), first_try=False)

    '''
    Description: Calculate cost using area, wirelength, and adjacent long edges
    '''
    def calculate_cost(self) -> tuple:
        """The cost function of the simulated annealing, calculate the cost of the floorplan. The cost is calculated by the area and wirelength. The wirelength is calculated by half-perimeter wirelength.

        Returns:
            tuple: The cost, area, and wirelength of current floorplan.
        """
        
        area, area_norm = self.calculate_area()
        wire_len = self.calculate_wirelength()
        cost = self.alpha * area/area_norm + (1 - self.alpha) * wire_len / self.avg_wirelen
        return cost, area, wire_len

    def calculate_area(self) -> int:
        """Calculate the area of the floorplan.

        Returns:
            int: The area of the floorplan.
        """
        area, area_norm = 0, 0
        max_x, max_y = 0, 0
        
        for block in self.blocks:
            area_norm += block.width * block.height
            
        for block in self.blocks:
            if block.x + block.width > max_x:
                max_x = block.x + block.width
            if block.y + block.height > max_y:
                max_y = block.y + block.height
        area = max_x * max_y
        return area, area_norm
    
    def calculate_wirelength(self) -> int:
        """Calculate the wirelength of the floorplan.

        Returns:
            int: The wirelength of the floorplan.
        """
        total_wirelength = 0

        for net in self.nets:
            min_x = float('inf')
            min_y = float('inf')
            max_x = float('-inf')
            max_y = float('-inf')

            for _node in net.get_nodes():
                if isinstance(_node, Block):
                    x1 = _node.x
                    y1 = _node.y
                    x2 = _node.x + _node.width
                    y2 = _node.y + _node.height
                elif isinstance(_node, Terminal):
                    x1 = _node.x
                    y1 = _node.y
                    x2 = _node.x
                    y2 = _node.y
                else:
                    continue

                min_x = min(min_x, x1)
                min_y = min(min_y, y1)
                max_x = max(max_x, x2)
                max_y = max(max_y, y2)

            hpwl = (max_x - min_x) + (max_y - min_y)
            total_wirelength += hpwl

        return total_wirelength

    def calculate_avg_wirelen(self) -> int:
        """Calculate the average wirelength of the floorplan.

        Returns:
            int: The average wirelength of the floorplan.
        """
        total_wl = 0
        for bk in self.blocks:
            total_wl += 0.5 * (bk.width + bk.height)
        return int(total_wl / len(self.blocks))
            
