import random

class HexMap:
    def __init__(self, 
                type,
                offsets, 
                size,
                tot_cell_count,
                rand_start, 
                rand_start_num, 
                fixed_open_cells):
        self.cells = None
        self.type = type
        self.offsets = offsets
        self.size = size
        self.tot_cell_count = tot_cell_count
        self.rand_start = rand_start
        self.rand_start_num = rand_start_num
        self.fixed_open_cells = fixed_open_cells
    
    def create_neighborhood(self):
        for cell in self.cells:
            r, c = cell.location[0], cell.location[1]
            neighbors = []

            for (a,b) in self.offsets:
                if r+a >= 0 and c+b >= 0:
                    n = next((x for x in self.cells if x.location == (r+a, c+b)), None)
                    if n != None:
                        neighbors.append(n)

            cell.add_neighbors(neighbors)
    
    def init_map(self):
        self.cells = []
        count = 0
        start_open = self.fixed_open_cells
        if self.rand_start:
            start_open = random.sample(range(self.tot_cell_count), self.rand_start_num)
        for i in range(self.size):
            for j in range(self.size if self.type == "diamond" else i+1):
                free = False if count in start_open else True
                self.cells.append(Cell((i, j), free))
                count += 1
        self.create_neighborhood()
        

class DiamondHexMap(HexMap):
    def __init__(self, 
                size, 
                rand_start, 
                rand_start_num, 
                fixed_open_cells=[]):
        super().__init__("diamond",
                        [(-1,0), (-1,1), (0,-1), (0,1), (1,-1), (1,0)],
                        size,
                        size**2,
                        rand_start,
                        rand_start_num,
                        fixed_open_cells)

class TriangleHexMap(HexMap):
    def __init__(self,
                size,
                rand_start, 
                rand_start_num, 
                fixed_open_cells=[]):
        super().__init__("triangle", 
                        [(-1,-1), (-1,0), (0,-1), (0,1), (1,0), (1,1)],
                        size,
                        sum(x for x in range(size+1)),
                        rand_start,
                        rand_start_num,
                        fixed_open_cells)

class Cell:
    def __init__(self, location, pegged, neighbors=[]):
        self.location = location
        self.pegged = pegged
        self.neighbors = neighbors
    
    def add_neighbors(self, neighbors):
        self.neighbors = neighbors
    
    def set_peg(self, b):
        self.pegged = b