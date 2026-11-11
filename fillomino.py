from copy import deepcopy
from itertools import combinations as combos
import matplotlib.pyplot as plt
import matplotlib.lines as mlines
import matplotlib.patches as patches
from math import pi, cos, sin, sqrt, gcd


class Cell:
    
    def __init__(self, address, val=None, locked=False):
        row, col = address
        self.address = address
        self.value = val
        self.restricted = set()
        self.locked = locked
        self.nbrs = {(row - 1, col),
                     (row, col + 1),
                     (row + 1, col),
                     (row, col - 1)}
        self.count_in = None
        
    def copy(self):
        new = Cell(self.address, self.value, self.locked)
        new.restricted = deepcopy(self.restricted)
        return new
        
class Board:
    
    def __init__(self, dims, givens):
        rows, cols = dims
        self.dims = dims
        self.givens = deepcopy(givens)
        self.cells = {(r, c): Cell((r, c)) for r in range(rows) for c in range(cols)}
        for addy, val in givens.items():
            self.cells[addy].value = val
        for cell in self.cells.values():
            bad = set()
            for nbr in cell.nbrs:
                r, c = nbr
                if r < 0 or r >= rows or c < 0 or c >= cols or self.cells[nbr].value is not None:
                    bad.add(nbr)
            cell.nbrs = cell.nbrs - bad
        self.components = None
                    
    def copy(self):
        new = Board(self.dims, self.givens)
        new.cells = deepcopy(self.cells)
        
        return new
        
    def __str__(self):
        rows, cols = self.dims
        outrows = []
        for row in range(rows):
            thisrow = []
            for col in range(cols):
                tup = (row, col)
                val = self.cells[tup].value
                char = '.' if val is None else str(val)
                thisrow.append(char)
            outrows.append(''.join(thisrow))
        return '\n'.join(outrows)
    
    __repr__ = __str__
    
    def find_connected_components(self):
        pool = {tup for tup in self.cells.keys() if (self.cells[tup].locked is False 
                                                     and self.cells[tup].value is not None)}
        comp = set()
        comv = None
        to_check = set()
        components = []
        while len(pool) > 0 or len(to_check) > 0:
            if len(to_check) == 0:
                if len(comp) > 0:
                    components.append([comv, comp])
                    comp = set()
                seed = pool.pop()
                to_check.add(seed)
                comv = self.cells[seed].value
            current = to_check.pop()
            comp.add(current)
            row, col = self.cells[current].address
            nbrs = {(row - 1, col),
                    (row, col + 1),
                    (row + 1, col),
                    (row, col - 1)}
            for nbr in nbrs:
                if nbr in pool and self.cells[nbr].value == comv and nbr not in comp:
                    to_check.add(nbr)
                    pool.discard(nbr)
        if len(comp) > 0:
            components.append([comv, comp])
        self.components = components
        
    def check_connected_components(self):
        new = []
        for comv, comp in self.components:
            # print(comv, len(comp))
            if len(comp) > comv:
                return False
            if len(comp) == comv:
                for tup in comp:
                    self.cells[tup].locked = True
                    for nbr in self.cells[tup].nbrs:
                        self.cells[nbr].restricted.add(comv)
            else:
                cnbrs = set()
                for tup in comp:
                    cnbrs |= self.cells[tup].nbrs
                if len(comp) < comv and len(cnbrs) == 0:
                    return False
                new.append([comv, comp])
        self.components = new
        
        return True
    
    def check_for_orphans(self):
        
        for cell in self.cells.values():
            if cell.value is None:
                # comv = cell.value
                
                row, col = cell.address
                nbrs = {(row - 1, col),
                        (row, col + 1),
                        (row + 1, col),
                        (row, col - 1)}
                
                locked = []
                ones = []
                for nbr in nbrs:
                    if nbr in self.cells:
                        test = self.cells[nbr].value in cell.restricted
                        locked.append(self.cells[nbr].locked or test) 
                        ones.append(self.cells[nbr].value == 1)
                        if self.cells[nbr].locked is False:
                            temp_val = self.cells[nbr].value
                if any(ones) and all(locked):
                    return False
                
                if any(ones) and locked.count(False) == 1 and temp_val is not None:
                    cell.value = temp_val
                    for nbr in nbrs:
                        if nbr in self.cells and self.cells[nbr].value != temp_val:
                            self.cells[nbr].nbrs.discard(cell.address)
                    self.find_connected_components()
                    test = self.check_connected_components()
                    if test is False:
                        return False
                    # print(cell.address)
                    return self.check_for_orphans()
                            
                    
        return True
                        
    def children_comp(self):
        children = []
        if len(self.components) == 0:
            return children
        for comv, comp in self.components:
            cnbrs = set()
            for tup in comp:
                
                for nbr in self.cells[tup].nbrs:
                    if comv not in self.cells[nbr].restricted and comv != self.cells[nbr].value:
                        cnbrs.add(nbr)
            if len(cnbrs) == 1:
                break
        diff = comv - len(comp)
        for nadd in range(1, diff + 1):
            for combo in combos(cnbrs, nadd):
                complement = cnbrs - set(combo)
                child = self.copy()
                child_comp = comp | set(combo)
                for new in combo:
                    child.cells[new].value = comv
                    row, col = new
                    nbrs = {(row - 1, col),
                            (row, col + 1),
                            (row + 1, col),
                            (row, col - 1)}
                    for nbr in nbrs:
                        if nbr in child.cells:
                            child.cells[nbr].nbrs.discard(new)    
                for new in complement:
                    child.cells[new].restricted.add(comv)
                    for addr in child_comp:
                        child.cells[addr].nbrs.discard(new)
                child.find_connected_components()
                test = child.check_connected_components()
                if test is True:
                    test = child.check_for_orphans()
                    if test is True:
                        children.append(child)
                    
        return children
    
    def children_cell(self):
        children = []
        found = False
        for addr, cell in self.cells.items():
            if cell.value is None:
                found = True
                break
        if found is False:
            return children
        testval = 1
        while testval in cell.restricted:
            testval += 1 
        child_with = self.copy()
        child_with.cells[addr].value = testval
        row, col = addr
        nbrs = {(row - 1, col),
                (row, col + 1),
                (row + 1, col),
                (row, col - 1)}
        for nbr in nbrs:
            if nbr in child_with.cells:
                child_with.cells[nbr].nbrs.discard(addr)  
        child_with.find_connected_components()
        test = child_with.check_connected_components()
        if test is True:
            test = child_with.check_for_orphans()
            if test is True:
                children.append(child_with)
        child_wo = self.copy()
        child_wo.cells[addr].restricted.add(testval)
        children.append(child_wo)
        
        return children
        
    def is_complete(self): 
        for cell in self.cells.values():
            if cell.locked is False:
                return False
            
        return True
    
    @staticmethod
    def _get_color_list(n, step, floor, start=0):
        ang = 2 * pi * step/n
        R = sqrt(1/3)
        k = 1 - floor
        coords = [[sqrt(6) / 3, R * cos(i * ang), R * sin(i * ang)] for i in range(n)]
        M = [[sqrt(3)/3, -sqrt(3)/3, -sqrt(3)/3],
             [sqrt(3)/3, (3+sqrt(3))/6, -(3-sqrt(3))/6],
             [sqrt(3)/3,  -(3-sqrt(3))/6, (3+sqrt(3))/6]]
        colors = []
        for xyz in coords:
            new = [floor + k * sum(a*b for a, b in zip(xyz, row)) for row in M]
            colors.append(new)
            floor += (1 - floor) / n
            k = 1 - floor
            x, y, z = xyz        
        return colors
    
    def plot(self):
        rows, cols = self.dims
        fig, ax = plt.subplots()
        fig.set_size_inches(rows, cols)
        ax.set_aspect(1)
        ax.axis('off')
        ax.set_xlim([0, 100 * cols])
        ax.set_ylim([0, 100 * rows])
    
        # draw background grid
        for row in range(rows + 1):
            if row == 0 or row == rows:
                c = '#000000' # black
                z = 5
            else:
                c = '#dddddd' # light gray
                z = 0
            xs = [0, cols * 100]
            ys = [row * 100, row * 100]
            line = mlines.Line2D(xs, ys, color = c, zorder = z)
            ax.add_line(line)     
        for col in range(cols + 1):
            if col == 0 or col == cols:
                c = '#000000' # black
                z = 5
            else:
                c = '#dddddd' # light gray
                z = 0
            xs = [col * 100, col * 100]
            ys = [0, rows * 100]
            line = mlines.Line2D(xs, ys, color = c, zorder = z)
            ax.add_line(line)
    
        # Put numbers in cells
        all_values = set()
        for addr, cell in self.cells.items():
            row, col = addr
            val = cell.value
            all_values.add(val)
            
            fw = 'bold' if addr in self.givens else 'normal'
            ax.text(100 * (col + 1) - 50, 100 * rows - 100 * (row + 1) + 50, 
                    val, size = 18, 
                    horizontalalignment = 'center',
                    verticalalignment = 'center',
                    fontweight = fw,
                    zorder = 10)
            
        if self.is_complete() is True:
            ncolors = len(all_values)
            step = 2
            while gcd(step, ncolors) > 1:
                step += 1
            floor = 0.5
            colors = Board._get_color_list(ncolors, step, floor, start=0)
            cdict = {v: c for v, c in zip(sorted(all_values), colors)}

            # Color cells
            for addr, cell in self.cells.items():
                row, col = addr
                val = cell.value
                color = cdict[val]
                rect = patches.Rectangle((100 * col, 100 * rows - 100 * (row + 1)), 
                                         100, 100, 
                                         facecolor=color, 
                                         edgecolor='none',
                                         zorder = -5)
                ax.add_patch(rect)
                
            for row in range(rows):
                for col in range(cols - 1):
                    left = self.cells[(row, col)]
                    right = self.cells[(row, col + 1)]
                    if left.value != right.value:
                        xs = [100 * (col + 1), 100 * (col + 1)]
                        ys = [100 * (rows - row) , 100 * (rows - row - 1)]
                        line = mlines.Line2D(xs, ys, color='#000000', zorder=5)
                        ax.add_line(line)             
            for col in range(cols):
                for row in range(rows - 1):
                    top = self.cells[(row, col)]
                    bottom = self.cells[(row + 1, col)]
                    if top.value != bottom.value:
                        xs = [100 * col, 100 * (col + 1)]
                        ys = [100 * (rows - row - 1), 100 * (rows - row - 1)]
                        line = mlines.Line2D(xs, ys, color='#000000', zorder=5)
                        ax.add_line(line)    

        return fig
        
class Fillomino:
    
    def __init__(self, dims, givens):
        
        self.board = Board(dims, givens)
        self.solutions = []
        
    def solve(self, max_solutions=2):
        new = self.board.copy()
        new.find_connected_components()
        res = new.check_connected_components()
        if res is False:
            return False
        res = new.check_for_orphans()
        if res is False:
            return False
        stack = [new]
        while len(stack) > 0:
            current = stack.pop()
            if len(current.components) > 0:
                children = current.children_comp()
            else: 
                children = current.children_cell()
            for child in children:
                if child.is_complete():
                    self.solutions.append(child)
                    if len(self.solutions) >= max_solutions:
                        break
                else:
                    stack.append(child)

        return len(self.solutions) > 0
    
    
dims = (20, 20)
givens = {(0, 1): 1,
 (0, 2): 6,
 (0, 3): 1,
 (0, 4): 6,
 (0, 6): 1,
 (0, 8): 1,
 (0, 12): 1,
 (0, 13): 8,
 (0, 17): 6,
 (0, 19): 3,
 (1, 4): 1,
 (1, 8): 3,
 (1, 10): 5,
 (1, 12): 3,
 (1, 16): 1,
 (1, 18): 3,
 (2, 0): 1,
 (2, 1): 6,
 (2, 5): 3,
 (2, 8): 1,
 (2, 10): 4,
 (2, 11): 3,
 (2, 12): 1,
 (2, 14): 1,
 (2, 16): 4,
 (2, 19): 2,
 (3, 4): 3,
 (3, 5): 1,
 (3, 7): 1,
 (3, 10): 1,
 (3, 13): 1,
 (3, 14): 4,
 (3, 16): 1,
 (3, 18): 1,
 (3, 19): 2,
 (4, 1): 6,
 (4, 2): 8,
 (4, 3): 1,
 (4, 6): 5,
 (4, 11): 6,
 (4, 12): 7,
 (4, 14): 1,
 (5, 1): 1,
 (5, 5): 1,
 (5, 8): 1,
 (5, 10): 6,
 (5, 12): 1,
 (5, 16): 9,
 (6, 1): 6,
 (6, 3): 7,
 (6, 4): 1,
 (6, 7): 8,
 (6, 13): 1,
 (6, 14): 6,
 (6, 17): 5,
 (6, 18): 5,
 (6, 19): 5,
 (7, 3): 5,
 (7, 7): 1,
 (7, 8): 3,
 (7, 9): 1,
 (7, 10): 8,
 (7, 14): 6,
 (7, 15): 6,
 (7, 16): 1,
 (7, 18): 5,
 (7, 19): 1,
 (8, 0): 1,
 (8, 3): 1,
 (8, 6): 1,
 (8, 8): 1,
 (8, 10): 6,
 (8, 11): 1,
 (8, 13): 1,
 (8, 17): 1,
 (9, 2): 1,
 (9, 5): 1,
 (9, 6): 5,
 (9, 13): 3,
 (9, 19): 7,
 (10, 2): 6,
 (10, 4): 4,
 (10, 5): 6,
 (10, 7): 5,
 (10, 8): 1,
 (10, 9): 5,
 (10, 13): 3,
 (10, 14): 3,
 (10, 15): 1,
 (10, 16): 8,
 (10, 17): 1,
 (11, 1): 1,
 (11, 3): 1,
 (11, 8): 4,
 (11, 10): 1,
 (11, 11): 5,
 (11, 12): 1,
 (11, 19): 1,
 (12, 0): 1,
 (12, 1): 3,
 (12, 4): 1,
 (12, 5): 5,
 (12, 6): 5,
 (12, 10): 3,
 (12, 11): 1,
 (12, 13): 4,
 (12, 18): 1,
 (13, 0): 5,
 (13, 2): 1,
 (13, 8): 1,
 (13, 10): 1,
 (13, 14): 6,
 (13, 15): 9,
 (13, 16): 1,
 (14, 1): 1,
 (14, 2): 6,
 (14, 3): 6,
 (14, 4): 6,
 (14, 6): 3,
 (14, 7): 1,
 (14, 9): 1,
 (14, 10): 6,
 (14, 14): 1,
 (14, 15): 4,
 (14, 16): 4,
 (14, 17): 7,
 (14, 19): 2,
 (15, 5): 3,
 (15, 6): 1,
 (15, 8): 6,
 (15, 9): 6,
 (15, 12): 1,
 (15, 17): 4,
 (15, 18): 1,
 (16, 0): 1,
 (16, 2): 1,
 (16, 3): 8,
 (16, 8): 6,
 (16, 9): 6,
 (16, 11): 1,
 (16, 13): 1,
 (16, 17): 5,
 (17, 2): 9,
 (17, 3): 1,
 (17, 5): 1,
 (17, 9): 9,
 (17, 11): 2,
 (17, 14): 1,
 (17, 15): 9,
 (17, 18): 5,
 (18, 4): 5,
 (18, 5): 5,
 (18, 9): 7,
 (18, 14): 2,
 (18, 17): 1,
 (19, 2): 1,
 (19, 4): 5,
 (19, 8): 1,
 (19, 9): 3,
 (19, 11): 1,
 (19, 12): 6,
 (19, 13): 1,
 (19, 15): 1,
 (19, 17): 4,
 (19, 18): 3,
 (19, 19): 1}

F = Fillomino(dims, givens)
new = F.board.copy()
new.find_connected_components()
res1 = new.check_connected_components()
res2 = new.check_for_orphans()
solutions = []
stack = [new]


count = 0
while len(stack) > 0:
    current = stack.pop()
    if len(current.components) > 0:
        children = current.children_comp()
    else: 
        children = current.children_cell()
    for child in children:
        if child.is_complete():
            solutions.append(child)

        else:
            child.count_in = count
            stack.append(child)
    
    
    # step = 1000
    # count += 1
    # if count%step == 0:
    #     print(count, len(stack), len(solutions))
    # # print(count, len(stack), len(solutions))
    # if count == step*100:
    #     break


    count += 1

    print(count, len(stack), len(solutions))
    if count == 23:
        break
    
print(len(solutions))
