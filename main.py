from hexmap import DiamondHexMap, TriangleHexMap
from pegsol import PegSolitaire
from rl import Environment, RLearner, Actor, TableCritic
from random import randrange
from tqdm import tqdm
from time import sleep
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


"""Helper function"""
def get_state_and_action(learner, epsilon):
    state = learner.critic.environment.get_current_state()
    action, choice_string = learner.decide_action_to_take(state, EPSILON)
    learner.actor.policy[tuple([state, action])]
    learner.critic.eTrace[state]

    return state, action, choice_string

if __name__ == "__main__":
    SIZE = 4
    EPISODES = 1000
    EPSILON_ = 0.9
    EPSILON_DECAY = -1/EPISODES
    EPSILON_DECAY_RATE = 0.99
    CRITIC_DISCOUNT_FACTOR = 0.5
    ACTOR_DISCOUNT_FACTOR = 0.5
    CRITIC_LEARNING_RATE = 0.001
    ACTOR_LEARNING_RATE = 0.001
    CRITIC_ELIGIBILITY_DECAY_RATE = 0.1
    ACTOR_ELIGIBILITY_DECAY_RATE = 0.1
    STEP_REWARD = 0.0
    WIN_REWARD = 100
    LOSE_REWARD = -10

    actor = Actor()
    critic = TableCritic(CRITIC_DISCOUNT_FACTOR)
    learner = RLearner(actor, critic)

    """ Train for all starting positions """
    for i in range(1):
        peg_result = []
        EPSILON = EPSILON_

        for j in tqdm(range(EPISODES)):
            print(EPSILON)
            map = DiamondHexMap(SIZE, False, 1, [2])
            world = PegSolitaire(map)
            environment = PegSolEnvironment(world)
            learner.critic.set_environment(environment)
            game = True
            current_episode = [] 

            """Initialize s and a"""
            state, action, _ = get_state_and_action(learner, EPSILON)
            prevstate = state
            reward = 0

            while game:
                #input("Press enter to continue...")
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
                        reward = WIN_REWARD if learner.critic.environment.is_win_state() else LOSE_REWARD
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
        #print(EPSILON)
        plt.plot(peg_result)
        plt.ylabel("Pegs left")
        plt.xlabel("Episodes")
        plt.show()
        """
        plt.draw()
        plt.pause(0.2)
        plt.clf()
        """


    