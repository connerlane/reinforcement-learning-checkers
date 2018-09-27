import json
from pathlib import Path
import sys


def move_is_illegal(move):
    if len(move) != 2:
        return True
    if len(move[0]) != 2 or len(move[1]) != 2:
        return True
    if not move[0][0].isalpha() or not move[1][0].isalpha():
        return True
    if not move[0][1].isnumeric() or not move[1][1].isnumeric():
        return True
    return False

def lookup_hash(h, table):
    if h in table:
        return table[h]
    else:
        l = len(table)
        table[h] = l
        return l


def write_lookup_table(table):
    with open('lookup_table.txt', 'w') as file:
        file.write(json.dumps(table))


def write_q_table(table):
    print("writing q_table")
    with open('q_table.json', 'w') as file:
        file.write(json.dumps(table))


def load_q_table():
    table_file = Path("q_table.json")
    if table_file.exists():
        d = json.load(open('q_table.json'))
        return d
    return dict()


def base36encode(number, alphabet='0123456789ABCDEFGHIJKLMNOPQRSTUVWXYZ'):
    """Converts an integer to a base36 string."""

    base36 = ''
    sign = ''

    if number < 0:
        sign = '-'
        number = -number

    if 0 <= number < len(alphabet):
        return sign + alphabet[number]

    while number != 0:
        number, i = divmod(number, len(alphabet))
        base36 = alphabet[i] + base36

    return sign + base36


def load_lookup_table():
    table_file = Path("lookup_table.txt")
    if table_file.exists():
        d = json.load(open('lookup_table.txt'))
        return {int(k): v for k, v in d.items()}
    return dict()


def translate(move):
    c = chr(move[0] + 65)
    return c + str(move[1])


def hash_action(action):
    h = hash(action)
    if h < 0:
        h += sys.maxsize + 1
    return base36encode(h)
