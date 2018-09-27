from random import choice, uniform
from board import hash_board, get_score
from utils import *
import operator
from time import sleep

LEARNING_RATE = 0.2
DISCOUNT = 1
RANDOM_CHOICE_CHANCE = 0
NAIVE_GIVEN_RANDOM = 0.9
END_GAME_REWARD = 50
LOST_GAME_PENALTY = -50


class ComputerPlayer():

    def __init__(self, q_table=None):
        # self.lookup_table = load_lookup_table()
        if q_table:
            self.q_table = q_table
        else:
            self.q_table = load_q_table()
        self.previous_state = self.previous_action = None

    def inform_won(self):
        self.q_table[self.previous_state][self.previous_action] = END_GAME_REWARD

    def inform_lost(self):
        self.q_table[self.previous_state][self.previous_action] = -10

    def choose_turn(self, turns, board):
        if hash_board(board.grid) in self.q_table and uniform(0, 1) > RANDOM_CHOICE_CHANCE:
            sorted_actions = sorted(self.q_table[hash_board(
                board.grid)].items(), key=operator.itemgetter(1))
            return eval(sorted_actions.pop()[0])
        elif uniform(0, 1) < NAIVE_GIVEN_RANDOM:
            s_turns = sorted(turns, key=lambda x: abs(x[0][0] - x[1][0]))
            s_turns = sorted(turns, key=len)
            # print(turns)
            if abs(s_turns[len(s_turns) - 1][0][0] - s_turns[len(s_turns) - 1][1][0]) == 1:
                return choice(s_turns)
            else:
                return s_turns.pop()
        else:
            return choice(turns)

    def play(self, board, silent=False):
        if self.previous_state:
            if hash_board(board.grid) in self.q_table:
                # with open("q_update.txt", "a") as f:
                #     f.write("old_q " + str(self.q_table[self.previous_state][self.previous_action]))
                #     f.write("\nmax " + str(max([self.q_table[hash_board(board.grid)][a]
                #             for a in self.q_table[hash_board(board.grid)]])))
                #     f.write("\ndifference " + str(max([self.q_table[hash_board(board.grid)][a]
                #             for a in self.q_table[hash_board(board.grid)]])
                #                 - self.q_table[self.previous_state][self.previous_action]))

                self.q_table[self.previous_state][self.previous_action] += (LEARNING_RATE * ((get_score(board.grid, board.turn) - get_score(self.previous_grid, board.turn)) - 0.1 +
                                                                                             DISCOUNT * max([self.q_table[hash_board(board.grid)][a]
                                                                                                             for a in self.q_table[hash_board(board.grid)]])
                                                                                             - self.q_table[self.previous_state][self.previous_action]))
                # f.write("\n" + str(self.q_table[self.previous_state][self.previous_action]))
                # f.write("\n\n")
            else:
                self.q_table[self.previous_state][self.previous_action] += (LEARNING_RATE * (get_score(board.grid, board.turn) -
                                                                                             self.q_table[self.previous_state][self.previous_action]))
        # sleep(1)
        if not silent:
            print(board)
        turns = board.get_all_legal_moves(board.grid)
        t = self.choose_turn(turns, board)
        # t = choice(turns)
        self.previous_grid = board.grid
        self.previous_state = hash_board(board.grid)
        self.previous_action = str(t)
        if self.previous_state not in self.q_table:
            action_dict = dict()
            for turn in turns:
                action_dict[str(turn)] = 0
            self.q_table[self.previous_state] = action_dict
        if not silent:
            print("Q-learn moves " +
                  " to ".join([translate(c) for c in t]) + "\n")
        for i in range(0, len(t) - 1):  # loop is here to support double jumps
            board.move(t[i], t[i + 1])

    def end_game(self):
        write_q_table(self.q_table)
        # with open('lookup_table_size.txt', 'a') as file:
        #     file.write(str(len(self.lookup_table)) + "\n")
