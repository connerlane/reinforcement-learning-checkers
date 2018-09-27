from random import choice, uniform


def translate(move):
    c = chr(move[0] + 65)
    return c + str(move[1])


dumb_emojis = ['🤤', '🔨', '🔩', '😥', '😓', '😴', '🐵', '🙉', '🐢', '🦍', '🥉', '🗿']

# This computer player simply chooses the move that will
# maximize profit for itself at each step.
# it is simply to expedite the early stages of training for the q learner.


class NaiveComputerPlayer():

    def __init__(self):
        pass

    def play(self, board, silent=False):
        if not silent:
            print(board)
        turns = board.get_all_legal_moves(board.grid)
        turns.sort(key=lambda x: abs(x[0][0] - x[1][0]))
        turns.sort(key=len)
        # print(turns)
        if uniform(0, 1) > 0.3:
            if abs(turns[len(turns) - 1][0][0] - turns[len(turns) - 1][1][0]) == 1:
                t = choice(turns)
            else:
                t = turns.pop()
        else:
            t = choice(turns)
        # t = choice(turns)
        if not silent:
            print("Naive moves " +
                  " to ".join([translate(c) for c in t]) + choice(dumb_emojis) + "\n")
        for i in range(0, len(t) - 1):  # loop is here to support double jumps
            board.move(t[i], t[i + 1])

    def end_game(self):
        write_lookup_table(self.lookup_table)
