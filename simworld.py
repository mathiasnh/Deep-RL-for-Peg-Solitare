from pegsolitare import initBoard, generatePossibleStates, isFinalState, printBoard
# Supply initial state
def getInitialState():
    return initBoard()

# Supply child states for any parent state
def getAllChildStates(state):
    return generatePossibleStates(state)

# Does current state represent a final state?

