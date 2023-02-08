from copy import deepcopy
from heapq import heappush, heappop
import time
import argparse
import sys

#====================================================================================

char_goal = '1'
char_single = '2'
char_empty = '.'

class Piece:
    """
    This represents a piece on the Hua Rong Dao puzzle.
    """

    def __init__(self, is_goal, is_single, coord_x, coord_y, orientation):
        """
        :param is_goal: True if the piece is the goal piece and False otherwise.
        :type is_goal: bool
        :param is_single: True if this piece is a 1x1 piece and False otherwise.
        :type is_single: bool
        :param coord_x: The x coordinate of the top left corner of the piece.
        :type coord_x: int
        :param coord_y: The y coordinate of the top left corner of the piece.
        :type coord_y: int
        :param orientation: The orientation of the piece (one of 'h' or 'v') 
            if the piece is a 1x2 piece. Otherwise, this is None
        :type orientation: str
        """

        self.is_goal = is_goal
        self.is_single = is_single
        self.coord_x = coord_x
        self.coord_y = coord_y
        self.orientation = orientation

    def __repr__(self):
        return '{} {} {} {} {}'.format(self.is_goal, self.is_single, \
            self.coord_x, self.coord_y, self.orientation)

class Board:
    """
    Board class for setting up the playing board.
    """

    def __init__(self, pieces):
        """
        :param pieces: The list of Pieces
        :type pieces: List[Piece]
        """

        self.width = 4
        self.height = 5

        self.pieces = pieces

        # self.grid is a 2-d (size * size) array automatically generated
        # using the information on the pieces when a board is being created.
        # A grid contains the symbol for representing the pieces on the board.
        self.grid = [] # we append lines (the rows) which makes in 2D
        self.__construct_grid()


    def __construct_grid(self):
        """
        Called in __init__ to set up a 2-d grid based on the piece location information.

        """

        for i in range(self.height):
            line = [] # a new row to append into the grid
            for j in range(self.width): # to create each row (which has 4 entries)
                line.append('.') # adding 4 empty spots to the new row to be added to grid
            self.grid.append(line) # adding the new line into the grid

        for piece in self.pieces:
            if piece.is_goal:
                self.grid[piece.coord_y][piece.coord_x] = char_goal
                self.grid[piece.coord_y][piece.coord_x + 1] = char_goal
                self.grid[piece.coord_y + 1][piece.coord_x] = char_goal
                self.grid[piece.coord_y + 1][piece.coord_x + 1] = char_goal
            elif piece.is_single:
                self.grid[piece.coord_y][piece.coord_x] = char_single
            else:
                if piece.orientation == 'h':
                    self.grid[piece.coord_y][piece.coord_x] = '<'
                    self.grid[piece.coord_y][piece.coord_x + 1] = '>'
                elif piece.orientation == 'v':
                    self.grid[piece.coord_y][piece.coord_x] = '^'
                    self.grid[piece.coord_y + 1][piece.coord_x] = 'v'

    def display(self):
        """
        Print out the current board.

        """
        for i, line in enumerate(self.grid):
            for ch in line:
                print(ch, end='')
            print()
        

class State:
    """
    State class wrapping a Board with some extra current state information.
    Note that State and Board are different. Board has the locations of the pieces. 
    State has a Board and some extra information that is relevant to the search: 
    heuristic function, f value, current depth and parent.
    """

    def __init__(self, board, f, depth, parent=None):
        """
        :param board: The board of the state.
        :type board: Board
        :param f: The f value of current state.
        :type f: int
        :param depth: The depth of current state in the search tree.
        :type depth: int
        :param parent: The parent of current state.
        :type parent: Optional[State]
        """
        self.board = board
        self.f = f
        self.depth = depth
        self.parent = parent
        self.id = hash(board)  # The id for breaking ties.


def read_from_file(filename):
    """
    Load initial board from a given file.

    :param filename: The name of the given file.
    :type filename: str
    :return: A loaded board
    :rtype: Board
    """

    puzzle_file = open(filename, "r")

    line_index = 0
    pieces = []
    g_found = False

    for line in puzzle_file:

        for x, ch in enumerate(line):

            if ch == '^': # found vertical piece
                pieces.append(Piece(False, False, x, line_index, 'v'))
            elif ch == '<': # found horizontal piece
                pieces.append(Piece(False, False, x, line_index, 'h'))
            elif ch == char_single:
                pieces.append(Piece(False, True, x, line_index, None))
            elif ch == char_goal:
                if g_found == False:
                    pieces.append(Piece(True, False, x, line_index, None))
                    g_found = True
        line_index += 1

    puzzle_file.close()

    board = Board(pieces)
    
    return board



if __name__ == "__main__":

    parser = argparse.ArgumentParser()
    parser.add_argument(
        "--inputfile",
        type=str,
        required=True,
        help="The input file that contains the puzzle."
    )
    parser.add_argument(
        "--outputfile",
        type=str,
        required=True,
        help="The output file that contains the solution."
    )
    parser.add_argument(
        "--algo",
        type=str,
        required=True,
        choices=['astar', 'dfs'],
        help="The searching algorithm."
    )
    args = parser.parse_args()

    # read the board from the file
    board = read_from_file(args.inputfile)
    



def manhattan_distance(position1, position2):
    return (abs(position1[0] - position2[0]) + abs(position1[1] - position2[1]))

def goal_test(state):
    #return (state.board.grid[3][1] == char_goal) 
    # if the top left corner of goal char is at 3,1 then returns true
    return (state.board.grid[4][1] == char_goal and state.board.grid[4][2] == char_goal)

def get_heuristic(state):
    # need to find the top-left corner of goal piece and compute manhattan
    curr_grid = state.board.grid
    for i in range(len(curr_grid)):
        for j in range(len(curr_grid[0])):
            if(curr_grid[i][j] == char_goal):
                return manhattan_distance((i, j) , (3,1))
                # return manhattan distance from upper left of goal piece to the goal position 3,1

def generate_successors(state):
    # first find the positions of each of the empty tiles
    curr_grid = state.board.grid

    for i in range(len(curr_grid)):
        for j in range(len(curr_grid[0])):
            print("hello")

# need the spot to be empty and within the board for the spot to be valid
def check_valid_move(state, row, col):
    if(state[row][col] == char_empty and (0 <= row < len(state.board.width) and (0 <= col < len(state.board.height)))):
        return True
    else:
        return False 



# pass in the row and col of the 2x2 piece (! which is top left-most position of it)
def do_2x2_piece(state, row, col):
    # check up
    if(check_valid_move(state, row-1, col) and check_valid_move(state, row-1, col+1)):
        # do a move up on state copy and add that as a successor
        
        # make a copy of the current state
        new_successor = deepcopy(state)
        
        # shift up
        new_successor.board.grid[row-1, col] = char_goal
        new_successor.board.grid[row-1, col+1] = char_goal
        
        # empty spots below the piece due to its shift up
        new_successor.board.grid[row+1, col] = char_empty
        new_successor.board.grid[row+1, col+1] = char_empty

        # compute the new_successor's cost and update that attribute
        # mark the 4 positions of the 2x2 piece in the OG state as completed
        # add the successor to the heap

    
    # check down
    if(check_valid_move(state, row+2, col) and check_valid_move(state, row+2, col+1)):
        # do a move down on state copy and add that as a successor

        # make a copy of the current state
        new_successor = deepcopy(state)
        
        # shift down
        new_successor.board.grid[row+2, col] = char_goal
        new_successor.board.grid[row+2, col+1] = char_goal
        
        # empty spots below the piece due to its shift down
        new_successor.board.grid[row, col] = char_empty
        new_successor.board.grid[row, col+1] = char_empty

        # compute the new_successor's cost and update that attribute
        # mark the 4 positions of the 2x2 piece in the OG state as completed
        # add the successor to the heap

    
    # check left
    if(check_valid_move(state, row, col-1) and check_valid_move(state, row+1, col-1)):
        # do a move left on state copy and add that as a successor

        # make a copy of the current state
        new_successor = deepcopy(state)
        
        # shift left
        new_successor.board.grid[row, col-1] = char_goal
        new_successor.board.grid[row+1, col-1] = char_goal
        
        # empty spots below the piece due to its shift left
        new_successor.board.grid[row, col+1] = char_empty
        new_successor.board.grid[row+1, col+1] = char_empty

        # compute the new_successor's cost and update that attribute
        # mark the 4 positions of the 2x2 piece in the OG state as completed
        # add the successor to the heap

    # check right
    if(check_valid_move(state, row, col+2) and check_valid_move(state, row+1, col+2)):
        # do a move right on state copy and add that as a successor

        # make a copy of the current state
        new_successor = deepcopy(state)
        
        # shift right
        new_successor.board.grid[row, col+2] = char_goal
        new_successor.board.grid[row+1, col+2] = char_goal
        
        # empty spots below the piece due to its shift right
        new_successor.board.grid[row, col] = char_empty
        new_successor.board.grid[row+1, col] = char_empty

        # compute the new_successor's cost and update that attribute
        # mark the 4 positions of the 2x2 piece in the OG state as completed
        # add the successor to the heap
    

def do_1x1_piece(state, row, col):
    # check up
    if(check_valid_move(state, row-1, col)):
        new_successor = deepcopy(state)
        new_successor.board.grid[row-1][col] = char_single
        new_successor.board.grid[row][col] = char_empty

    # check down
    if(check_valid_move(state, row+1, col)):
        new_successor = deepcopy(state)
        new_successor.board.grid[row+1][col] = char_single
        new_successor.board.grid[row][col] = char_empty


    #check left
    if(check_valid_move(state, row, col-1)):
        new_successor = deepcopy(state)
        new_successor.board.grid[row][col-1] = char_single
        new_successor.board.grid[row][col] = char_empty


    # check right
    if(check_valid_move(state, row, col+1)):
        new_successor = deepcopy(state)
        new_successor.board.grid[row][col+1] = char_single
        new_successor.board.grid[row][col] = char_empty

    
    # compute the new_successor's cost and update that attribute
    # mark the 4 positions of the 2x2 piece in the OG state as completed
    # add the successor to the heap

def do_1x2_piece(state, row, col):
    # first check orientation of the piece, whether its 2x1 or 1x2
    
    # check if its a 1x2 piece
    if(state.board.grid[row][col] == '<'):
        # check if we can move up
        if(check_valid_move(state, row-1, col) and check_valid_move(state, row-1, col+1)):
            new_successor = deepcopy(state)
            
            # shift up
            new_successor[row-1][col] = '<'
            new_successor[row-1][col+1] = '>'

            # remove below due to shift up
            new_successor[row][col] = char_empty
            new_successor[row][col+1] = char_empty
        
        # check if we can move down
        if(check_valid_move(state, row+1, col) and check_valid_move(state, row+1, col+1)):
            new_successor = deepcopy(state)
            
            # shift down
            new_successor[row+1][col] = '<'
            new_successor[row+1][col+1] = '>'

            # remove below due to shift down
            new_successor[row][col] = char_empty
            new_successor[row][col+1] = char_empty
        
        # check if we can move left
        if(check_valid_move(state, row, col-1)):
            new_successor = deepcopy(state)

            new_successor[row][col-1] = '<'
            new_successor[row][col] = '>'
            new_successor[row][col+1] = char_empty

        # check if we can move right
        if(check_valid_move(state, row, col+2)):
            new_successor = deepcopy(state)

            new_successor[row][col+2] = '>'
            new_successor[row][col+1] = '<'
            new_successor[row][col] = char_empty    
    

    # else it is vertical orientation (2x1 piece)
    else:
        # check vertical movement
        if(check_valid_move(state, row-1, col)):
            new_successor = deepcopy(state)

            new_successor[row-1][col] = '^'
            new_successor[row][col] = 'v'
            new_successor[row+1][col] = char_empty
        
        # check downward movement
        if(check_valid_move(state, row+2, col)):
            new_successor = deepcopy(state)

            new_successor[row+2][col] = 'v'
            new_successor[row+1][col] = '^'
            new_successor[row][col] = char_empty
        
        # check leftward movement
        if(check_valid_move(state, row, col-1) and check_valid_move(state, row+1, col-1)):
            # make a copy of the current state
            new_successor = deepcopy(state)
            
            # shift left
            new_successor.board.grid[row][col-1] = '^'
            new_successor.board.grid[row+1][col-1] = 'v'

            # current spots become empty due to shift left
            new_successor.board.grid[row][col-1] = char_empty
            new_successor.board.grid[row+1][col-1] = char_empty


        # check rightward movement
        if(check_valid_move(state, row, col+1) and check_valid_move(state, row+1, col+1)):
            # make a copy of the current state
            new_successor = deepcopy(state)
            
            # shift left
            new_successor.board.grid[row][col+1] = '^'
            new_successor.board.grid[row+1][col+1] = 'v'

            # current spots become empty due to shift left
            new_successor.board.grid[row][col] = char_empty
            new_successor.board.grid[row+1][col] = char_empty


def DFS(state):
    # push the initial state (argument) onto the stack
    # pop the top state from the stack, if it is the goal then return
    # else generate all successors and add them to the stack and repeat the process until the stack is empty
    pass


def A_star(state):
    # push the initial state onto the priority queue with its cost + heuristic value
    # the cost so far is the number of moves that have been taken so far to reach the state from the start state
    # add states and repeat until the prioirty queue is empty
    pass


# ideas for generating successors:
#   - for each piece on the board, check for the validity (if empty spot) of each up, down, left, right positions
#     (check_valid_move() can be one of the helper functions)
#   - if the move is valid, then move the piece on a copy of the current state, then add this state to list
