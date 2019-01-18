import argparse
import random
import time

# Max depth of the search tree
max_depth = 0

adjacents = {}


class InvalidSudokuError(Exception):
    """
    Raised when input sudoku is invalid.
    Invalid cases are: 1) Length of string representing sudoku is not 81 chars
    2) Initially assigned values (also called clues) do not have conflicting
    cases (e.g: two 3s in a row).
    """
    pass


def str_to_grid(sudoku, fill_possibilities=False):
    """
    Convert an 81-char string sequence representing sudoku into a grid (dict)
    with keys as indexes [0-80] and values as possible assignments. Valid
    values are [1-9] for filled cells. All other characters represent an empty
    cell.
    """
    if len(sudoku) != 81:
        return None

    possibilities = set(range(1, 10)) if fill_possibilities else set()

    return {ndx: {int(s)} if s in '123456789' else possibilities
            for ndx, s in enumerate(sudoku)}


def grid_to_str(grid):
    """
    Convert grid - our internal representation into an 81-char sudoku
    string
    """
    return ''.join(str(grid[ndx].pop()) for ndx in range(0, 81))


def display(sudoku, header=None):
    """
    Return a 'pretty print' sudoku string (2d) with an optional
    header message.

    input: 81 characters of sudoku sequence or a dict with keys [0-80]
    and possible assignments as values
    """
    grid = str_to_grid(sudoku) if type(sudoku) == str else sudoku

    result = ''

    if header:
        result += '\n\t{0}\n'.format(header)

    # Space added between cells for pretty printing
    space_btwn_cells = 2

    max_possibilities = max([len(v) for v in grid.values()])

    for ndx in range(0, 81):
        possibilities = grid[ndx]

        if ndx != 0 and ndx % 9 == 0:
            result += '\n'

        if ndx != 0 and ndx % 27 == 0:
            # 5 below because we add 3 spaces for ' | ' and 2 spaces
            # for before and after each cell'
            result += '-'*(max_possibilities*9 + space_btwn_cells*9 + 5) + '\n'

        if ndx != 0 and ndx % 3 == 0 and ndx % 9 != 0:
            result += ' | '

        # Print . in place of empty cells
        cell_content = ''.join(str(s) for s in sorted(possibilities)) \
            if len(possibilities) > 0 else '.'

        cell_padding = max_possibilities - len(cell_content)
        # Note ONE pre and post whitespace when forming contents of a cell
        result += ' ' + cell_content + ' '*cell_padding + ' '

    #print result + '\n'
    result += '\n'
    return result


def get_square_indices(row, col):
    """
    Given row and col of a cell, find all adjacent cells in its square.
    Return a list of zero-based indices
    """
    sq_row, sq_col = row/3, col/3
    # Identify the start location of square index in the grid
    sq_start_ndx = (sq_row*9*3) + (sq_col*3)
    sq_indices = [sq_start_ndx+c for c in [0, 1, 2, 9, 10, 11, 18, 19, 20]]

    return sq_indices


def is_solved(sudoku):
    """
    Return True if sudoku (81 character input) is solved, False otherwise if
    some characters (cells) are still unsolved.
    If input is invalid, raise InvalidSudokuError.
    """
    validate(sudoku)

    # The logic is that if we didn't find any conflict in the input sudoku
    # and all 81 characters are digits, it's a solved sudoku.
    return sudoku.isdigit()


def validate(sudoku):
    """
    Returns True if input 81-char sudoku string is valid (like no repeating
    chars in any row), raises InvalidSudokuError otherwise.
    """
    if sudoku is None or not isinstance(sudoku, basestring):
        raise InvalidSudokuError('Input must be an 81-character string')

    # Ensure input string is always 81 characters
    if not sudoku or len(sudoku) != 81:
        raise InvalidSudokuError('Input length is {0}. Expecting 81 characters'
                                 .format(len(sudoku)))

    # Ensure that initially assigned values do not have conflict.
    # E.g: repeating number in a row, col, square
    for ndx, s in enumerate(sudoku):
        # Initially assigned cell
        if s in '123456789':
            row, col = int(ndx/9), ndx % 9
            row_occurrences = [l for l, su in enumerate(sudoku[row*9:row*9+9])
                               if s == su]

            if len(row_occurrences) > 1:
                raise InvalidSudokuError('{0} appears {1}x in row {2}'.
                                         format(
                                             s, len(row_occurrences), row+1
                                         ))

            col_occurrences = [l for l, su in enumerate(sudoku[col::9])
                               if s == su]

            if len(col_occurrences) > 1:
                raise InvalidSudokuError('{0} appears {1}x in col {2}'.
                                         format(
                                             s, len(col_occurrences), col+1))

            sq_indices = get_square_indices(row, col)
            sq_occurrences = [l for l, su in enumerate(
                ''.join(sudoku[x] for x in sq_indices)
                ) if s == su]

            if len(sq_occurrences) > 1:
                raise InvalidSudokuError('{0} appears {1}x in a square'.
                                         format(s, len(sq_occurrences)))
    return True


def eliminate(grid, cell):
    """
    Given a cell in sudoku's current state, reduce possible digits by:
     1) Removing solved digits from cell's row, col and square
     2) Determining unique value looking at row, col and square - one at a time
        E.g: Cell 10 has '12345' and the union of all possible values of its
        row is '23456789', which means cell 10 can hold the value '1'
        set('12345') - set('23456789')

    Also check if reduction creates invalid state where number of all possible
    values in a row, column or square is not in {1,2,3,4,5,6,7,8,9}.

    grid: Current sudoku's state
    cell: Cell to remove possible digits from. This is the index in the grid
            in the range[0-80]

    Returns the new possible digits for the cell as a set or False if
        sudoku reaches an invalid state
    """
    possibilities = grid[cell]

    if len(possibilities) == 1:
        # This cell is solved
        return possibilities

    # Find all adjacents of this cell (all cells in this cell's row,
    # col and square)
    cell_adjacents = adjacents[cell][0] + adjacents[cell][1] + adjacents[cell][2]
    # Get all 'solved' digits from this cell's row, col and sq
    solved_adjacents_values = [grid[v] for v in cell_adjacents
                               if len(grid[v]) == 1]

    if solved_adjacents_values:
        new_possibilities = possibilities - set.union(*solved_adjacents_values)

        if len(new_possibilities) == 1:
            return new_possibilities
        else:
            possibilities = new_possibilities

    # Find if we have a unique value left in this cell by subtracting this
    # cell's possible values from all values in row or column or square
    # 0: row, 1: col, 2: square
    for uniqueness in [0, 1, 2]:
        adjacent_values = set.union(*[grid[v] for v in adjacents[cell][uniqueness]])
        unique_values = possibilities - adjacent_values

        if len(unique_values) == 1:
            return unique_values

        # Did our reduction lead to an invalid state?
        if {1, 2, 3, 4, 5, 6, 7, 8, 9} != adjacent_values | possibilities:
            return False

    return possibilities


def reduce_grid(grid):
    """
    Iterate through all cells in the grid and eliminate possibilities to create
    a reduced grid

    Returns a reduced grid if elimination was successful.
    Returns False if elimination leads to an invalid state (e.g: invalid
    assignment)
    """
    cell = 0

    while cell < 81:
        n = len(grid[cell])

        if n > 1:
            results = eliminate(grid, cell)
            # Invalid state! Do not assign and return FALSE
            if not results:
                return False

            if len(results) < n:
                # We reduce possible values for this cell. Restart reduction
                grid[cell] = results
                cell = 0
                continue

        cell += 1

    return grid


def search(grid, randomize_traversal, depth=0):

    # Track max depth we hit using this approach
    global max_depth
    max_depth = max(max_depth, depth)

    if max_depth > 81:
        # In the worst case, we would have tried 81 possible assignments in a
        # given branch. Curious to find a sudoku, which leads to this.
        print 'Max depth of {0} reached. Returning..'.format(max_depth)
        return False

    # Start with reduction
    result = reduce_grid(grid)
    if not result:
        return False

    grid = result

    # Pick the cell with minimum possibilities. Pick first possibility and
    # solve it. If it doesn't work, backtrack and pick the next possibility
    # min_ndx = min( ((k,v) for k,v in grid.items() if len(v) > 1), \
    #                key=lambda x: len(x[1]) )[0]
    min_cell = None

    for cell in range(0, 81):
        possibilities = len(grid[cell])
        if possibilities > 1:
            if not min_cell or possibilities < len(grid[min_cell]):
                min_cell = cell

    if not min_cell:
        return grid

    # Pick one of the possibilities of min ndx and ensure we don't create an
    # invalid state by assigning this value.
    possibilities = list(grid[min_cell])

    if randomize_traversal:
        random.shuffle(possibilities)

    for p in possibilities:
        recurse_grid = grid.copy()
        recurse_grid[min_cell] = {p}

        results = search(recurse_grid, randomize_traversal, depth+1)

        if results:
            # If we reach here, we have a successful assignment
            return results

    return False


def solve(sudoku, randomize_traversal=False):
    """
    Solve sudoku!

    sudoku: 81-character string representing input sudoku

    Returns an 81-character solution for the input sudoku.
    Raises InvalidSudokuError if input is invalid.
    """
    validate(sudoku)

    grid = str_to_grid(sudoku, fill_possibilities=True)
    return grid_to_str(search(grid, randomize_traversal=randomize_traversal))


# Initialize and identify adjacents for all cells
for row in range(0, 9):
    for col in range(0, 9):
        cells_in_row = [x for x in range(row*9, row*9+9) if x != (row*9+col)]
        cells_in_col = [x for x in range(col, 81, 9) if x != (row*9+col)]
        cells_in_sq = get_square_indices(row, col)
        cells_in_sq.remove(row*9+col)
        adjacents[row*9+col] = [cells_in_row, cells_in_col, cells_in_sq]

if __name__ == '__main__':

    example = '''EXAMPLES
            python sudoku.py .1...8...3.472169...6....1....9.253..421.378..358.6....9....1...213874.9...5...2.
            python sudoku.py -p 9715..842..69...1....8.2..95.....79...76.83...28.....57..1.5....4...91..819..7254
            python sudoku.py -i easy_10_sudoku.txt
            python sudoku.py -df -i easy_10_sudoku.txt > solution_output.txt
              '''
    parser = argparse.ArgumentParser(description='Sudoku solver',
                                     epilog=example,
                                     formatter_class=argparse.RawDescriptionHelpFormatter)
    group = parser.add_mutually_exclusive_group(required=True)
    group.add_argument('-i', '--input',
                       help='Input text file containing 81 char sudoku string, \
                             one per line')
    group.add_argument('puzzle', type=str, nargs='?',
                       help="81 character string representing sudoku")

    p_group = parser.add_mutually_exclusive_group()
    p_group.add_argument('-ns', '--nostat', action='store_true',
                         help='Do not print solver\'s statistics')
    p_group.add_argument('-p', '--prettyprint', action='store_true',
                         help='Pretty print sudoku and its solution in 2D')
    p_group.add_argument('-df', '--dfprint', action='store_true',
                         help='Print sudoku and its solution in dataframe-friendly \
                            format. Headers included')

    parser.add_argument('-r', '--randomize', action='store_true',
                        help='Randomize tree traversal when solving. For fun!')

    args = parser.parse_args()

    puzzles = []

    if args.puzzle:
        puzzles.append(args.puzzle)
    else:
        with open(args.input, 'rb') as sudoku_input:
            puzzles = sudoku_input.readlines()

    header_printed = False

    for ndx, sudoku in enumerate(puzzles):
        sudoku = sudoku.strip()

        if sudoku.startswith('#'):
            continue

        start = time.time()
        solution = solve(sudoku, args.randomize)
        end = time.time()

        if is_solved(solution):
            # We have a solution. Decide how to display solution
            if args.prettyprint:
                print display(sudoku, "Input #" + str(ndx+1))
                print display(solution, "Solution")
            elif args.dfprint:
                if not header_printed:
                    print 'Sudoku,Solution,Computation_Time(s),Max_Search_Depth'
                    header_printed = True

                print '{0},{1},{2:.3f},{3}'.format(sudoku, solution,
                                                   end-start, max_depth)
            else:
                print sudoku
                print '>', solution
            if not args.dfprint and not args.nostat:
                print '>>Solved in {0:.3f}s with max depth {1}' \
                      .format(end-start, max_depth)
            max_depth = 0
        elif not solution:
            if args.prettyprint:
                print display(sudoku)
        else:
            # Will we ever reach here?
            print '\tHmm...Can\'t solve this puzzle'
            print display(solution, 'Unsolved state')
