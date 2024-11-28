'''
Descripttion: BStarTree impl for units, and simulate annealing method for floorplan optimization
Author: Albresky
Date: 2024-11-27 22:55:47
LastEditors: Albresky
LastEditTime: 2024-11-28 14:31:15
'''

import math, random
from fp_units import Outline, Block, Terminal, Nets, Blocks

class BStarTree:
    def __init__(self, blocks:Blocks, temperature:int=1000, alpha:float=0.95) -> None:
        self.blocks = blocks.get_units()
        self.root = None
        self.best_blocks = None  # 保存最优解
        self.block_dict = {block.name: block for block in self.blocks}
        self.operations = []  # 保存操作序列以便回溯
        
        # 模拟退火参数
        self.T = 1000
        self.alpha = 0.99

    def initialize(self) -> None:
        # 初始化 B*-树，随机排列模块
        random.shuffle(self.blocks)
        self.root = self.blocks[0]
        for block in self.blocks[1:]:
            self.insert(self.root, block)

    def insert(self, parent, block) -> None:
        # 随机插入左子节点或右子节点
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


    '''
    Description: Due to Python DOES NOT support tail recursion, 
                 we use iterations with stack to avoid recursion boom 
                 (Stack Overflow! LOL ;-D) )
    '''   
    def pack(self) -> None:
        def traverse_iter(node) -> None:
            stack = [(node, None, True)]  # Stack to hold nodes, their parents, and whether they are left children
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

    def perturb(self) -> None:
        # 执行扰动操作，如交换模块、旋转等
        action = random.choice(['swap', 'rotate', 'move'])
        if action == 'swap':
            self.swap_blocks()
        elif action == 'rotate':
            self.rotate_block()
        elif action == 'move':
            self.move_subtree()

    def swap_blocks(self) -> None:
        b1, b2 = random.sample(self.blocks, 2)
        
        # 交换模块在树中的位置
        self.exchange_nodes(b1, b2)
        self.operations.append(('swap', b1, b2))

    def rotate_block(self) -> None:
        block = random.choice(self.blocks)
        block.width, block.height = block.height, block.width
        block.rotated = not block.rotated
        self.operations.append(('rotate', block))

    def move_subtree(self) -> None:
        src, dst = random.sample(self.blocks, 2)
        original_parent = src.parent  # Store the original parent
        self.detach_node(src)
        self.attach_node(dst, src)
        self.operations.append(('move', src, dst, original_parent))

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
            src, dst, original_parent = action[1], action[2], action[3]
            self.detach_node(src)
            self.attach_node(original_parent, src)

    def simulate_annealing(self, outline:Outline, nets:Nets, max_iterations:int=1000) -> None:
        best_cost, _, _, _ = self.calculate_cost(nets)
        self.best_blocks = [block for block in self.blocks]

        for i in range(max_iterations):
            self.perturb()
            self.pack()
            # 检查是否超出芯片范围
            if not self.check_out_of_outline(outline):
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

    def check_out_of_outline(self, outline:Outline) -> bool:
        max_x = max(block.x + block.width for block in self.blocks)
        max_y = max(block.y + block.height for block in self.blocks)
        return max_x <= outline.w and max_y <= outline.h