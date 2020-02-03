from collections import defaultdict
from random import randrange
from abc import ABC, abstractmethod

class RLearner:
    def __init__(self, 
                actor, 
                critic):
        self.actor = actor
        self.critic = critic
        self.state = None
        self.action = None
        
    def decide_action_to_take(self, state, epsilon):
        """
        Decides whether to do an action based on policy or randomly.
        If the state is unknown, the choice will always be random.
        """
        choice_string = ""
        if randrange(100)/100 < epsilon:
            action = self.get_random_action()
            choice_string = "randomly by epsilon"
        else:
            if state in (x[0] for x in self.actor.policy.keys()):
                action = self.actor.select_action(state)
                choice_string = "not randomly"
            else:
                action = self.get_random_action()
                choice_string = "randomly because no actions for this state yet"
                """
                for sap in self.actor.policy:
                    print(str(sap) + " " + str(self.actor.policy[sap]))
                """

        return action, choice_string

    def get_random_action(self):
        possible_actions = self.critic.environment.generate_possible_child_states()
        action = None

        if len(possible_actions) > 0:
            random_index = randrange(len(possible_actions))
            action = possible_actions[random_index]
        return action


class Actor:
    def __init__(self):
        self.policy = defaultdict(lambda: 0)
        self.eTrace = defaultdict(lambda: 0)

    def set_policy(self, sap, value):
        self.policy[sap] = value

    def set_eligibility(self, sap, e):
        self.eTrace[sap] = e

    def select_action(self, state):
        max = float('-inf')
        action = None
        for s in (x for x in self.policy.keys() if x[0] == state):
            val = self.policy[s]
            if val >= max:
                max = val
                action = s[1]
        return action       



class Critic:
    def __init__(self, values, eTrace, discount_factor):
        self.values = values
        self.eTrace = eTrace
        self.discount_factor = discount_factor
        self.TD_error = None

    def set_value(self, state, value):
        self.values[state] = value

    def set_eligibility(self, state, e):
        self.eTrace[state] = e

    def set_TD_error(self, r, state, prevstate):
        self.TD_error = r + self.discount_factor * self.values[state] - self.values[prevstate] 

    def set_environment(self, environment):
        self.environment = environment

class TableCritic(Critic):
    def __init__(self, discount_factor):
        super().__init__(defaultdict(lambda: randrange(100)/100),
                        defaultdict(lambda: 0),
                        discount_factor)

class NeuralCritic(Critic):
    def __init__(self):
        super().__init__()

class Environment(ABC):
    @abstractmethod
    def produce_initial_state():
        pass

    @abstractmethod
    def generate_possible_child_states():
        pass

    @abstractmethod
    def is_terminal_state():
        pass

    @abstractmethod
    def perform_action():
        pass



#TDError = reinforcement + discountFactor*value(newState) - value(state)
#value(state) = value(state) + learningRate * tdError


