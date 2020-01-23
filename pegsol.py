from hexmap import *

BOARD_SIZE = 5
BOARD_TYPE = "diamond" # triangle / diamond
RANDOM_START = True     # open cells will be placed randomly
RAND_OPEN_CELLS = 3     # number of random open cells
OPEN_CELLS = [2]  # only active if not random start 

class PegSolitaire:
    def __init__(self, map):
        self.map = map

    def printBoard(self, state):
        for i in range(BOARD_SIZE):
            temp = []
            for cell in state:
                if cell.location[0] == i:
                    disp = "pegged" if cell.pegged else "empty!"
                    temp.append(disp)
            print(temp)

    def produceInitialState(self):
        self.map.initMap()
        self.printBoard(self.map.cells)
        print(tuple(x.pegged for x in self.map.cells))


    def generatePossibleStates(self, state):
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

    def resetState(self, actions):
        for i in range(3):
            s[i][0].setPeg(not s[i][1])

    def isTerminalState(self, state):
        return len(generatePossibleStates(state)) == 0

    def isWinState(self, state):
        count = sum(s.pegged == True for s in state)

        if count == 1:
            print("*****EYYYY*****")
            printBoard(state)
            return True

        return False 

"""
if __name__ == "__main__":

    perfect = False
    
    for i in range(1000):
        count = 0
        board = TriangleHexMap(BOARD_SIZE, RANDOM_START, RAND_OPEN_CELLS, OPEN_CELLS)
        board.initMap()
        state = board.cells
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
    """