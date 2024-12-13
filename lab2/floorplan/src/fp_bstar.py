'''
Descripttion: BStarTree impl for units, and simulate annealing method for floorplan optimization
Author: Albresky
Date: 2024-11-27 22:55:47
LastEditors: Albresky
LastEditTime: 2024-12-13 16:33:54
'''

import math, random, copy
from fp_units import Outline, Block, Terminal, Nets, Blocks

class BStarTree:
    def __init__(self, outline:Outline, blocks:Blocks, temperature:int=1000, alpha:float=0.95) -> None:
        self.outline = outline
        self.blocks = blocks.get_units()
        self.root = None
        self.best_blocks = None
        self.block_dict = {block.name: block for block in self.blocks}
        self.operations = []
        
        # 模拟退火参数
        self.T = 1000
        self.alpha = 0.99

                
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
        # 交换两个节点的位置
        b1.parent, b2.parent = b2.parent, b1.parent
        b1.left, b2.left = b2.left, b1.left
        b1.right, b2.right = b2.right, b1.right


    def detach_node(self, node) -> None:
        # 从树中删除节点
        parent = node.parent
        if parent:
            if parent.left == node:
                parent.left = None
            else:
                parent.right = None
        node.parent = None


    def attach_node(self, parent, node) -> None:
        if parent is None:
            # If parent is None, set node as the new root
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


    def move_block(self, block:Block=None, x:int=0, y:int=0) -> None:
        if block is None:
            block = random.choice(self.blocks)
        block.x -= x
        block.y -= y
        self.operations.append(('move', block, x, y))


    def swap_blocks(self) -> None:
        b1, b2 = random.sample(self.blocks, 2)
        
        # 交换模块在树中的位置
        self.exchange_nodes(b1, b2)
        self.operations.append(('swap', b1, b2))


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


    def move_subtree(self) -> None:
        src, dst = random.sample(self.blocks, 2)
        original_parent = src.parent  # Store the original parent
        self.detach_node(src)
        self.attach_node(dst, src)
        self.operations.append(('move', src, dst, original_parent))


    '''
    Description: Revert the last operation
    '''
    def revert(self) -> None:
        if not self.operations:
            return
        action = self.operations.pop()
        if action[0] == 'swap':
            self.exchange_nodes(action[1], action[2])
        elif action[0] == 'rotate':
            block = action[1]
            block.width, block.height = block.height, block.width
            block.rotated = not block.rotated
        elif action[0] == 'move':
            # src, dst, original_parent = action[1], action[2], action[3]
            # self.detach_node(src)
            # self.attach_node(original_parent, src)
            x_step = action[1]
            y_step = action[2]
            self.move_block(block, -1*x_step, -1*y_step)


    def initialize(self) -> None:
        # Sort the blocks from large to small based on area (width * height)
        self.blocks.sort(key=lambda block: block.width * block.height, reverse=True)
        placed_blocks = []

        for block in self.blocks:
            block.placed = False
            block.x = 0
            block.y = 0

            while not block.placed :
                self.adjust_position(block, max_trials=99, random_pos=False)
                
            if block.placed:
                print(f'[init] Block {block.name} placed at ({block.x}, {block.y})')
            else:
                print(f'[init] Block {block.name} cannot be placed')
            
            placed_blocks.append(block)

        # Set up the B*-tree structure
        self.root = placed_blocks[0]
        for block in placed_blocks[1:]:
            self.insert(self.root, block)


    '''
    Description: Pack the blocks in the floorplan 
                
                 Due to Python DOES NOT support tail recursion, 
                 we use iterations with stack to avoid recursion boom 
                 (Stack Overflow! LOL ;-D) )
    '''   
    def pack(self):
        def traverse_iter(node):
            stack = [(node, None, True)]  # Stack to hold nodes, their  parents, and whether they are left children
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

                # if self.check_valid(current):
                #     self.adjust_position(current)

                if current.right:
                    stack.append((current.right, current, False))
                if current.left:
                    stack.append((current.left, current, True))

        if self.root:
            traverse_iter(self.root)


    def check_out_of_outline(self, outline: Outline) -> bool:
        for block in self.blocks:
            if block.x + block.width > outline.w or block.y + block.height > outline.h or block.x < 0 or block.y < 0:
                return True
        return False
    
    
    def is_block_within_outline(self, block:Block) -> bool:
        res = (block.x >= 0) and (block.y >= 0) and (block.x + block.width <= self.outline.w) and (block.y + block.height <= self.outline.h)
        # if not res:
            # print(f'Block {block.name} is out of outline')
        return res
    
    
    def check_overlap(self, block) -> bool:
        for other in self.blocks:
            if other.name != block.name and other.placed:
                if not (block.x + block.width <= other.x or block.x >= other.x  + other.width or
                        block.y + block.height <= other.y or block.y >= other.y + other.height):
                    # print(f'block {block.name} is overlapped with {other.name}')
                    return True # has overlap
        return False


    def check_valid(self, block) -> bool:
        return self.is_block_within_outline(block) and not self.check_overlap(block)
    

    def check_valid_all(self) -> bool:
        for _ in self.blocks:
            if not _.placed:
                print(f'Block {_.name} is not placed')
            if not self.check_valid(_):
                print(f'Block {_.name} is invalid @({_.x}, {_.y})')
            

    def get_rdm_pos(self, block:Block) -> tuple:
        while True:
            # random seed
            x = random.randint(0, self.outline.w - block.width)
            y = random.randint(0, self.outline.h - block.height)
            # print(f'Random position for block {block.name}: ({x}, {y})')

            # check if the coordinate is within other blocks
            for b in self.blocks:
                if b.name != block.name:
                    if not ((x > b.x) and (x <b.x + b.width) and y > b.y and y <b.y+b.height):
                        break
                else:
                    # print(f'Random position for block {block.name}: ({x}, {y})')
                    return (x, y)


    '''
    Description: Get the best position for the block
    '''
    def adjust_position(self, block:Block, max_trials:int=10, random_pos:bool=False) -> Block:
        best_block = Block()
        min_cost = float('inf')
        possible_positions = None
        
        if random_pos:
            # Get a random position
            possible_positions = self.get_rdm_pos(block)
        else:
            # Use strategy to adjust the position
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
            # print(f'Find best position for block: {best_block.name}, cost: {min_cost}')
            best_block.placed = True
            block.updateAttr(best_block)
        # Step 2: If no valid position found, adjust the position randomly
        elif max_trials > 0: 
            max_trials -= 1
            self.adjust_position(block, max_trials, random_pos=True)

 
    '''
    Description: Get all possible positions for a block in the left space
    '''
    def get_possible_positions(self, block:Block):
        positions = []
        for other in self.blocks:
            if other.name != block.name and other.placed:
                positions.append((other.x + other.width, other.y))
                positions.append((other.x, other.y + other.height))
        if len(positions) == 0:
            positions.append((0, 0))
        # print(f'Possible positions for block {block.name}: {len(positions)}x')
        return positions


    def calculate_cost_for_block(self, block):
        # 计算单个 block 的成本
        cost = 0
        for other in self.blocks:
            if other.name != block.name:
                cost += abs(block.x - other.x) + abs(block.y - other.y)
        return cost


    '''
    Description: Perturb the current floorplan
    '''
    def perturb(self) -> None:
        # 执行扰动操作，如交换模块、旋转等
        action = random.choice(['rotate', 'move'])
        if action == 'swap':
            self.swap_blocks()
        elif action == 'rotate':
            self.rotate_block()
        elif action == 'move':
            self.move_block(x=1, y=1)


    '''
    Description: The Simulate Annealing function to find optimal floorplan.
    '''
    def simulate_annealing(self, nets:Nets, max_iterations:int=1000) -> None:
        best_cost, _, _, _ = self.calculate_cost(nets)
        self.best_blocks = [block for block in self.blocks]
    
        for i in range(max_iterations):
            self.perturb()
            # self.pack()
            # 检查是否超出芯片范围
            if self.check_valid_all():
                self.revert()
                continue
            cost, _, _, _ = self.calculate_cost(nets)
            delta = cost - best_cost
            if delta < 0 or random.random() < math.exp(-delta / self.T):
                if cost < best_cost:
                    best_cost = cost
                    self.best_blocks = [block for block in self.blocks]
            else:
                self.revert()
            self.T *= self.alpha  # 降温
            
            print(f'Iteration: {i}, Cost: {cost}, Best Cost: {best_cost}, T: {self.T}', flush=True)


    '''
    Description: Calculate the number of adjacent long edges,
                 add this as benifit to the cost function
    '''
    def calculate_adjacent_long_edges(self, nets) -> None:
        adjacent_long_edges = 0
        for net in nets.get_units():
            for i in range(len(net.get_nodes()) - 1):
                for j in range(i + 1, len(net.get_nodes())):
                    node1 = net.get_nodes()[i]
                    node2 = net.get_nodes()[j]
                    if isinstance(node1, Block) and isinstance(node2, Block):
                        if (node1.x == node2.x and abs(node1.y - node2.y) == max(node1.height, node2.height)) or \
                           (node1.y == node2.y and abs(node1.x - node2.x) == max(node1.width, node2.width)):
                            adjacent_long_edges += 1
        return adjacent_long_edges


    def calculate_cost(self, nets:Nets, alpha=0.5, beta=0.5) -> tuple:
        # 计算面积和线长
        _blocks = self.blocks
        min_x = min(block.x for block in _blocks)
        min_y = min(block.y for block in _blocks)
        max_x = max(block.x + block.width for block in _blocks)
        max_y = max(block.y + block.height for block in _blocks)
        area = (max_x - min_x) * (max_y - min_y)

        wirelength = 0
        for net in nets.get_units():
            xs = []
            ys = []
            for node in net.get_nodes():
                if isinstance(node, Block):
                    xs.append(node.x + node.width / 2)
                    ys.append(node.y + node.height / 2)
                elif isinstance(node, Terminal):
                    xs.append(node.x)
                    ys.append(node.y)
            wirelength += (max(xs) - min(xs)) + (max(ys) - min(ys))

        # 计算相邻长边的奖励
        adjacent_long_edges = self.calculate_adjacent_long_edges(nets)

        # 计算成本函数
        cost = alpha * area + (1 - alpha) * wirelength - beta * adjacent_long_edges
        return cost, area, wirelength, adjacent_long_edges
