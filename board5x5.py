from copy import deepcopy
from utils import base36encode
from random import choice
MAX_UNEVENTFUL_TURNS = 30


class Type:  # enumeration
    illegal = -1
    empty = 0
    red = 1
    red_king = 2
    black = 3
    black_king = 4


def get_score(grid, color):
    u_black = k_black = 0
    u_red = k_red = 0
    for i in range(0, len(grid)):
        for j in range(0, len(grid)):
            t = grid[i][j]
            if t == Type.black:
                u_black += 1
            elif t == Type.black_king:
                k_black += 1
            elif t == Type.red:
                u_red += 1
            elif t == Type.red_king:
                k_red += 1
    if color == Type.black:
        return u_black + 2 * k_black - (u_red + 2 * k_red)
    elif color == Type.red:
        return u_red + 2 * k_red - (u_black + 2 * k_black)
    else:
        raise ValueError("illegal color parameter")


def hash_board(grid):
    l = []
    for i in range(0, len(grid)):
        j = 1
        if i % 2 == 0:
            j = 0
        while j < len(grid):
            l.append(str(bin(grid[i][j]))[2:].zfill(3))
            j += 2
    return base36encode(int("".join(l), 2))


class Board5x5:

    def __init__(self):  # hard coding size to 8x8 for now...
        self.grid = [[Type.empty for i in range(5)] for j in range(5)]
        self._initialize_board()
        self.turn = choice([Type.red, Type.black])
        self.multijump = False
        self.jumpless_turns = 0

    # origin and destination are each a list of 2 ints representing
    # the row and column of the position, respectively
    # example: move_piece([3, 1], [4, 2])
    # return 1 if a multijump is available
    def move(self, origin, destination):
        # if user chose not to end their turn on a multijump opportunity
        # then they must take the jump using the original piece
        if self.multijump and (origin != self.multijump_pos or destination not in self.multijumps):
            raise ValueError("must take jump")
        self.multijump = False
        self.multijump_pos = []
        self.multijumps = []

        if not self._is_valid_move(self.grid, origin, destination):
            raise ValueError("illegal move")

        ori_r, ori_c = origin
        dest_r, dest_c = destination

        self.grid[dest_r][dest_c] = self.grid[ori_r][ori_c]
        self.grid[ori_r][ori_c] = Type.empty
        if self._should_crown(destination):
            # crown piece (1 goes to 2, 3 goes to 4)
            self.grid[dest_r][dest_c] += 1

        if abs(dest_r - ori_r) == 2:  # a jump has occured
            self.jumpless_turns = 0
            r_offset = (dest_r - ori_r) // 2
            c_offset = (dest_c - ori_c) // 2
            self.grid[ori_r + r_offset][ori_c + c_offset] = Type.empty
            if self._can_still_jump(destination):
                return 1

        else:
            self.jumpless_turns += 1

        self.flip_turn()

    def recursive_jumps(self, grid, move):
        moves = []
        pos = move[len(move) - 1]
        for s1 in [-2, 2]:
            for s2 in [-2, 2]:
                if self._is_valid_move(grid, pos, [pos[0] + s1, pos[1] + s2]):
                    moves.append(move + [[pos[0] + s1, pos[1] + s2]])
                    newgrid = deepcopy(grid)
                    newgrid[pos[0] + s1][pos[1] + s2] = newgrid[pos[0]][pos[1]]
                    newgrid[pos[0]][pos[1]] = Type.empty
                    newgrid[pos[0] + (s1 // 2)][pos[1] +
                                                (s2 // 2)] = Type.empty
                    newmove = move + [[pos[0] + s1, pos[1] + s2]]
                    moves += self.recursive_jumps(newgrid, newmove)
        return moves

    def get_all_legal_moves(self, grid):
        moves = []
        for i in range(len(grid)):
            for j in range(len(grid)):
                for jump in [1, 2]:
                    for sign1 in [-1, 1]:
                        for sign2 in [-1, 1]:
                            dest = [i + (jump * sign1), j + (jump * sign2)]
                            if self._is_valid_move(grid, [i, j],  dest):
                                move = [[i, j], dest]
                                moves.append(move)
                                if jump == 2:
                                    newgrid = deepcopy(grid)
                                    newgrid[dest[0]][dest[1]] = newgrid[i][j]
                                    newgrid[i][j] = Type.empty
                                    newgrid[i + sign1][j + sign2] = Type.empty
                                    moves += self.recursive_jumps(
                                        newgrid, move)

        return [tuple([tuple(y) for y in x]) for x in moves]

    def flip_turn(self):
        if self.turn == Type.black:
            self.turn = Type.red
        else:
            self.turn = Type.black

    def hold_turn(self, destination):
        self.multijump = True
        self.multijump_pos = destination

    # Returns 1 if red wins, 0 if black wins, -1 if draw, -2 if no winner
    def game_status(self):
        # Infinite chase
        # For now this just returns -1 in order to print the draw message and end the game
        # later this -1 could signal the AI to giveup to allow the game to end
        if self.jumpless_turns == MAX_UNEVENTFUL_TURNS:
            return -1

        # Win by jumping other pieces
        red_found = False
        black_found = False
        for list in self.grid:
            if Type.red in list or Type.red_king in list:
                red_found = True
            if Type.black in list or Type.black_king in list:
                black_found = True
        if not red_found:
            return 1
        if not black_found:
            return 2

        # Win by trapping the opponent
        moves = self.get_all_legal_moves(self.grid)
        if len(moves) == 0:
            if self.turn == Type.red:
                return 1
            else:
                return 2

        return 0

    # overridden str() method allows you to simply call print(my_board)
    def __str__(self):
        output = "    0   1   2   3   4\n"
        output += u'  ╭' + (u'───┬' * (len(self.grid) - 1)) + u'───╮\n'
        # Feel free to change any of these printed symbols
        for row in range(len(self.grid)):
            output += chr(row + 65)
            for col in self.grid[row]:
                output += u' │ '
                if col == 0:
                    output += " "
                elif col == Type.illegal:  # illegal space
                    output += " "
                elif col == Type.red:
                    output += "r"
                elif col == Type.red_king:
                    output += "R"
                elif col == Type.black:
                    output += "b"
                elif col == Type.black_king:
                    output += "B"
            output += u" │\n"
            if row != 4:
                output += u'  ├' + (u'───┼' * (len(self.grid) - 1)) + u'───┤\n'
        output += u'  ╰' + (u'───┴' * (len(self.grid) - 1) + u'───╯\n')
        if self.turn == Type.black:
            output += "\nBlack's turn\n"
        else:
            output += "\nRed's turn\n"
        return output

    def _can_still_jump(self, position):
        pos_r, pos_c = position
        next_jump = [pos_r + 2, pos_c + 2]
        if self._is_valid_move(self.grid, position, next_jump):
            self.multijumps.append(next_jump)
        next_jump = [pos_r + 2, pos_c - 2]
        if self._is_valid_move(self.grid, position, next_jump):
            self.multijumps.append(next_jump)
        next_jump = [pos_r - 2, pos_c - 2]
        if self._is_valid_move(self.grid, position, next_jump):
            self.multijumps.append(next_jump)
        next_jump = [pos_r - 2, pos_c + 2]
        if self._is_valid_move(self.grid, position, next_jump):
            self.multijumps.append(next_jump)
        if self.multijumps.__len__() != 0:
            return True
        return False

    def _is_valid_move(self, grid, origin, destination):
        ori_r, ori_c = origin
        ori_type = grid[ori_r][ori_c]
        dest_r, dest_c = destination

        if not (0 <= ori_r <= 4):
            return False
        if not (0 <= ori_c <= 4):
            return False
        if not (0 <= dest_r <= 4):
            return False
        if not (0 <= dest_c <= 4):
            return False

        if (ori_type != self.turn
                and ori_type != self.turn + 1):
            return False

        if grid[dest_r][dest_c] != Type.empty:
            return False

        if ori_r == dest_r or ori_c == dest_c:
            return False

        if abs(dest_r - ori_r) > 2 or abs(dest_c - ori_c) > 2:
            return False

        if abs(dest_r - ori_r) != abs(dest_c - ori_c):
            return False

        if ori_type == Type.black:
            if dest_r < ori_r:
                return False
            if abs(dest_r - ori_r) == 2:
                c_offset = (dest_c - ori_c) // 2
                if (grid[ori_r + 1][ori_c + c_offset] != Type.red
                        and grid[ori_r + 1][ori_c + c_offset] != Type.red_king):
                    return False

        if ori_type == Type.red:
            if dest_r > ori_r:
                return False
            if abs(dest_r - ori_r) == 2:
                c_offset = (dest_c - ori_c) // 2
                if (grid[ori_r - 1][ori_c + c_offset] != Type.black
                        and grid[ori_r - 1][ori_c + c_offset] != Type.black_king):
                    return False

        if ori_type == Type.black_king:
            if abs(dest_r - ori_r) == 2:
                r_offset = (dest_r - ori_r) // 2
                c_offset = (dest_c - ori_c) // 2
                if (grid[ori_r + r_offset][ori_c + c_offset] != Type.red
                        and grid[ori_r + r_offset][ori_c + c_offset] != Type.red_king):
                    return False

        if ori_type == Type.red_king:
            if abs(dest_r - ori_r) == 2:
                r_offset = (dest_r - ori_r) // 2
                c_offset = (dest_c - ori_c) // 2
                if (grid[ori_r + r_offset][ori_c + c_offset] != Type.black
                        and grid[ori_r + r_offset][ori_c + c_offset] != Type.black_king):
                    return False

        return True

    def _should_crown(self, position):
        pos_r, pos_c = position
        if self.grid[pos_r][pos_c] == Type.red and pos_r == 0:
            return True
        if self.grid[pos_r][pos_c] == Type.black and pos_r == 4:
            return True
        return False

    def _initialize_board(self):
        # # Debugging multi jumps
        # self.grid[0][3] = Type.black
        # self.grid[0][0] = Type.black
        # self.grid[1][2] = Type.red
        # self.grid[1][4] = Type.red
        # self.grid[3][2] = Type.red
        # self.grid[5][2] = Type.red
        # self.grid[5][4] = Type.red

        for i in range(0, len(self.grid)):  # place initial black pieces
            if i % 2 == 0:
                self.grid[0][i] = Type.black
            else:
                self.grid[0][i] = Type.illegal
        for i in range(0, len(self.grid)):
            if i % 2 == 1:
                self.grid[1][i] = Type.black
            else:
                self.grid[1][i] = Type.illegal

        for j in range(0, len(self.grid)):
            if j % 2 == 1:
                self.grid[2][j] = Type.illegal

        for i in range(0, len(self.grid)):  # place initial red pieces
            if i % 2 == 1:
                self.grid[3][i] = Type.red
            else:
                self.grid[3][i] = Type.illegal
        for i in range(0, len(self.grid)):
            if i % 2 == 0:
                self.grid[4][i] = Type.red
            else:
                self.grid[4][i] = Type.illegal
