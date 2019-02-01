import budget.io as bio
import budget.types as b
from flask import render_template, Blueprint, g, request
import os


bp = Blueprint('budget', __name__)


def is_budget_exists(budget_name):
    saved_budgets = bio.get_available_budgets('./saved_budgets')
    if budget_name in saved_budgets:
        return True
    else:
        return False


@bp.before_request
def load_saved_budgets():
    g.saved_budgets = bio.get_available_budgets('./saved_budgets')


@bp.route('/edit=<budget_file>')
def edit_budget(budget_file=None):
    budget = None
    if is_budget_exists(budget_file):
        budget = bio.load_budget('./saved_budgets/' + budget_file)
    if budget is None:
        return 'Не найден файл бюджета' + budget_file

    return render_template('edit.html', budget=budget, budget_file=budget_file)


@bp.route('/print=<budget_file>')
def print_budget(budget_file=None):
    if is_budget_exists(budget_file):
        budget = bio.load_budget('./saved_budgets/' + budget_file)
        return render_template('report.html', budget=budget, budget_file=budget_file)

    return 'Бюджет "' + budget_file + '" не найден.'


@bp.route('/delete=<budget_file>')
def delete_budget(budget_file=None):
    return render_template('deletebudgetdialog.html', budget_file=budget_file)


@bp.route('/copy=<budget_file>')
def copy_budget(budget_file=None):
    if is_budget_exists(budget_file):
        budget = bio.load_budget('./saved_budgets/' + budget_file)
        bio.save_budget(budget, './saved_budgets/' + budget_file[:-4] + ' - copy')

    g.saved_budgets = bio.get_available_budgets('./saved_budgets')
    return render_template('index.html')


@bp.route('/edit_file_name=<budget_file>', methods=['POST'])
def edit_budget_file_name(budget_file=None):
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


@bp.route('/delete=<budget_file>/dialog', methods=['POST'])
def delete_budget_ok(budget_file=None):
    if request.form.get('ok') is not None:
        if is_budget_exists(budget_file):
            os.remove('./saved_budgets/' + budget_file)
            g.saved_budgets = bio.get_available_budgets('./saved_budgets')

    return render_template('index.html')


@bp.route('/budget=<budget_file>/remove_person=<person_name>', methods=['POST'])
def edit_budget_remove_person(budget_file=None, person_name=None):
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


@bp.route('/budget=<budget_file>/add_person', methods=['POST'])
def edit_budget_add_person(budget_file=None):
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


@bp.route('/edit_memo=<budget_file>', methods=['POST'])
def edit_budget_edit_memo(budget_file=None):
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


@bp.route('/calculate=<budget_file>', methods=['POST'])
def edit_budget_calculate(budget_file=None):
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
