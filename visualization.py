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
        """
            Creates a graph using Networkx, adds nodes from a HexMap 
            and edges between neighboring nodes
        """
        g = nx.Graph()
        for cell in self.cells:
            g.add_node((cell.pos[0], cell.pos[1]), pos=self.pos_in_graph(cell.pos))
        g.add_edges_from([((cell.pos[0], cell.pos[1]), (neighbor.pos[0], neighbor.pos[1])) for cell in self.cells for neighbor in cell.neighbors])
        return g

    def pos_in_graph(self, pos):
        """
            Calculates the positions of a node in the graph based on its position
            on the board. Dependent on map type (Diamond or Triangle).
        """
        r, c = pos
        if self.is_diamond_map:
            return (c - r) / 2, -(c + r) * sqrt(3) / 2
        else:
            return c - r / 2, -r * sqrt(3) / 2 

    def get_node_colors(self, state, action):
        """
            Returns a list of colors to be matched with their respective nodes in 
            a graph. Green is node is to jump, red if node is to be jumped over, 
            black if node is pegged, and white if node is empty.
        """
        if action is not None:
            colors = []
            for cell in state:
                if cell.pos == action[0]: colors.append('green')
                elif cell.pos == action[1]: colors.append('red')
                elif cell.pegged: colors.append('black')
                else: colors.append('white')
            return colors
        else:
            return ['black' if c.pegged else 'white' for c in state]

    def draw(self, state, action, delay):
        """
            Draw a given state with the current board-graph. The action parameter 
            contains references to the jumper and jumped (green and red respectively).
        """
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
