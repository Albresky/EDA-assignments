'''
Descripttion: BStarTree impl for units, and simulate annealing method for floorplan optimization
Author: Albresky
Date: 2024-11-27 22:55:47
LastEditors: Albresky
LastEditTime: 2024-11-28 13:25:08
'''

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
        import random
        random.shuffle(self.blocks)
        self.root = self.blocks[0]
        for block in self.blocks[1:]:
            self.insert(self.root, block)

    def insert(self, parent, block):
        import random
        
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

    def pack(self):
        # 通过前序遍历计算每个模块的位置
        def traverse(node):
            if node.parent is None:
                node.x = 0
                node.y = 0
            else:
                if node == node.parent.left:
                    node.x = node.parent.x + node.parent.width
                    node.y = node.parent.y
                else:
                    node.x = node.parent.x
                    node.y = node.parent.y + node.parent.height
            if node.left:
                traverse(node.left)
            if node.right:
                traverse(node.right)
        if self.root:
            traverse(self.root)

    def perturb(self):
        # 执行扰动操作，如交换模块、旋转等
        import random
        action = random.choice(['swap', 'rotate', 'move'])
        if action == 'swap':
            self.swap_blocks()
        elif action == 'rotate':
            self.rotate_block()
        elif action == 'move':
            self.move_subtree()

    def swap_blocks(self):
        import random
        b1, b2 = random.sample(self.blocks, 2)
        # 交换模块在树中的位置
        self.exchange_nodes(b1, b2)
        self.operations.append(('swap', b1, b2))

    def rotate_block(self):
        import random
        block = random.choice(self.blocks)
        block.width, block.height = block.height, block.width
        block.rotated = not block.rotated
        self.operations.append(('rotate', block))

    def move_subtree(self):
        import random
        src, dst = random.sample(self.blocks, 2)
        original_parent = src.parent  # Store the original parent
        self.detach_node(src)
        self.attach_node(dst, src)
        self.operations.append(('move', src, dst, original_parent))

    def exchange_nodes(self, b1, b2):
        # 交换两个节点的位置
        b1.parent, b2.parent = b2.parent, b1.parent
        b1.left, b2.left = b2.left, b1.left
        b1.right, b2.right = b2.right, b1.right

    def detach_node(self, node):
        # 从树中删除节点
        parent = node.parent
        if parent:
            if parent.left == node:
                parent.left = None
            else:
                parent.right = None
        node.parent = None

    def attach_node(self, parent, node):
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

    def revert(self):
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

    def simulate_annealing(self, outline:Outline, nets:Nets, max_iterations:int=1000):
        import math
        import random
        
        best_cost, _, _ = self.calculate_cost(nets)
        self.best_blocks = [block for block in self.blocks]

        # self.print_tree()

        for i in range(max_iterations):
            self.perturb()
            self.pack()
            # 检查是否超出芯片范围
            if not self.check_out_of_outline(outline):
                self.revert()
                continue
            cost, _, _ = self.calculate_cost(nets)
            delta = cost - best_cost
            if delta < 0 or random.random() < math.exp(-delta / self.T):
                if cost < best_cost:
                    best_cost = cost
                    self.best_blocks = [block for block in self.blocks]
            else:
                self.revert()
            self.T *= self.alpha  # 降温

    def calculate_cost(self, nets:Nets, alpha=0.5) -> tuple:
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

        # 计算成本函数
        cost = alpha * area + (1 - alpha) * wirelength
        return cost, area, wirelength

    def check_out_of_outline(self, outline:Outline) -> bool:
        max_x = max(block.x + block.width for block in self.blocks)
        max_y = max(block.y + block.height for block in self.blocks)
        return max_x <= outline.w and max_y <= outline.h