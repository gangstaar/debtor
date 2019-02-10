import budget.io as bio

file_name = 'saved_budgets/Perm.bdg'

print('Тестовый бюджет:')
budget = bio.get_test_budget()
bio.print_report(budget)

print('Бюджет из файла ' + file_name)
budget = bio.load_budget(file_name)
bio.print_report(budget)
