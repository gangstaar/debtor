import budget.io as bio
from budget import types as t

file_name = 'saved_budgets/CPermDated'

budget = bio.get_test_budget()

print('Тестовый бюджет сошёлся:')
budget.calc_debt_operations_list('simple')
print(' по простому алгоритму: ' + budget.is_converged().__str__())
budget.calc_debt_operations_list('monte-carlo')
print(' по алгоритму Монте-Карло: ' + budget.is_converged().__str__())
bio.save_budget(budget, file_name)

budget = bio.load_budget(file_name)
print('Бюджет из файла "' + file_name + '" сошёлся:')
budget.calc_debt_operations_list('simple')
print(' по простому алгоритму: ' + budget.is_converged().__str__())
budget.calc_debt_operations_list('monte-carlo')
print(' по алгоритму Монте-Карло: ' + budget.is_converged().__str__())

sp = t.TSpending(t.TPerson())
budget.current_spending = sp

bio.save_budget(budget, file_name + 'Resaved.bdg')
