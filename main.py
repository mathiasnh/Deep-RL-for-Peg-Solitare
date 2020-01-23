import hexmap
import pegsol
from rl import Environment

class PegSolEnvironment(Environment):
    def produceInitialState():
        pass

    def generatePossibleChildStates():
        pass

    def isTerminalState():
        pass

    def performAction():
        pass



if __name__ == "__main__":
    a = PegSolEnvironment()
    """
    map = hexmap.DiamondHexMap(4, True, 3)
    environment = pegsol.PegSolitaire(map)

    environment.produceInitialState()
    children = environment.generatePossibleStates()

    rl.environment

    for c in children:
        print(c)
    """
