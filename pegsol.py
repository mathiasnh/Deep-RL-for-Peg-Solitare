from hexmap import TriangleHexMap, DiamondHexMap
from random import randrange

class PegSolitaire:
    """
        The Simulated world (SimWorld) for the game Peg Solitaire
    """
    def __init__(self, board):
        self.board = board
        self.inital_state = None

        self.produce_initial_state()

    def produce_initial_state(self):
        """
            Initalizes map and produces an initial state 
            that is used if environment needs to be reset
        """
        self.board.init_map()
        self.inital_state = [(x.pos, x.pegged) for x in self.board.cells]


    def generate_possible_states(self):
        """
            Traverses the current board state and finds all possible/legal
            actions based on the game rules. An action represents the 
            state it leads to.
        """
        child_states = []
        state = self.board.cells

        for cell in state:
            pos = cell.pos
            if cell.pegged == True:
                for cn in cell.neighbors:
                    if cn.pegged == True:
                        delta = tuple(map(lambda x, y: y - x, pos, cn.pos))
                        nn_pos = tuple(map(lambda x, y: x + y, cn.pos, delta)) #Pos of neighbor's neighbors we may jump to (if empty)
                        nn = next((x for x in state if x.pos == nn_pos), None) #Neighbors's neighbor node
                        if nn != None and nn.pegged == False:
                            child_states.append(tuple([cell.pos, cn.pos, nn.pos]))

        return child_states

    def reset_state(self):
        """
            Resets the board to its initial state
        """
        for i, c in enumerate(self.board.cells):
            c.set_peg(self.inital_state[i][1])

    def set_state(self, action):
        """
            Pushes board into the next state depending
            on some action. A legal action involves two nodes
            becoming empty while one becomes pegged.
        """
        action_cells = [c for c in self.board.cells if c.pos in action]
        for a in action_cells:
            a.set_peg(not a.pegged)

    def is_terminal_state(self):
        """
            The board is in a terminal state if there are no
            possible legal moves to be taken.
        """
        actions = self.generate_possible_states()
        return len(actions) == 0

    def is_win_state(self):
        """
            The board is in a winning state if there is only one
            peg left on the board. 
        """
        count = sum(s.pegged == True for s in self.board.cells)

        if count == 1:
            return True

        return False 
