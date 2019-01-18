import unittest
import sudoku
from sudoku import InvalidSudokuError

class SudokuTest(unittest.TestCase):

    def test_empty_str(self):
        self.assertRaises(InvalidSudokuError, sudoku.solve, '')
        self.assertRaisesRegexp(InvalidSudokuError, 'Input length is .* 81 characters',\
                                sudoku.solve, '')

    def test_is_str(self):
        self.assertRaisesRegexp(InvalidSudokuError, 'Input must be .*81-character string', sudoku.solve, 1)

    def test_none_input(self):
        self.assertRaisesRegexp(InvalidSudokuError, 'Input must be .*81-character string', sudoku.solve, None)
    
    def test_less_81_char(self):
        bad_input  = '.1...8...3.472169...6....1....9.253..421.378..358.6....9....1...213874.9...5...2'
        self.assertRaisesRegexp(InvalidSudokuError, 'Input length is 80.*81 characters',\
                                sudoku.solve, bad_input)
        
    def test_more_81_char(self):
        bad_input  = '.1...8...3.472169...6....1....9.253..421.378..358.6....9....1...213874.9...5...2..'
        self.assertRaisesRegexp(InvalidSudokuError, 'Input length is 82.*81 characters',\
                                sudoku.solve, bad_input)

    def test_eq_81_char(self):
        good_input = '.1...8...3.472169...6....1....9.253..421.378..358.6....9....1...213874.9...5...2.' 
        expected_sol = '719638254354721698286495317678942531942153786135876942893264175521387469467519823'
        self.assertEqual(expected_sol, sudoku.solve(good_input))

    def test_blank_sudoku(self):
        # Blank sudoku will have 81 '.'
        sol = sudoku.solve(''.join('.' for x in range(0,81)))
        self.assertTrue(sudoku.is_solved(sol) )

    def test_contradicting_row(self):
        # Test for invalid input where a number appears more than once in any sudoku row
        self.assertRaisesRegexp(InvalidSudokuError, '1 appears 2x in row 1',\
                                sudoku.solve,
                                '1..1.............................................................................')
        self.assertRaisesRegexp(InvalidSudokuError, '1 appears 2x in row 9',\
                                sudoku.solve,
                                '...............................................................................11')
        self.assertRaisesRegexp(InvalidSudokuError, '1 appears 2x in row 8',\
                                sudoku.solve,
                                '...............................................................1.......1.........')  

    def test_contradicting_col(self):
        # Test for invalid input where a number appears more than once in any sudoku col
        self.assertRaisesRegexp(InvalidSudokuError, '1 appears 2x in col 1',\
                                sudoku.solve,
                                '1........1.......................................................................')
        self.assertRaisesRegexp(InvalidSudokuError, '1 appears 2x in col 1',\
                                sudoku.solve,
                                '1.......................................................................1........')
        self.assertRaisesRegexp(InvalidSudokuError, '1 appears 2x in col 9',\
                                sudoku.solve,
                                '........1.......................................................................1')

    def test_contradicting_sq(self):
        # Test for invalid input where a number appears more than once in any sudoku sq
        self.assertRaisesRegexp(InvalidSudokuError, '9 appears 2x in a square',\
                                sudoku.solve,
                                '9.........9......................................................................')
        self.assertRaisesRegexp(InvalidSudokuError, '9 appears 2x in a square',\
                                sudoku.solve,
                                '.....................................................................9..........9')
        self.assertRaisesRegexp(InvalidSudokuError, '9 appears 2x in a square',\
                                sudoku.solve,
                                '..............................9...................9..............................')

    def test_any_char_in_blank_cell(self):
        silly_input = '.1AAA8bbb3.472169...6....1....9c253..421.378..358.6....9....1...213874.9...5...2.'
        expected_sol = '719638254354721698286495317678942531942153786135876942893264175521387469467519823'
        self.assertEqual(expected_sol, sudoku.solve(silly_input))

    def test_easy_cases(self):
        lines = []
        with open('data/easy_10_sudoku.txt', 'rb') as input_handler:
            lines = input_handler.readlines()

        for puzzle in lines:
            puzzle = puzzle.strip()
            self.assertTrue(sudoku.is_solved(sudoku.solve(puzzle)))

    def test_evil_cases(self):
        lines = []
        with open('data/evil_10_sudoku.txt', 'rb') as input_handler:
            lines = input_handler.readlines()

        for puzzle in lines:
            puzzle = puzzle.strip()
            self.assertTrue( sudoku.is_solved(sudoku.solve(puzzle)))

if __name__ == '__main__':
    unittest.main()
