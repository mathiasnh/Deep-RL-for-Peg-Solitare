from hexmap import DiamondHexMap, TriangleHexMap
from pegsol import PegSolitaire
from rl import Environment, RLearner, Actor, TableCritic, NeuralNetCritic
from random import randrange
from tqdm import tqdm
from time import sleep
import numpy as np
import matplotlib.pyplot as plt
import torch 

class PegSolEnvironment(Environment):
    def __init__(self, world):
        self.world = world

    def produce_initial_state(self):
        self.world.produce_initial_state()

    def generate_possible_child_states(self):
        return self.world.generate_possible_states()

    def is_terminal_state(self):
        return self.world.is_terminal_state()

    def is_win_state(self):
        return self.world.is_win_state()

    def perform_action(self, action):
        self.world.set_state(action)

    def reset_environment(self):
        self.world.reset_state()

    def get_current_state(self):
        return tuple(x.pegged for x in self.world.board.cells)

    def pegs_left(self):
        return sum(s.pegged == True for s in self.world.board.cells)


"""Helper function"""
def get_state_and_action(learner, epsilon, nn_critic):
    state = learner.critic.environment.get_current_state()
    action = learner.decide_action_to_take(state, EPSILON)
    learner.actor.policy[tuple([state, action])]
    # Since eligibility trace works differently with nn
    if not nn_critic:
        learner.critic.e_trace[state]

    return state, action

if __name__ == "__main__":
    SIZE                            = 5
    DIAMOND_SHAPE                   = False # if False: Triangle
    NN_CRITIC                       = True  # if False: TableCritic
    EPISODES                        = 700
    EPSILON                         = 0.9
    EPSILON_DECAY                   = -1/EPISODES
    EPSILON_DECAY_RATE              = 0.99
    CRITIC_DISCOUNT_FACTOR          = 0.9225
    ACTOR_DISCOUNT_FACTOR           = 0.7583
    CRITIC_LEARNING_RATE            = 0.4798 # smaller for neural net (?)
    ACTOR_LEARNING_RATE             = 0.0815
    CRITIC_ELIGIBILITY_DECAY_RATE   = 0.018
    ACTOR_ELIGIBILITY_DECAY_RATE    = 0.7017
    """
    CRITIC_DISCOUNT_FACTOR          = 0.9
    ACTOR_DISCOUNT_FACTOR           = 0.9
    CRITIC_LEARNING_RATE            = 0.001 # smaller for neural net (?)
    ACTOR_LEARNING_RATE             = 0.1
    CRITIC_ELIGIBILITY_DECAY_RATE   = 0.9
    ACTOR_ELIGIBILITY_DECAY_RATE    = 0.9
    """
    STEP_REWARD                     = 0
    WIN_REWARD                      = 100
    LOSE_REWARD                     = -50
    NN_LAYERS                       = [10, 1]
    
    NN_INPUT_SIZE = SIZE**2 if DIAMOND_SHAPE else sum(x for x in range(SIZE+1))


    #map = DiamondHexMap(SIZE, False, 1, [2, 6, 10, 13, 16, 22, 24])
    
    if DIAMOND_SHAPE:
        map = DiamondHexMap(SIZE, False, 1, [6])
    else:
        map = TriangleHexMap(SIZE, False, 1, [5])

    world = PegSolitaire(map)
    environment = PegSolEnvironment(world)
    actor = Actor(ACTOR_LEARNING_RATE, 
                ACTOR_DISCOUNT_FACTOR, 
                ACTOR_ELIGIBILITY_DECAY_RATE)
    if NN_CRITIC:
        critic = NeuralNetCritic(environment, 
                                CRITIC_LEARNING_RATE, 
                                CRITIC_DISCOUNT_FACTOR, 
                                CRITIC_ELIGIBILITY_DECAY_RATE, 
                                NN_LAYERS, 
                                NN_INPUT_SIZE)
    else:
        critic = TableCritic(environment, 
                                CRITIC_LEARNING_RATE, 
                                CRITIC_DISCOUNT_FACTOR, 
                                CRITIC_ELIGIBILITY_DECAY_RATE)
    learner = RLearner(actor, critic)

    epsilons = []
    peg_result = []
    for j in tqdm(range(EPISODES)):
        epsilons.append(EPSILON)
        game = True
        current_episode = [] 

        # see SuttonBarto - page 232 - fig 9 algorithm (e = 0), for NN
        learner.critic.reset_e_trace()

        """Initialize s and a"""
        state, action = get_state_and_action(learner, EPSILON, NN_CRITIC)
        prevstate = state
        reward = 0

        while game:
            #input("Press enter to continue...")
            #sleep(0.5)
            if not learner.critic.environment.is_terminal_state():
                current_episode.append(tuple([state, action]))

                """ Do action a --> now in state s' """
                learner.critic.environment.perform_action(action)

                state, action = get_state_and_action(learner, EPSILON, NN_CRITIC)

                """ Reward  """
                if learner.critic.environment.is_terminal_state():
                    reward = WIN_REWARD if learner.critic.environment.is_win_state() else LOSE_REWARD#*learner.critic.environment.pegs_left()
                    #print(reward)
                else:
                    reward = STEP_REWARD

                learner.actor.set_eligibility(tuple([state, action]), 1)

                learner.critic.set_TD_error(reward, state, prevstate)
                learner.critic.set_eligibility(prevstate, 1)

                """ ∀(s,a) ∈ current episode """
                for sap in current_episode:
                    s = sap[0]
                    a = sap[1]

                    learner.critic.set_value(s)

                    # Only for TableCritic
                    learner.critic.set_eligibility(s)

                    learner.actor.set_policy(sap, learner.critic.TD_error)
                    learner.actor.set_eligibility(sap)

                prevstate = state
                
            else:
                game = False
                peg_result.append(sum(s.pegged == True for s in learner.critic.environment.world.board.cells))

        #EPSILON = max(EPSILON + EPSILON_DECAY, 0) 
        EPSILON = EPSILON*EPSILON_DECAY_RATE
                
        learner.critic.environment.reset_environment()
    
    plt.plot(peg_result, label="Pegs left")
    plt.plot(epsilons, label="Epsilon")
    #plt.ylabel("Pegs left")
    plt.xlabel("Episodes")
    plt.legend()
    plt.show()
    """
    plt.draw()
    plt.pause(0.2)
    plt.clf()
    """


    