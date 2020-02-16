import networkx as nx
import matplotlib.pyplot as plt
from math import sqrt
from hexmap import DiamondHexMap, TriangleHexMap
from pegsol import PegSolitaire

class HexMapVisualizer:
    def __init__(self, cells, is_diamond_map):
        self.cells = cells
        self.is_diamond_map = is_diamond_map
        self.board = self.create_graph()
        
    def create_graph(self):
        g = nx.Graph()
        for cell in self.cells:
            g.add_node((cell.pos[0], cell.pos[1]), pos=self.pos_in_graph(cell.pos))
        g.add_edges_from([((cell.pos[0], cell.pos[1]), (neighbor.pos[0], neighbor.pos[1])) for cell in self.cells for neighbor in cell.neighbors])
        return g

    def pos_in_graph(self, pos):
        r, c = pos
        if self.is_diamond_map:
            return (c - r) / 2, -(c + r) * sqrt(3) / 2
        else:
            return c - r / 2, -r * sqrt(3) / 2 

    def get_node_colors(self, state, action):
        if action is not None:
            colors = []
            for cell in state:
                if cell.pos == action[0]: colors.append('yellow')
                elif cell.pos == action[1]: colors.append('red')
                elif cell.pegged: colors.append('black')
                else: colors.append('white')
            return colors
        else:
            return ['black' if c.pegged else 'white' for c in state]


    def draw(self, state, action, delay):
        plt.pause(delay)
        plt.clf()
        nx.draw(
            self.board,
            nx.get_node_attributes(self.board, 'pos'),
            node_color=self.get_node_colors(state, action),
            edgecolors='black'
        )
        plt.axis('equal')
        plt.draw()


        


if __name__ == "__main__":
    map = DiamondHexMap(4, False, 1, [15])
    env = PegSolitaire(map)
    env.produce_initial_state()
    print([(c.pegged, c.pos) for c in env.board.cells])
    drawer = HexMapVisualizer(env.board.cells, True)
    drawer.draw(tuple(x.pegged for x in env.board.cells))
    plt.show()