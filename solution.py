class VisualizibleDict(dict):
    def __init__(self, mapping):
        super().__init__(mapping)
        self.assignments = []

    def __setitem__(self, box, value):
        """
        Please use this function to update your values dictionary!
        Assigns a value to a given box. If it updates the board record it.
        """

        # Don't waste memory appending actions that don't actually change any values
        if self[box] == value:
            return

        super().__setitem__(box, str(value))
        if len(value) == 1:
            self.assignments.append(self.copy())

def cross(A, B):
    "Cross product of elements in A and elements in B."
    return [a + b for a in A for b in B]

rows = 'ABCDEFGHI'
cols = '123456789'
boxes = cross(rows, cols)
row_units = [cross(r, cols) for r in rows]
column_units = [cross(rows, c) for c in cols]
square_units = [cross(rs, cs) for rs in ('ABC','DEF','GHI') for cs in ('123','456','789')]
diagonal_units = [[r+c for r,c in zip(rows, cols)], [r+c for r,c in zip(rows, reversed(cols))]]
units = row_units + column_units + square_units + diagonal_units
box_units = dict((s, [u for u in units if s in u]) for s in boxes)
box_peers = dict((s, set(sum(box_units[s],[]))-set([s])) for s in boxes)
        
def grid_values(grid):
    """
    Convert grid into a dict of {square: char} with '123456789' for empties.
    Args:
        grid(string) - A grid in string form.
    Returns:
        A grid in dictionary form
            Keys: The boxes, e.g., 'A1'
            Values: The value in each box, e.g., '8'. If the box has no value, then the value will be '123456789'.
    """
    return {pair[0]: pair[1] if pair[1] in '123456789' else '123456789'
            for pair in zip(cross(rows, cols), grid)}

def display(values):
    """
    Display the values as a 2-D grid.
    Args:
        values(dict): The sudoku in dictionary form
    """
    # make all boxes strings equal length
    width = 1+max(len(values[s]) for s in boxes)
    # add separators between squares
    line = '+'.join(['-'*(width*3)]*3) 

    for r in rows:
        print(''.join(values[r+c].center(width)+('|' if c in '36' else '')
                      for c in cols))
        if r in 'CF': print(line)
    return

def naked_twins(values):
    """Eliminate values using the naked twins strategy.
    Args:
        values(dict): a dictionary of the form {'box_name': '123456789', ...}

    Returns:
        the values dictionary with the naked twins eliminated from peers.
    """

    for unit in units:
        pairs = ((box1, box2) for box1 in unit for box2 in unit
            if box1 < box2 # skip duplicated pairs
            # and take only pairs having same 2 possible values
            and len(values[box1]) == 2 and set(values[box1]) == set(values[box2]))

        for box1, box2 in pairs:
            prohibited = values[box1] # dissallow this values for current unit
            other_boxes = (box for box in unit if box not in [box1, box2])
            for box in other_boxes: # and remove them from all other boxes in unit
                values[box] = values[box].replace(prohibited[0], '').replace(prohibited[1], '')

    return values

def eliminate(values):
    # loop over all boxes with single known value
    for box, box_value in ((b, v) for b, v in values.items() if len(v) == 1):
        for peer in box_peers[box]: # and remove this value from all its peers
            new_value = values[peer].replace(box_value, '')
            if not new_value: # do not assign empty string if no possible values - fail instead
                return False
            values[peer] = new_value
    return values

def only_choice(values):
    for unit in units:
        for digit in '123456789': # for all possible digits
            # find all boxes with this digit as possible value in current unit
            digit_boxes = [box for box in unit if digit in values[box]]
            if(len(digit_boxes) == 1): # if only one such box
                values[digit_boxes[0]] = digit # then we know its value :)
    return values

def reduce_puzzle(values):
    while True:
        # number of solved boxes before applying solving strategies
        solved_count_old = sum(1 for box, digits in values.items() if len(digits) == 1)

        # try apply strategies
        if not eliminate(values):
            return False
        if not only_choice(values):
            return False

        # number of solved boxes after applying solving strategies
        solved_count_new = sum(1 for box, digits in values.items() if len(digits) == 1)
        if solved_count_new == solved_count_old:
            break # stop if no new boxes have been solved
        
    return values

def search(values):
    if not reduce_puzzle(values):
        return False # backtrack if failed to reduce puzzle
    if not any(True for s in boxes if len(values[s]) != 1): 
        return values # return if all boxes are solved
    
    # find one of the unsolved boxes with minimal number of possible values
    box, _  = min((box, len(values[box])) for box in boxes if len(values[box]) > 1)
    for value in values[box]: # loop over DFS children
        # copy sudoku before recursive call since changes can be made during strategies execution
        new_sudoku = values.copy()
        new_sudoku[box] = value
        # DFS recursive vall for next node
        attempt = search(new_sudoku)
        if attempt:
            return attempt

def solve(grid):
    """
    Find the solution to a Sudoku grid.
    Args:
        grid(string): a string representing a sudoku grid.
            Example: '2.............62....1....7...6..8...3...9...7...6..4...4....8....52.............3'
    Returns:
        The dictionary representation of the final sudoku grid. False if no solution exists.
    """

    values = grid_values(grid)
    values = VisualizibleDict(values)
    return search(values)

if __name__ == '__main__':
    diag_sudoku_grid = '2.............62....1....7...6..8...3...9...7...6..4...4....8....52.............3'
    solution = solve(diag_sudoku_grid)
    display(solution)

    try:
        from visualize import visualize_assignments
        visualize_assignments(solution.assignments)

    except SystemExit:
        pass
    except:
        print('We could not visualize your board due to a pygame issue. Not a problem! It is not a requirement.')
