import random

class HexMap:
    def __init__(self, 
                type,
                offsets, 
                size,
                totCellCount,
                randStart, 
                randStartNum, 
                fixedOpenCells):
        self.cells = []
        self.type = type
        self.offsets = offsets
        self.size = size
        self.totCellCount = totCellCount
        self.randStart = randStart
        self.randStartNum = randStartNum
        self.fixedOpenCells = fixedOpenCells
    
    def createNeighborhood(self):
        for cell in self.cells:
            r, c = cell.location[0], cell.location[1]
            neighbors = []

            for (a,b) in self.offsets:
                if r+a >= 0 and c+b >= 0:
                    n = next((x for x in self.cells if x.location == (r+a, c+b)), None)
                    if n != None:
                        neighbors.append(n)

            cell.addNeighbors(neighbors)
    
    def initMap(self):
        count = 0
        startOpen = self.fixedOpenCells
        if self.randStart:
            startOpen = random.sample(range(self.totCellCount), self.randStartNum)
        for i in range(self.size):
            for j in range(self.size if self.type == "diamond" else i+1):
                free = False if count in startOpen else True
                self.cells.append(Cell((i, j), free))
                count += 1
        self.createNeighborhood()
        

class DiamondHexMap(HexMap):
    def __init__(self, 
                size, 
                randStart, 
                randStartNum, 
                fixedOpenCells=[]):
        super().__init__("diamond",
                        [(-1,0), (-1,1), (0,-1), (0,1), (1,-1), (1,0)],
                        size,
                        size**2,
                        randStart,
                        randStartNum,
                        fixedOpenCells)

class TriangleHexMap(HexMap):
    def __init__(self,
                size,
                randStart, 
                randStartNum, 
                fixedOpenCells):
        super().__init__("triangle", 
                        [(-1,-1), (-1,0), (0,-1), (0,1), (1,0), (1,1)],
                        size,
                        sum(x for x in range(size+1)),
                        randStart,
                        randStartNum,
                        fixedOpenCells)

class Cell:
    def __init__(self, location, pegged, neighbors=[]):
        self.location = location
        self.pegged = pegged
        self.neighbors = neighbors
    
    def addNeighbors(self, neighbors):
        self.neighbors = neighbors
    
    def setPeg(self, b):
        self.pegged = b