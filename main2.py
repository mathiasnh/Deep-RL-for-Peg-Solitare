from hexmap import DiamondHexMap, TriangleHexMap
from pegsol import PegSolitaire
from rl import Environment, RLearner, Actor, TableCritic
from random import randrange
from tqdm import tqdm
from time import sleep
import numpy as np
import matplotlib.pyplot as plt
import json
import os

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
    """
    SIZE = 5
    FIXED_START = [2, 6, 10, 13, 16, 22, 24]
    RAND_START = False
    RAND_START_NUM = 1
    EPISODES = 1000
    EPSILON = 0.9
    EPSILON_DECAY = -1/EPISODES
    EPSILON_DECAY_RATE = 0.995
    CRITIC_DISCOUNT_FACTOR = 0.5
    ACTOR_DISCOUNT_FACTOR = 0.5
    CRITIC_LEARNING_RATE = 0.4
    ACTOR_LEARNING_RATE = 0.4
    CRITIC_ELIGIBILITY_DECAY_RATE = 0.1
    ACTOR_ELIGIBILITY_DECAY_RATE = 0.1
    STEP_REWARD = 0
    WIN_REWARD = 100
    LOSE_REWARD = -50
    """
    
    SIZE = 5
    FIXED_START = [2, 6, 10, 13, 16, 22, 24]
    RAND_START = False
    RAND_START_NUM = 1
    
    map = DiamondHexMap(SIZE, RAND_START, RAND_START_NUM, FIXED_START)
    world = PegSolitaire(map)
    environment = PegSolEnvironment(world)
    
    for i in range(100):
        EPISODES = 1000
        EPSILON = 0.9
        EPSILON_DECAY = -1/EPISODES
        EPSILON_DECAY_RATE = 0.995
        CRITIC_DISCOUNT_FACTOR = randrange(10000)/10000
        ACTOR_DISCOUNT_FACTOR = randrange(10000)/10000
        CRITIC_LEARNING_RATE = randrange(10000)/10000
        ACTOR_LEARNING_RATE = randrange(10000)/10000
        CRITIC_ELIGIBILITY_DECAY_RATE = randrange(10000)/10000
        ACTOR_ELIGIBILITY_DECAY_RATE = randrange(10000)/10000
        STEP_REWARD = 0
        WIN_REWARD = 100
        LOSE_REWARD = -50

        success_count = 0
        
        for j in tqdm(range(10)):
            actor = Actor()
            critic = TableCritic(environment, CRITIC_DISCOUNT_FACTOR)
            learner = RLearner(actor, critic)
            #learner.critic.set_environment(environment)

            epsilons = []
            peg_result = []
            win_count = 0
            

            for k in range(EPISODES):
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

                        """ Get s' and a' """
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
                            reward = WIN_REWARD if learner.critic.environment.is_win_state() else LOSE_REWARD*learner.critic.environment.pegs_left()
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

                #EPSILON = EPSILON*EPSILON_DECAY_RATE
                EPSILON = max(EPSILON + EPSILON_DECAY, 0) 
                        
                learner.critic.environment.reset_environment()
            
            for k in range(1, 11):
                if peg_result[-i] == 1:
                    win_count += 1

            if win_count > 9:
                save_path = r'C:\Users\Mathias Henriksen\git\Deep-RL-for-Peg-Solitare\wins\try' + str(i)
                os.makedirs(save_path)
                f = open("wins/try" + str(i) + "/params" + str(j) + ".txt", "w+")
                f.write("CRITIC_DISCOUNT_FACTOR = " + str(CRITIC_DISCOUNT_FACTOR) + "\n")
                f.write("ACTOR_DISCOUNT_FACTOR = " + str(ACTOR_DISCOUNT_FACTOR) + "\n")
                f.write("CRITIC_LEARNING_RATE = " + str(CRITIC_LEARNING_RATE) + "\n")
                f.write("ACTOR_LEARNING_RATE = " + str(ACTOR_LEARNING_RATE) + "\n")
                f.write("CRITIC_ELIGIBILITY_DECAY_RATE = " + str(CRITIC_ELIGIBILITY_DECAY_RATE) + "\n")
                f.write("ACTOR_ELIGIBILITY_DECAY_RATE = " + str(ACTOR_ELIGIBILITY_DECAY_RATE) + "\n")
                f.close()
                plt.plot(peg_result, label="Pegs left")
                plt.plot(epsilons, label="Epsilon")
                #plt.ylabel("Pegs left")
                plt.xlabel("Episodes")
                plt.legend()
                plt.savefig("wins/try" + str(i) + "/plot" + str(j) + ".png")
                #plt.show()
                """
                plt.draw()
                plt.pause(0.2)
                """
                plt.clf()


    