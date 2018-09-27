# from board import Board, get_score, Type
# from board5x5 import *
from board6x6 import *
from time import sleep
from ai import ComputerPlayer
from sarsa import SARSAPlayer
from naive_ai import NaiveComputerPlayer
from red_ai import ComputerPlayerRed
from utils import *
from time import time


TRAINING = True
TRAIN_HOURS = 5
def game_is_over(b, cp1):
    status = b.game_status()

    # Check for a winner
    if status == 2:
        # print(b)
        print("Red Wins!")
        cp1.inform_lost()
        # with open("winners.txt", "a") as f:
        #     f.write("r\n")
        return True
    elif status == 1:
        # print(b)
        print("Black Wins!")
        cp1.inform_won()
        # with open("winners.txt", "a") as f:
        #     f.write("b\n")
        return True
    # Temporary
    elif status == -1:
        # print(b)
        print("Draw!")
        # with open("winners.txt", "a") as f:
        #     f.write("d\n")
        return True
    return False


if __name__ == "__main__":
    print("loading Q-table...")
    q_table = load_q_table()
    cp1 = ComputerPlayer(q_table=q_table) # Q-learn
    cp2 = NaiveComputerPlayer()
    t = time()
    big_t = time()
    while True:
        cp1.previous_state = cp1.previous_action = None
        try:
            b = Board6x6()
            # with open("q_table_size.txt", "a") as f:
            #     f.write(str(len(cp1.q_table)) + "\n")
            while True:
                if not TRAINING:
                    print(b)
                    sleep(0.75)
                if game_is_over(b, cp1):
                    # cp1.end_game()
                    break
                if b.turn == Type.black:
                    cp1.play(b, silent=TRAINING)
                else:
                    if TRAINING:
                        cp2.play(b, silent=TRAINING)
                    else:
                        try:

                            # print(get_score(b.grid, Type.black))
                            # Get input
                            move = input("space-separated move: ").upper().split()
                            while move_is_illegal(move):
                                print("ILLEGAL MOVE. TRY AGAIN. MOVES SHOULD LOOK SOMETHING LIKE (ex: \"e4 d5\")")
                                move = input("space-separated move: ").upper().split()
                            ori, dest = move

                            # Convert the letter to the corresponding row number (0 - 7)
                            ori = [(ord(ori[0]) - 65), int(ori[1])]
                            dest = [(ord(dest[0]) - 65), int(dest[1])]
                            print("")

                            # if move is a multijump play allow the user to choose
                            # whether to take the jumps or pass their turn
                            if b.move(ori, dest) == 1:
                                while True:
                                    skip = input("End turn? (Y/N) ").upper()
                                    # flip turn and wait for next users move
                                    if skip == "Y":
                                        print("")
                                        b.flip_turn()
                                        break
                                    # wait for the next users move without flipping the turn
                                    elif skip == "N":
                                        print("")
                                        b.hold_turn(dest)
                                        break
                                    else:
                                        print("Invalid input!\n")

                        except ValueError as e:
                            print("Error: " + str(e) + "\n")
            if TRAINING and time() - big_t > TRAIN_HOURS * 3600:
                print("{} hours passed; done".format(TRAIN_HOURS))
                cp1.end_game()
                break
            if TRAINING and time() - t > 5000:
                cp1.end_game()
                t = time()

        except KeyboardInterrupt:
            cp1.end_game()
            break
