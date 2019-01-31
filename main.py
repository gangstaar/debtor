import budget.io as bio
import budget.types as b
from flask import Flask, render_template, g, request, flash
import os


# budget = bio.get_test_budget()
# bio.print_report(budget)

app = Flask(__name__)
app.config.from_mapping(SECRET_KEY='deva')
app.current_spending = None
app.static_folder = './static/debtor'


def is_budget_exists(budget_name):
    saved_budgets = bio.get_available_budgets('./saved_budgets')
    if budget_name in saved_budgets:
        return True
    else:
        return False


@app.route('/debtor', methods=['POST', 'GET'])
def main():
    g.saved_budgets = bio.get_available_budgets('./saved_budgets')
    if request.method == 'POST':
        error = None
        budget_file_name = request.form['budgetname']
        if not budget_file_name.endswith('.bdg'):
            budget_file_name += '.bdg'

        if not budget_file_name:
            error = 'Необходимо ввести имя бюджета.'

        if budget_file_name in g.saved_budgets:
            error = 'Бюджет с таким именем уже существует.'

        if error is None:
            bio.save_budget(b.TBudget(), './saved_budgets/' + budget_file_name)
            g.saved_budgets = bio.get_available_budgets('./saved_budgets')
            return render_template('index.html')

        flash(error)

    return render_template('index.html')


@app.route('/debtor/test_budget')
def print_test_budget():
    return str(bio.get_report_html(bio.get_test_budget(), False))


@app.route('/debtor/print_budget=<budget_file>')
def print_budget(budget_file=None):
    g.saved_budgets = bio.get_available_budgets('./saved_budgets')
    if is_budget_exists(budget_file):
        budget = bio.load_budget('./saved_budgets/' + budget_file)
        return render_template('report.html', budget=budget, budget_file=budget_file)

    return 'Бюджет "' + budget_file + '" не найден.'


@app.route('/debtor/edit_budget=<budget_file>')
def edit_budget(budget_file=None):
    g.saved_budgets = bio.get_available_budgets('./saved_budgets')
    budget = None
    if is_budget_exists(budget_file):
        budget = bio.load_budget('./saved_budgets/' + budget_file)
    if budget is None:
        return 'Не найден файл бюджета' + budget_file

    return render_template('edit.html', budget=budget, budget_file=budget_file)


@app.route('/debtor/delete_budget=<budget_file>')
def delete_budget(budget_file=None):
    g.saved_budgets = bio.get_available_budgets('./saved_budgets')
    return render_template('deletebudgetdialog.html', budget_file=budget_file)


@app.route('/debtor/copy_budget=<budget_file>')
def copy_budget(budget_file=None):
    g.saved_budgets = bio.get_available_budgets('./saved_budgets')
    if is_budget_exists(budget_file):
        budget = bio.load_budget('./saved_budgets/' + budget_file)
        bio.save_budget(budget, './saved_budgets/' + budget_file[:-4] + ' - copy')

    g.saved_budgets = bio.get_available_budgets('./saved_budgets')
    return render_template('index.html')


@app.route('/debtor/edit_budget=<budget_file>/edit_file_name', methods=['POST'])
def edit_budget_file_name(budget_file=None):
    g.saved_budgets = bio.get_available_budgets('./saved_budgets')
    if is_budget_exists(budget_file):
        budget = bio.load_budget('./saved_budgets/' + budget_file)
        new_file_name = request.form.get('filename')
        if new_file_name is not None and len(new_file_name) > 0:
            if not new_file_name.endswith('.bdg'):
                new_file_name += '.bdg'
            if os.path.exists(os.path.dirname('./saved_budgets/' + new_file_name)):
                os.rename('./saved_budgets/' + budget_file, './saved_budgets/' + new_file_name)
                budget = bio.load_budget('./saved_budgets/' + new_file_name)
                g.saved_budgets = bio.get_available_budgets('./saved_budgets')
                return render_template('edit.html', budget=budget, budget_file=new_file_name)

    return render_template('edit.html', budget=budget, budget_file=budget_file)


@app.route('/debtor/delete_budget=<budget_file>/dialog', methods=['POST'])
def delete_budget_ok(budget_file=None):
    g.saved_budgets = bio.get_available_budgets('./saved_budgets')
    if request.form.get('ok') is not None:
        if is_budget_exists(budget_file):
            os.remove('./saved_budgets/' + budget_file)
            g.saved_budgets = bio.get_available_budgets('./saved_budgets')

    return render_template('index.html')


@app.route('/debtor/edit_budget=<budget_file>/remove_person=<person_name>', methods=['POST'])
def edit_budget_remove_person(budget_file=None, person_name=None):
    g.saved_budgets = bio.get_available_budgets('./saved_budgets')
    budget = None
    if is_budget_exists(budget_file):
        budget = bio.load_budget('./saved_budgets/' + budget_file)
    if budget is None:
        return 'Не найден файл бюджета' + budget_file

    if person_name is not None:
        budget.spending_list.clear()
        budget.debt_operations_list.clear()
        budget.persons_list.remove(budget.get_person_by_name(person_name))
        bio.save_budget(budget, './saved_budgets/' + budget_file)

    return render_template('edit.html', budget=budget, budget_file=budget_file)


@app.route('/debtor/edit_budget=<budget_file>/add_person', methods=['POST'])
def edit_budget_add_person(budget_file=None):
    g.saved_budgets = bio.get_available_budgets('./saved_budgets')
    budget = None
    if is_budget_exists(budget_file):
        budget = bio.load_budget('./saved_budgets/' + budget_file)
    if budget is None:
        return 'Не найден файл бюджета' + budget_file

    if request.method == 'POST':
        person_name = request.form['name']
        person_weight = request.form['weight']
        pays_for_name = request.form['paysfor']

        if (person_name is None) or (person_weight is None) or (pays_for_name is None):
            return 'Не заполнено(ы) поле(я) для добавления участника.'

        if (person_name.isspace()) or (person_weight.isspace()):
            return 'Не заполнено(ы) поле(я) для добавления участника.'

        if (person_name.__len__() == 0) or (person_weight.__len__() == 0):
            return 'Не заполнено(ы) поле(я) для добавления участника.'

        if not person_weight.replace('.', '1').isdigit():
            return 'В поле "Вес" должно быть число!'

        person_weight = float(person_weight)

        budget.spending_list.clear()
        budget.debt_operations_list.clear()
        if budget.is_participant(person_name):
            return 'Участник с таким именем уже есть в бюджете!'

        budget.persons_list.append(b.TPerson(person_name, person_weight, pays_for_name))
        bio.save_budget(budget, './saved_budgets/' + budget_file)

        return render_template('edit.html', budget=budget, budget_file=budget_file)


@app.route('/debtor/edit_budget=<budget_file>/edit_memo', methods=['POST'])
def edit_budget_edit_memo(budget_file=None):
    g.saved_budgets = bio.get_available_budgets('./saved_budgets')
    budget = None
    if is_budget_exists(budget_file):
        budget = bio.load_budget('./saved_budgets/' + budget_file)
    if budget is None:
        return 'Не найден файл бюджета' + budget_file

    if request.method == 'POST':
        memo = request.form['memo']
        budget.memo = memo
        bio.save_budget(budget, './saved_budgets/' + budget_file)

        return render_template('edit.html', budget=budget, budget_file=budget_file)


@app.route('/debtor/edit_budget=<budget_file>/add_spending', methods=['POST'])
def edit_budget_add_spending(budget_file=None):
    g.saved_budgets = bio.get_available_budgets('./saved_budgets')
    budget = None
    if is_budget_exists(budget_file):
        budget = bio.load_budget('./saved_budgets/' + budget_file)
    if budget is None:
        return 'Не найден файл бюджета' + budget_file

    app.current_spending = b.TSpending('', b.TPerson(''), 0)

    return render_template('editspending.html',  budget=budget, budget_file=budget_file, spending=app.current_spending)


@app.route('/debtor/edit_budget=<budget_file>/edit_spending=<spending_number>', methods=['POST'])
def edit_budget_edit_spending(budget_file=None, spending_number='0'):
    g.saved_budgets = bio.get_available_budgets('./saved_budgets')
    budget = None
    if is_budget_exists(budget_file):
        budget = bio.load_budget('./saved_budgets/' + budget_file)
    if budget is None:
        return 'Не найден файл бюджета' + budget_file

    index = int(spending_number)
    if index < len(budget.spending_list):
        if request.form.get('deletespending.x') is not None:
            budget.spending_list.pop(index)
            budget.calc_debt_operations_list()
            bio.save_budget(budget, './saved_budgets/' + budget_file)

        if request.form.get('editspending.x') is not None:
            app.current_spending = budget.spending_list.pop(index)
            budget.calc_debt_operations_list()
            bio.save_budget(budget, './saved_budgets/' + budget_file)
            return render_template('editspending.html', budget=budget, budget_file=budget_file, spending=app.current_spending)

    return render_template('edit.html', budget=budget, budget_file=budget_file)


@app.route('/debtor/edit_budget=<budget_file>/calculate', methods=['POST'])
def edit_budget_calculate(budget_file=None):
    g.saved_budgets = bio.get_available_budgets('./saved_budgets')
    budget = None
    if is_budget_exists(budget_file):
        budget = bio.load_budget('./saved_budgets/' + budget_file)
    if budget is None:
        return 'Не найден файл бюджета' + budget_file

    if request.form.get('simple') is not None:
        budget.calc_debt_operations_list('simple')
        bio.save_budget(budget, './saved_budgets/' + budget_file)

    if request.form.get('monte-carlo') is not None:
        budget.calc_debt_operations_list('monte-carlo')
        bio.save_budget(budget, './saved_budgets/' + budget_file)

    return render_template('edit.html', budget=budget, budget_file=budget_file)


@app.route('/debtor/edit_budget=<budget_file>/edit_spending/remove_person=<consumer_number>', methods=['POST'])
def edit_spending_remove_person(budget_file=None, consumer_number=0):
    g.saved_budgets = bio.get_available_budgets('./saved_budgets')
    budget = None
    if is_budget_exists(budget_file):
        budget = bio.load_budget('./saved_budgets/' + budget_file)
    if budget is None:
        return 'Не найден файл бюджета' + budget_file

    if app.current_spending is None:
        return 'Потеряна текущая трата. Вернитесь на главную страницу.'

    if request.method == 'POST':
        index = int(consumer_number)
        if index < len(app.current_spending.consumers_list):
            app.current_spending.consumers_list.pop(index)

        return render_template('editspending.html', budget=budget, budget_file=budget_file, spending=app.current_spending)

    return 'Ошибка'


@app.route('/debtor/edit_budget=<budget_file>/edit_spending/add_person', methods=['POST'])
def edit_spending_add_person(budget_file=None):
    g.saved_budgets = bio.get_available_budgets('./saved_budgets')
    budget = None
    if is_budget_exists(budget_file):
        budget = bio.load_budget('./saved_budgets/' + budget_file)
    if budget is None:
        return 'Не найден файл бюджета' + budget_file

    if app.current_spending is None:
        return 'Потеряна текущая трата. Вернитесь на главную страницу.'

    if request.method == 'POST':
        if (request.form['name'] is not None) and (request.form['amount'] is not None):
            person = budget.get_person_by_name(request.form['name'])
            if person is not None:
                app.current_spending.add_consumer(person, float(request.form['amount']))
                return render_template('editspending.html',  budget=budget, budget_file=budget_file, spending=app.current_spending)

    return 'Ошибка'


# @app.route('/debtor/edit_budget=<budget_file>/edit_spending/edit_sum', methods=['POST'])
# def edit_spending_edit_sum(budget_file=None):
#     g.saved_budgets = bio.get_available_budgets('./saved_budgets')
#     budget = None
#     if is_budget_exists(budget_file):
#         budget = bio.load_budget('./saved_budgets/' + budget_file)
#     if budget is None:
#         return 'Не найден файл бюджета' + budget_file
#
#     if app.current_spending is None:
#         return 'Потеряна текущая трата. Вернитесь на главную страницу.'
#
#     if request.method == 'POST':
#         app.current_spending.amount = float(request.form['spendingamount'])
#         return render_template('editspending.html', budget=budget, budget_file=budget_file,
#                                spending=app.current_spending)
#     return 'Ошибка'
#
#
# @app.route('/debtor/edit_budget=<budget_file>/edit_spending/edit_memo', methods = ['POST'])
# def edit_spending_edit_memo(budget_file=None):
#     g.saved_budgets = bio.get_available_budgets('./saved_budgets')
#     budget = None
#     if is_budget_exists(budget_file):
#         budget = bio.load_budget('./saved_budgets/' + budget_file)
#     if budget is None:
#         return 'Не найден файл бюджета' + budget_file
#
#     if app.current_spending is None:
#         return 'Потеряна текущая трата. Вернитесь на главную страницу.'
#
#     if request.method == 'POST':
#         app.current_spending.memo = request.form['spendingmemo']
#         return render_template('editspending.html', budget=budget, budget_file=budget_file,
#                                spending=app.current_spending)
#
#     return 'Ошибка'
#
#
# @app.route('/debtor/edit_budget=<budget_file>/edit_spending/edit_payer', methods = ['POST'])
# def edit_spending_edit_payer(budget_file=None):
#     g.saved_budgets = bio.get_available_budgets('./saved_budgets')
#     budget = None
#     if is_budget_exists(budget_file):
#         budget = bio.load_budget('./saved_budgets/' + budget_file)
#     if budget is None:
#         return 'Не найден файл бюджета' + budget_file
#
#     if app.current_spending is None:
#         return 'Потеряна текущая трата. Вернитесь на главную страницу.'
#
#     if request.method == 'POST':
#         person = budget.get_person_by_name(request.form['payer'])
#         if person is not None:
#             app.current_spending.payer = person
#             return render_template('editspending.html', budget=budget, budget_file=budget_file,
#                                    spending=app.current_spending)
#
#     return 'Ошибка'


@app.route('/debtor/edit_budget=<budget_file>/edit_spending/edit_head', methods=['POST'])
def edit_spending_edit_head(budget_file=None):
    g.saved_budgets = bio.get_available_budgets('./saved_budgets')
    budget = None
    if is_budget_exists(budget_file):
        budget = bio.load_budget('./saved_budgets/' + budget_file)
    if budget is None:
        return 'Не найден файл бюджета' + budget_file

    if app.current_spending is None:
        return 'Потеряна текущая трата. Вернитесь на главную страницу.'

    if request.method == 'POST':
        amount = request.form['spendingamount']
        memo = request.form['spendingmemo']
        payer = request.form['spendingpayer']

        if (amount is None) or (memo is None) or (payer is None):
            return 'Неверный запрос'

        if not amount.replace('.', '1').isdigit():
            return 'В поле "Сумма" должно быть число!'

        app.current_spending.amount = float(amount)
        app.current_spending.memo = memo

        if not budget.is_participant(payer):
            return 'Оплачивать трату может только участник бюджета!'

        person = budget.get_person_by_name(payer)
        if person is not None:
            app.current_spending.payer = person

        return render_template('editspending.html', budget=budget, budget_file=budget_file,
                               spending=app.current_spending)

    return 'Ошибка'


@app.route('/debtor/edit_budget=<budget_file>/edit_spending/calc', methods = ['POST'])
def edit_spending_calc(budget_file=None):
    g.saved_budgets = bio.get_available_budgets('./saved_budgets')
    budget = None
    if is_budget_exists(budget_file):
        budget = bio.load_budget('./saved_budgets/' + budget_file)
    if budget is None:
        return 'Не найден файл бюджета' + budget_file

    if app.current_spending is None:
        return 'Потеряна текущая трата. Вернитесь на главную страницу.'

    if request.method == 'POST':
        if request.form.get('aver') is not None:
            app.current_spending.calc_average()
        if request.form.get('weighted') is not None:
            app.current_spending.calc_weighted()

        return render_template('editspending.html', budget=budget, budget_file=budget_file,
                               spending=app.current_spending)

    return 'Ошибка'


@app.route('/debtor/edit_budget=<budget_file>/edit_spending/ok', methods = ['POST'])
def edit_spending_ok(budget_file=None):
    g.saved_budgets = bio.get_available_budgets('./saved_budgets')
    budget = None
    if is_budget_exists(budget_file):
        budget = bio.load_budget('./saved_budgets/' + budget_file)
    if budget is None:
        return 'Не найден файл бюджета' + budget_file

    if app.current_spending is None:
        return 'Потеряна текущая трата. Вернитесь на главную страницу.'

    if request.method == 'POST':
        if request.form.get('ok') is not None:
            budget.add_spending(app.current_spending)
            budget.calc_debt_operations_list()
            bio.save_budget(budget, './saved_budgets/' + budget_file)
            return render_template('edit.html', budget=budget, budget_file=budget_file)
        if request.form.get('cancel') is not None:
            app.current_spending = None
            return render_template('edit.html', budget=budget, budget_file=budget_file)

    return 'Ошибка'
