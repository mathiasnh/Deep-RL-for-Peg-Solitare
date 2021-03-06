from hexmap import DiamondHexMap, TriangleHexMap
from pegsol import PegSolitaire
from AI import Environment, RLearner, Actor, TableCritic, NeuralNetCritic
from visualization import HexMapVisualizer
from random import randrange
from tqdm import tqdm
from time import sleep
import numpy as np
import matplotlib.pyplot as plt
import torch 

class PegSolEnvironment(Environment):
    """
        Serves as an extra layer of abstraction between the 
        reinforcement learner and the game. 
    """
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


"""Helper functions"""
def get_state_and_action(learner, epsilon, nn_critic):
    state = learner.critic.environment.get_current_state()
    action = learner.decide_action_to_take(state, EPSILON)
    learner.actor.policy[tuple([state, action])]
    # Since eligibility trace works differently with nn
    if not nn_critic:
        learner.critic.e_trace[state]

    return state, action

def plot_results(peg_result, epsilons):
    """
        Plots results from each episode in the run 
        as well as the epsilon decay.
    """
    plt.plot(peg_result, label="Pegs left")
    plt.plot(epsilons, label="Epsilon")
    plt.ylabel("Pegs left")
    plt.xlabel("Episodes")
    plt.legend()
    plt.savefig("result.png")
    plt.draw()
    plt.pause(0.5)

def play(learner, visualizer, delay=1):
    """
        Play one game with epsilon=0 (on-policy)
    """
    game = True

    states = []

    while game:
        state = learner.critic.environment.world.board.cells # Need state with (pegged, pos) for visualization
        action = learner.decide_action_to_take(learner.critic.environment.get_current_state(), 0) # Epsilon = 0 (on-policy)
        visualizer.draw(state, action, delay)

        """ Do action a --> now in state s' """
        learner.critic.environment.perform_action(action)
        states.append(learner.critic.environment.get_current_state())

        if learner.critic.environment.is_terminal_state():
            visualizer.draw(state, None, delay)
            game = False
            
    learner.critic.environment.reset_environment()
    return states


if __name__ == "__main__":
    SIZE                            = 6
    DIAMOND_SHAPE                   = True # if False: Triangle
    NN_CRITIC                       = True  # if False: TableCritic
    EPISODES                        = 50
    EPSILON                         = 0.99
    EPSILON_DECAY                   = -1/EPISODES #EPSILON = max(EPSILON + EPSILON_DECAY, 0) 
    EPSILON_DECAY_RATE              = 0.99
    CRITIC_DISCOUNT_FACTOR          = 0.92
    ACTOR_DISCOUNT_FACTOR           = 0.76
    CRITIC_LEARNING_RATE            = 0.008
    ACTOR_LEARNING_RATE             = 0.2
    CRITIC_ELIGIBILITY_DECAY_RATE   = 0.1
    ACTOR_ELIGIBILITY_DECAY_RATE    = 0.8
    STEP_REWARD                     = 0
    WIN_REWARD                      = 100
    LOSE_REWARD                     = -50
    NN_LAYERS                       = [10, 1]
    
    # Number of nodes on game board 
    NN_INPUT_SIZE = SIZE**2 if DIAMOND_SHAPE else sum(x for x in range(SIZE+1))
    
    if DIAMOND_SHAPE:
        map = DiamondHexMap(SIZE, True, 1, [5, 6, 7])
    else:
        map = TriangleHexMap(SIZE, False, 1, [1, 4, 8])
    
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

    visualizer = HexMapVisualizer(world.board.cells, DIAMOND_SHAPE)
    
    epsilons = []
    peg_result = []

    """ 
        The generic Actor-Critic algorithm presented in the PDF 
        "Implementing the Actor-Critic Model of Reinforcement Learning"
    """
    for j in tqdm(range(EPISODES)):
        epsilons.append(EPSILON)
        game = True
        current_episode = [] 

        # See Sutton & Barto - page 232 - fig 9 algorithm (e = 0), for NN
        learner.critic.reset_e_trace()

        """Initialize s and a"""
        state, action = get_state_and_action(learner, EPSILON, NN_CRITIC)
        prevstate = state
        reward = 0

        while game:
            if not learner.critic.environment.is_terminal_state():
                current_episode.append(tuple([state, action]))

                """ Do action a --> now in state s' """
                learner.critic.environment.perform_action(action)
            
                state, action = get_state_and_action(learner, EPSILON, NN_CRITIC)

                """ Reward  """
                if learner.critic.environment.is_terminal_state():
                    reward = WIN_REWARD if learner.critic.environment.is_win_state() else LOSE_REWARD
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
                    learner.critic.set_eligibility(s) # Only for TableCritic

                    learner.actor.set_policy(sap, learner.critic.TD_error)
                    learner.actor.set_eligibility(sap)

                prevstate = state
                
            else:
                game = False
                peg_result.append(sum(s.pegged == True for s in learner.critic.environment.world.board.cells))

        EPSILON = EPSILON*EPSILON_DECAY_RATE
                
        learner.critic.environment.reset_environment()

    plot_results(peg_result, epsilons)


    if NN_CRITIC:
        for w in learner.critic.model.parameters():
            print(w)
    
    while True:
        delay = input("Type in a desired delay (in sec) between action, and a game will start: ")
        if delay == "":
            break
        states = play(learner, visualizer, float(delay))
    


    