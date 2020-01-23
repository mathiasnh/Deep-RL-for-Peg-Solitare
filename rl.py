from collections import defaultdict
import random
from abc import ABC, abstractmethod

class RLearner:
    def __init__(self, 
                actor, 
                critic,
                environment):
        self.actor = actor
        self.critic = critic
        self.environment = environment
        self.state = None
        self.action = None
    
    def initializeSandA(self):
        """get from getInitialState instead"""
        state, action = self.produceInitialState
        self.state = state
        self.action = action

    def run(self, episodes):
        for i in episodes:
            pass

class Actor:
    def __init__(self):
        self.policy = defaultdict(lambda: 0)
        self.e = defaultdict(lambda: 0)

    def setPolicy(self, sap):
        self.policy[sap] = None

class Critic:
    def __init__(self):
        pass

class TableCritic(Critic):
    def __init__(self):
        super().__init__()
        self.values = defaultdict(lambda: random.randrange(100)/100)
        self.eTrace = defaultdict(lambda: 0)
    
    def setValue(self, state):
        self.values[state] = self.values[state]

class NeuralCritic(Critic):
    def __init__(self):
        super().__init__()

class Environment(ABC):
    @abstractmethod
    def produceInitialState():
        pass

    @abstractmethod
    def generatePossibleChildStates():
        pass

    @abstractmethod
    def isTerminalState():
        pass

    @abstractmethod
    def performAction():
        pass



#TDError = reinforcement + discountFactor*value(newState) - value(state)
#value(state) = value(state) + learningRate * tdError


