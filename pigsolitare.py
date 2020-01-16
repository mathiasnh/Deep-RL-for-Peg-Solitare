BOARD_SIZE = 8
BOARD_TYPE = "diamond" #or triangle

class Cell:
    def __init__(self, location, pegged, neighbors=[]):
        self.location = location
        self.pegged = pegged
        self.neighbors = neighbors
    
    def addNeighbors(self, neighbors):
        self.neighbors = neighbors
        return self.neighbors
    
    def setPeg(self, b):
        self.pegged = b
    


def createNeighborhood(currentCell, cells):
    indexes = [(-1,0), (-1,1), (0,-1), (0,1), (1,-1), (1,0)] if BOARD_TYPE == "diamond" else [(-1,-1), (-1,0), (0,-1), (0,1), (1,0), (1,1)]
    r, c = currentCell.location[0], currentCell.location[1]
    neighbors = []
    for (a,b) in indexes:
        if r+a >= 0 and c+b >= 0:
            n = next((x for x in cells if x.location == (r+a, c+b)), None)
            if n != None:
                neighbors.append(n)
    currentCell.addNeighbors(neighbors)

def initBoard():
    cells = []
    count = 0
    for i in range(BOARD_SIZE):
        for j in range(BOARD_SIZE if BOARD_TYPE == "diamond" else i + 1):
            start = False if count == 20 else True
            cells.append(Cell((i, j), start))
            count += 1
            
    for cell in cells:
        createNeighborhood(cell, cells)
    
    return cells

def printBoard(state):
    for i in range(BOARD_SIZE):
        temp = []
        for cell in state:
            if cell.location[0] == i:
                disp = "pegged" if cell.pegged else "empty!"
                temp.append(disp)
        print(temp)

def generatePossibleStates(state):
    #Is any neighbor's neighbor empty? 
    #If so, is it possible to jump to (in a straight line)?
    childStates = []
    for cell in state:
        pos = cell.location
        if cell.pegged == True:
            for cn in cell.neighbors:
                if cn.pegged == True:
                    delta = tuple(map(lambda x, y: y - x, pos, cn.location))
                    nnPos = tuple(map(lambda x, y: x + y, cn.location, delta)) #Pos of neighbor's neighbors we may jump to (if empty)
                    nn = next((x for x in state if x.location == nnPos), None) #Neighbors's neighbor node
                    if nn != None and nn.pegged == False:
                        """
                        cell.setPeg(False) #Hopper
                        cn.setPeg(False)   #Hopped over 
                        nn.setPeg(True)    #Destination
                        """
                        childStates.append([(cell, False), (cn, False), (nn, True)]) #Actions to a possible state
    return childStates

def resetState(actions):
    s[0][0].setPeg(not s[0][1])
    s[1][0].setPeg(not s[1][1])
    s[2][0].setPeg(not s[2][1])

if __name__ == "__main__":
    state = initBoard()
    game = True
    count = 0
    while game:
        input("Press enter to continue...")
        printBoard(state)
        childStates = generatePossibleStates(state)
        print("***********")
        for i, s in enumerate(childStates):
            print("Child #", i + 1)
            s[0][0].setPeg(s[0][1])
            s[1][0].setPeg(s[1][1])
            s[2][0].setPeg(s[2][1])
            printBoard(state)
            resetState(childStates)
                
        #GENRATE ALL STATES







