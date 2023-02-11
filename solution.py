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
        self.goal_piece_coordinates = [0, 0] # added this to keep track of the 2x2 piece's coordinates
        self.__construct_grid()

        #self.id_val = hash(str(self))


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
                # store the (x,y) coordinates of the 2x2 goal piece
                self.goal_piece_coordinates[0] = piece.coord_x
                self.goal_piece_coordinates[1] = piece.coord_y
                
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
        
        board_str = str(board.grid)
        self.id = hash(board_str)

        #self.id = board.id_val
        
        #self.id = hash(board)  # The id for breaking ties.
    
    # overloading the < operator for the heap used in A*
    def __lt__(self, other):
        if self.f == other.f:
            return self.id < other.id
        return self.f < other.f


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
    

################################

def manhattan_distance(board):
    position_1_x = board.goal_piece_coordinates[0]
    position_1_y = board.goal_piece_coordinates[1]

    # the goal coordinate for the 2x2 piece is at (x, y) = (1, 1)
    position_end_x = 1
    position_end_y = 3

    return (abs(position_1_x - position_end_x) + abs(position_1_y - position_end_y))


def goal_test(state):
    # we could also check that the right grid spots have goal characters
    return (state.board.goal_piece_coordinates == [1,3])


# need the spot to be empty and within the board for the spot to be valid
def check_valid_spot(state, x, y):
    if(0 <= x < state.board.width and (0 <= y < state.board.height)):
        if(state.board.grid[y][x] == char_empty):
            return True
    else:
        return False 


# this function is used to move the piece and then create and return a new state
# direction can be 'up', 'down', 'left', or 'right'
def get_new_state(state, piece_x, piece_y, direction):
    curr_board = state.board
    
    new_board = deepcopy(curr_board) # create a new board - will move piece on this board

    # find the piece on the new baord and update its position (move it up)           
    for piece in new_board.pieces:
        if(piece.coord_x == piece_x and piece.coord_y == piece_y):
            
            if direction == "left":
                piece.coord_x -= 1
            
            elif direction == "right":
                piece.coord_x += 1
            
            elif direction == "up":
                piece.coord_y -= 1
            
            else: # moving the piece down
                piece.coord_y += 1
            
            # piece moved so now break out of loop
            break
    
    # now create a new state using this board and add it as a successor
    # f-value the same as the depth?
    test_board = Board(new_board.pieces) # to update grid
    updated_depth = state.depth + 1
    f_value = updated_depth + manhattan_distance(test_board)

    print(f"Here is the f value of the new state: {f_value}")
    new_state = State(test_board, f = f_value, depth = updated_depth, parent = state)
    
    # print("here are the pieces of the new state: ")
    # print(new_state.board.display())

    return new_state

def generate_successors(state):
    successors = []   # a list to store all our successors, to be returned at the end
    curr_pieces = state.board.pieces

    for piece in curr_pieces:

        # get (x,y) coordinates of the current piece 
        x = piece.coord_x
        y = piece.coord_y
        
        if(piece.is_goal):
            # try up
            if(check_valid_spot(state, x, y-1) and check_valid_spot(state, x+1, y-1)):     
                new_state = get_new_state(state, piece.coord_x, piece.coord_y, "up")
                successors.append(new_state)

            # try down
            if(check_valid_spot(state, x, y+2) and check_valid_spot(state, x+1, y+2)):     
                new_state = get_new_state(state, piece.coord_x, piece.coord_y, "down")
                successors.append(new_state)

            # try left
            if(check_valid_spot(state, x-1, y) and check_valid_spot(state, x-1, y+1)):     
                new_state = get_new_state(state, piece.coord_x, piece.coord_y, "left")
                successors.append(new_state)

            # try right
            if(check_valid_spot(state, x+2, y) and check_valid_spot(state, x+2, y+1)):     
                new_state = get_new_state(state, piece.coord_x, piece.coord_y, "right")
                successors.append(new_state)
        
        elif(piece.orientation == 'h'):
            # try up
            if(check_valid_spot(state, x, y-1) and check_valid_spot(state, x+1, y-1)):     
                new_state = get_new_state(state, piece.coord_x, piece.coord_y, "up")
                successors.append(new_state)
            
            # try down
            if(check_valid_spot(state, x, y+1) and check_valid_spot(state, x+1, y+1)):     
                new_state = get_new_state(state, piece.coord_x, piece.coord_y, "down")
                successors.append(new_state)

            # try left
            if(check_valid_spot(state, x-1, y)):     
                new_state = get_new_state(state, piece.coord_x, piece.coord_y, "left")
                successors.append(new_state)

            # try right
            if(check_valid_spot(state, x+2, y)):     
                new_state = get_new_state(state, piece.coord_x, piece.coord_y, "right")
                successors.append(new_state)
        
        
        elif(piece.orientation == 'v'):
            # try up
            if(check_valid_spot(state, x, y-1)):     
                new_state = get_new_state(state, piece.coord_x, piece.coord_y, "up")
                successors.append(new_state)
            
            # try down
            if(check_valid_spot(state, x, y+2)):     
                new_state = get_new_state(state, piece.coord_x, piece.coord_y, "down")
                successors.append(new_state)

            # try left
            if(check_valid_spot(state, x-1, y) and check_valid_spot(state, x-1, y+1)):     
                new_state = get_new_state(state, piece.coord_x, piece.coord_y, "left")
                successors.append(new_state)

            # try right
            if(check_valid_spot(state, x+1, y) and check_valid_spot(state, x+1, y+1)):     
                new_state = get_new_state(state, piece.coord_x, piece.coord_y, "right")
                successors.append(new_state)
            

        # its a 1x1 piece
        else:
            # try up
            if(check_valid_spot(state, x, y-1)):     
                new_state = get_new_state(state, piece.coord_x, piece.coord_y, "up")
                successors.append(new_state)
            
            # try down
            if(check_valid_spot(state, x, y+1)):     
                new_state = get_new_state(state, piece.coord_x, piece.coord_y, "down")
                successors.append(new_state)

            # try left
            if(check_valid_spot(state, x-1, y)):     
                new_state = get_new_state(state, piece.coord_x, piece.coord_y, "left")
                successors.append(new_state)

            # try right
            if(check_valid_spot(state, x+1, y)):     
                new_state = get_new_state(state, piece.coord_x, piece.coord_y, "right")
                successors.append(new_state)
        
    return successors



def DFS(state):
    # push the initial state (argument) onto the stack
    # pop the top state from the stack, if it is the goal then return
    # else generate all successors and add them to the stack and repeat the process until the stack is empty
    
    frontier = [state]
    visited = set()

    while frontier:
        curr_state = frontier.pop()

        curr_state.board.display()
        print()

        if curr_state.id in visited:
            continue

        if goal_test(curr_state):
            #print(" we in the DFS goal state boiiiiiiiiiii")
            return curr_state
        else:
            # print("I am adding the following to visited:")
            # print(visited)

            visited.add(curr_state.id)
            successors = generate_successors(curr_state)

            # make sure we only add successor states that haven't been explored yet
            for state in successors:
                if state.id not in visited:
                    frontier.append(state)
    
    print("I am about to return None")
    return None # if no solution is found - goal state is never reached


def A_star(state):
    # push the initial state onto the priority queue with its cost + heuristic value
    # the cost so far is the number of moves that have been taken so far to reach the state from the start state
    # add states and repeat until the prioirty queue is empty
    frontier = []
    heappush(frontier, state) # add the first state to the frontier which is now a heap
    visited = set()

    while frontier:   
        curr_state = heappop(frontier)
        # print(curr_state.id)
        if curr_state.id in visited:
            continue
        
        visited.add(curr_state.id)

        if goal_test(curr_state):
            
            print("reached the goal state, here is the board:")
            curr_state.board.display()
            #print()

            return curr_state

        curr_state.board.display()
        print()
        

        successors = generate_successors(curr_state)

        for s in successors:
            # print("Successor:")
            # print(state.board.pieces)
            heappush(frontier, s)
        

        # for state in successors:
        #     if state.id not in visited:
        #         heappush(frontier, state)
    
    return None



def write_to_file(first_state, filename, solution):
    
    with open(filename, "w") as file:
        # write the initial solution to the file
        for row in first_state.board.grid:
            for char in row:
                file.write(str(char))
            
            file.write("\n")
        
        file.write("\n")

        # write the solution to the file
        counter = 0
        
        all_states = []
        while solution.parent != None:
            all_states.append(solution)
            solution = solution.parent
        
        all_states.reverse()

        for state in all_states:
            for row in state.board.grid:
                for char in row:
                    file.write(str(char))
                
                file.write("\n")
            
            file.write("\n")

        # while solution.parent != None:
        #     counter += 1
        #     for row in solution.board.grid:
        #         for char in row:
        #             file.write(str(char))
                
        #         file.write("\n")
            
        #     file.write("\n")
        #     solution = solution.parent
        
        #print(f"here is the count value: {counter}")


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

    first_state = State(board, 0, 0, parent=None) # generate the initial state

    # run the wanted search algorithm
    if args.algo == 'astar':
        solution = A_star(first_state)
    else:
        solution = DFS(first_state)

    # write the solution to the output file
    # output_file = open(args.outputfile, "x")
    write_to_file(first_state, args.outputfile, solution)
