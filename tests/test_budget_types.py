import unittest
import budget.types as b
import budget.io as bio


class TestBudget(unittest.TestCase):

    def setUp(self):
        self.budget = bio.get_test_budget()  # type: b.TBudget
        test_budget_full_name = 'tests/CPermDated.bdg'
        if not bio.is_budget_exists(test_budget_full_name):
            bio.save_budget(self.budget, test_budget_full_name)

    def test_just_print_test_budget(self):
        bio.print_report(self.budget)

    def test_simple_algorithm(self):
        self.budget.calc_debt_operations_list('simple')
        self.assertTrue(self.budget.is_converged())

    def test_monte_carlo_algorithm(self):
        self.budget.calc_debt_operations_list('monte-carlo')
        self.assertTrue(self.budget.is_converged())

    def test_load_budget(self):
        budget = bio.load_budget('tests/CPermDated.bdg')
        budget.calc_debt_operations_list('simple')
        self.assertTrue(budget.is_converged())
        #self.assertAlmostEqual(budget.get_positive_debt_sum(), 24389.87, 2) # с точностью до 2 знаков после запятой
        #self.assertAlmostEqual(budget.get_transaction_sum(), 24389.87, 2)

    def test_save_budget(self):
        file_full_path = 'tests/TestBudgetSaved.bdg'
        bio.save_budget(self.budget, file_full_path)
        budget = bio.load_budget(file_full_path)
        budget.calc_debt_operations_list()
        self.assertTrue(budget.is_converged())


if __name__ == '__main__':
    unittest.main()
