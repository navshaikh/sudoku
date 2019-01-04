import unittest
import sudoku

class SudokuTest(unittest.TestCase):

    def test_empty_str(self):
        self.assertFalse(sudoku.solve(''))

    def test_less_81_char(self):
        self.assertFalse(sudoku.solve('.1...8...3.472169...6....1....9.253..421.378..358.6....9....1...213874.9...5...2'))

    def test_more_81_char(self):
        self.assertFalse(sudoku.solve('.1...8...3.472169...6....1....9.253..421.378..358.6....9....1...213874.9...5...2..'))

    def test_eq_81_char(self):
        sol = sudoku.solve('.1...8...3.472169...6....1....9.253..421.378..358.6....9....1...213874.9...5...2.')
        self.assertEqual('719638254354721698286495317678942531942153786135876942893264175521387469467519823', \
                        sudoku.grid_to_str(sol))

    def test_blank_sudoku(self):
        # Blank sudoku will have 81 '.'
        sol = sudoku.solve(''.join('.' for x in range(0,81)))
        self.assertTrue( sudoku.is_valid_solution(sol) )

    def test_contradicting_row(self):
        # Test for invalid input where a number appears more than once in any sudoku row
        self.assertFalse(sudoku.solve('1..1.............................................................................'))
        self.assertFalse(sudoku.solve('...............................................................................11'))
        self.assertFalse(sudoku.solve('...............................................................1.......1.........'))

    def test_contradicting_col(self):
        # Test for invalid input where a number appears more than once in any sudoku col
        self.assertFalse(sudoku.solve('1........1.......................................................................'))
        self.assertFalse(sudoku.solve('1.......................................................................1........'))
        self.assertFalse(sudoku.solve('........1.......................................................................1'))

    def test_contradicting_sq(self):
        # Test for invalid input where a number appears more than once in any sudoku sq
        self.assertFalse(sudoku.solve('9.........9......................................................................'))
        self.assertFalse(sudoku.solve('.....................................................................9..........9'))
        self.assertFalse(sudoku.solve('..............................9...................9..............................'))

    def test_any_char_in_blank_cell(self):
        sol = sudoku.solve('.1AAA8bbb3.472169...6....1....9c253..421.378..358.6....9....1...213874.9...5...2.')
        self.assertEqual('719638254354721698286495317678942531942153786135876942893264175521387469467519823', \
                        sudoku.grid_to_str(sol))

    def test_easy_cases(self):
        lines = []
        with open('data/easy_10_sudoku.txt', 'rb') as input_handler:
            lines = input_handler.readlines()

        for puzzle in lines:
            puzzle = puzzle.strip()
            self.assertTrue( sudoku.is_valid_solution(sudoku.solve(puzzle)))

    def test_evil_cases(self):
        lines = []
        with open('data/evil_10_sudoku.txt', 'rb') as input_handler:
            lines = input_handler.readlines()

        for puzzle in lines:
            puzzle = puzzle.strip()
            self.assertTrue( sudoku.is_valid_solution(sudoku.solve(puzzle)))

if __name__ == '__main__':
    unittest.main()
