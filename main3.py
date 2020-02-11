from hexmap import DiamondHexMap, TriangleHexMap
from pegsol import PegSolitaire
from rl import Environment, RLearner, Actor, TableCritic
from random import randrange
from tqdm import tqdm
from time import sleep
import numpy as np
import matplotlib.pyplot as plt

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
def get_state_and_action(learner, epsilon):
    state = learner.critic.environment.get_current_state()
    action, choice_string = learner.decide_action_to_take(state, EPSILON)
    learner.actor.policy[tuple([state, action])]
    learner.critic.eTrace[state]

    return state, action, choice_string

if __name__ == "__main__":
    SIZE = 5
    EPISODES = 1000
    EPSILON = 0.9
    EPSILON_DECAY = -1/EPISODES
    EPSILON_DECAY_RATE = 0.99
    CRITIC_DISCOUNT_FACTOR = 0.9225
    ACTOR_DISCOUNT_FACTOR = 0.0583
    CRITIC_LEARNING_RATE = 0.4798
    ACTOR_LEARNING_RATE = 0.7815
    CRITIC_ELIGIBILITY_DECAY_RATE = 0.018
    ACTOR_ELIGIBILITY_DECAY_RATE = 0.7017
    STEP_REWARD = 0
    WIN_REWARD = 100
    LOSE_REWARD = -50

    map = DiamondHexMap(SIZE, False, 1, [2, 6, 10, 13, 16, 22, 24])
    #map = DiamondHexMap(SIZE, False, 1, [12])
    #map = TriangleHexMap(SIZE, False, 1, [2])
    world = PegSolitaire(map)
    environment = PegSolEnvironment(world)
    actor = Actor()
    critic = TableCritic(environment, CRITIC_DISCOUNT_FACTOR)
    learner = RLearner(actor, critic)

    epsilons = []
    peg_result = []
    for j in tqdm(range(EPISODES)):
        epsilons.append(EPSILON)
        game = True
        current_episode = [] 

        """Initialize s and a"""
        state, action, _ = get_state_and_action(learner, EPSILON)
        prevstate = state
        reward = 0

        while game:
            #input("Press enter to continue...")
            #sleep(0.5)
            if not learner.critic.environment.is_terminal_state():
                current_episode.append(tuple([state, action]))

                """ Do action a --> now in state s' """
                learner.critic.environment.perform_action(action)

                state, action, choice_string = get_state_and_action(learner, EPSILON)
            
                """
                if action is not None:
                    print("Next state is: ")
                    world.print_board()
                    print("Next action (chosen " + choice_string + ") is: " + str(action))
                else:
                    print("Game over!")
                    world.print_board()
                """

                """ Reward  """
                if learner.critic.environment.is_terminal_state():
                    reward = WIN_REWARD if learner.critic.environment.is_win_state() else LOSE_REWARD#*learner.critic.environment.pegs_left()
                    #print(reward)
                else:
                    reward = STEP_REWARD

                learner.actor.set_eligibility(tuple([state, action]), 1)

                learner.critic.set_TD_error(reward, state, prevstate, CRITIC_DISCOUNT_FACTOR)
                learner.critic.set_eligibility(prevstate, 1)

                """ ∀(s,a) ∈ current episode """
                for sap in current_episode:
                    s = sap[0]
                    a = sap[1]

                    learner.critic.set_value(s, learner.critic.values[s] + CRITIC_LEARNING_RATE*learner.critic.TD_error*learner.critic.eTrace[s])
                    learner.critic.set_eligibility(s, CRITIC_LEARNING_RATE*CRITIC_ELIGIBILITY_DECAY_RATE*learner.critic.eTrace[s])

                    learner.actor.set_policy(sap, learner.actor.policy[sap] + ACTOR_LEARNING_RATE*learner.critic.TD_error*learner.actor.eTrace[sap])
                    learner.actor.set_eligibility(sap, ACTOR_LEARNING_RATE*ACTOR_ELIGIBILITY_DECAY_RATE*learner.actor.eTrace[sap])

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


    