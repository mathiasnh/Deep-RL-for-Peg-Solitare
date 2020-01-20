import random

BOARD_SIZE = 7
BOARD_TYPE = "triangle" # triangle / diamond
RANDOM_START = False     # open cells will be placed randomly
RAND_OPEN_CELLS = 6     # number of random open cells
OPEN_CELLS = [12]  # only active if not random start 

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
    startOpen = OPEN_CELLS
    boardSize = BOARD_SIZE**2 if BOARD_TYPE == "diamond" else sum(x for x in range(BOARD_SIZE+1))

    if RANDOM_START:
        startOpen = random.sample(range(boardSize), RAND_OPEN_CELLS)

    for i in range(BOARD_SIZE):
        for j in range(BOARD_SIZE if BOARD_TYPE == "diamond" else i + 1):
            start = False if count in startOpen else True
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
                        childStates.append([(cell, False), (cn, False), (nn, True)]) #Actions to a possible state

    return childStates

def resetState(actions):
    for i in range(3):
        s[i][0].setPeg(not s[i][1])

def isFinalState(state):
    return len(generatePossibleStates(state)) == 0

def isWinState(state):
    count = sum(s.pegged == True for s in state)

    if count == 1:
        print("*****EYYYY*****")
        printBoard(state)
        return True

    return False 

if __name__ == "__main__":
    state = initBoard()
    perfect = False
    printBoard(state)

    for i in range(100000):
        count = 0
        state = initBoard()
        game = True
        while game:
            #input("Press enter to continue...")
            #printBoard(state)
            childStates = generatePossibleStates(state)
            if not isFinalState(state):
                index = random.randrange(len(childStates))
                s = childStates[index]
                for i in range(3):
                    s[i][0].setPeg(s[i][1]) #Apply actions
            else:
                perfect = isWinState(state)
                game = False
        if perfect == True:
            break

    print("Game over")
        







