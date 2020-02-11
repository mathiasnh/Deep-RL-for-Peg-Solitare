import numpy as np 
from collections import defaultdict
from random import randrange
from abc import ABC, abstractmethod
from keras.models import Sequential, Model
from keras.layers import Dense, Dropout, Input
from keras.layers.merge import Add, Multiply
from keras.optimizers import Adam
import keras.backend as K
import tensorflow as tf

from splitgd import fit

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
        if randrange(10000)/10000 < epsilon:
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
    def __init__(self, values, eTrace, environment, discount_factor):
        self.values = values
        self.eTrace = eTrace
        self.discount_factor = discount_factor
        self.TD_error = None
        self.environment = environment

    def set_value(self, state, value):
        self.values[state] = value

    def set_eligibility(self, state, e):
        self.eTrace[state] = e

    def set_TD_error(self, r, state, prevstate, df):
        self.TD_error = r + df * self.values[state] - self.values[prevstate]

class TableCritic(Critic):
    def __init__(self, environment, discount_factor):
        super().__init__(defaultdict(lambda: randrange(100)/100),
                        defaultdict(lambda: 0),
                        environment,
                        discount_factor)

class NeuralNetCritic(Critic):
    def __init__(self):
        super().__init__()
        _, self.model = self.init_NN_critic()

    def init_NN_critic(self):
        sess = tf.compat.v1.Session()
        K.set_session(sess)

        state_input = Input(shape=(16,0))
        h1 = Dense(24, activation='relu')(state_input)
        h2 = Dense(48, activation='relu')(h1)
        h3 = Dense(24, activation='relu')(h2)
        output = Dense(1, activation='relu')(h3)
        
        model = Sequential(input=state_input, output=output)
        adam  = Adam(lr=0.001)
        model.compile(loss="mse", optimizer=adam)
        return state_input, model

    "Sende inn self.model.predict for å få brettet (liste) om til tensor"
    "Hente gradienter"
    "Fikse eligibilieties"
    "Calle fit"

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


