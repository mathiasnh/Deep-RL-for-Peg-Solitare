from hexmap import TriangleHexMap, DiamondHexMap
from random import randrange

BOARD_SIZE = 4
BOARD_TYPE = "diamond" # triangle / diamond
RANDOM_START = True     # open cells will be placed randomly
RAND_OPEN_CELLS = 6     # number of random open cells
OPEN_CELLS = [2]  # only active if not random start 

class PegSolitaire:
    def __init__(self, board):
        self.board = board
        self.inital_state = None

        self.produce_initial_state()

    def print_board(self):
        for i in range(BOARD_SIZE):
            temp = []
            for cell in self.board.cells:
                if cell.location[0] == i:
                    disp = "pegged" if cell.pegged else "empty!"
                    temp.append(disp)
            print(temp)

    def produce_initial_state(self):
        self.board.init_map()
        self.inital_state = [(x.location, x.pegged) for x in self.board.cells]


    def generate_possible_states(self):
        child_states = []
        state = self.board.cells

        for cell in state:
            pos = cell.location
            if cell.pegged == True:
                for cn in cell.neighbors:
                    if cn.pegged == True:
                        delta = tuple(map(lambda x, y: y - x, pos, cn.location))
                        nn_pos = tuple(map(lambda x, y: x + y, cn.location, delta)) #Pos of neighbor's neighbors we may jump to (if empty)
                        nn = next((x for x in state if x.location == nn_pos), None) #Neighbors's neighbor node
                        if nn != None and nn.pegged == False:
                            child_states.append(tuple([cell.location, cn.location, nn.location]))

        return child_states

    def reset_state(self):
        for i, c in enumerate(self.board.cells):
            c.set_peg(self.inital_state[i][1])

    def set_state(self, action):
        action_cells = [c for c in self.board.cells if c.location in action]
        for a in action_cells:
            a.set_peg(not a.pegged)

    def is_terminal_state(self):
        actions = self.generate_possible_states()
        return len(actions) == 0

    def is_win_state(self):
        count = sum(s.pegged == True for s in self.board.cells)

        if count == 1:
            #print("*****EYYYY*****")
            #self.print_board()
            return True

        return False 


if __name__ == "__main__":

    perfect = False
    
    for i in range(1000):
        count = 0
        board = DiamondHexMap(BOARD_SIZE, RANDOM_START, RAND_OPEN_CELLS, OPEN_CELLS)
        world = PegSolitaire(board)
        world.produce_initial_state()
        state = world.board.cells
        if i == 0:
            world.print_board(state)
        game = True
        while game:
            #input("Press enter to continue...")
            #print_board(state)
            child_states = world.generate_possible_states()
            if not world.is_terminal_state():
                index = randrange(len(child_states))
                s = child_states[index]
                world.setState(s) #Apply action
            else:
                perfect = world.is_win_state()
                game = False
        if perfect == True:
            break

    print("Game over")
