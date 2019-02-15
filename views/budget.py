import budget.io as bio
import budget.types as b
from budget.io import is_budget_exists
from flask import render_template, Blueprint, g, request, session, redirect, url_for
from datetime import datetime as dt
import os


bp = Blueprint('budget', __name__)


@bp.before_request
def load_budgets():
    g.saved_budgets = bio.get_available_budgets('./saved_budgets')

    budget_file = session['budget_file']
    if (budget_file is None) or (not is_budget_exists(budget_file)):
        return redirect(url_for('main'))

    g.budget_file = budget_file
    g.budget = bio.load_budget('./saved_budgets/' + budget_file)


@bp.route('/edit', methods=['GET'])
def edit():
    return render_template('edit.html', budget=g.budget, budget_file=g.budget_file)


@bp.route('/edit-file-name', methods=['POST'])
def edit_file_name():
    new_file_name = request.form.get('filename')

    if new_file_name is not None and len(new_file_name) > 0:
        if not new_file_name.endswith('.bdg'):
            new_file_name += '.bdg'
        if os.path.exists(os.path.dirname('./saved_budgets/' + new_file_name)):
            if os.path.exists('./saved_budgets/' + new_file_name):
                return 'Файл бюджета с именем "' + new_file_name + '" уже существует. Выберите другое имя.'
            os.rename('./saved_budgets/' + g.budget_file, './saved_budgets/' + new_file_name)
            session['budget_file'] = new_file_name

    return redirect(url_for('budget.edit'))


@bp.route('/remove-person=<person_name>', methods=['POST'])
def remove_person(person_name=None):
    if person_name is not None:
        g.budget.spending_list.clear()
        g.budget.debt_operations_list.clear()
        g.budget.persons_list.remove(g.budget.get_person_by_name(person_name))
        bio.save_budget(g.budget, './saved_budgets/' + g.budget_file)

    return redirect(url_for('budget.edit'))


@bp.route('/add-person', methods=['POST'])
def add_person():
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

    g.budget.spending_list.clear()
    g.budget.debt_operations_list.clear()
    if g.budget.is_participant(person_name):
        return 'Участник с таким именем уже есть в бюджете!'

    g.budget.persons_list.append(b.TPerson(person_name, person_weight, pays_for_name))
    bio.save_budget(g.budget, './saved_budgets/' + g.budget_file)

    return redirect(url_for('budget.edit'))


@bp.route('/edit-memo', methods=['POST'])
def edit_memo():
    memo = request.form['memo']
    g.budget.memo = memo
    bio.save_budget(g.budget, './saved_budgets/' + g.budget_file)

    return redirect(url_for('budget.edit'))


@bp.route('/calculate', methods=['POST'])
def calculate():
    if request.form.get('simple') is not None:
        g.budget.calc_debt_operations_list('simple')

    if request.form.get('monte-carlo') is not None:
        g.budget.calc_debt_operations_list('monte-carlo')

    bio.save_budget(g.budget, './saved_budgets/' + g.budget_file)
    return redirect(url_for('budget.edit'))


@bp.route('/add-spending', methods=['POST'])
def add_spending():
    g.budget.current_spending = b.TSpending(b.TPerson(''), '', 0)
    g.budget.current_spending.date_time = dt.now()

    session['spending_index'] = -1

    bio.save_budget(g.budget, './saved_budgets/' + g.budget_file)
    return redirect(url_for('spending.edit'))


@bp.route('/edit_spending=<spending_number>', methods=['POST'])
def edit_spending(spending_number='0'):
    index = int(spending_number)
    if index < len(g.budget.spending_list):
        if request.form.get('deletespending.x') is not None:
            g.budget.spending_list.pop(index)
            g.budget.calc_debt_operations_list()
            bio.save_budget(g.budget, './saved_budgets/' + g.budget_file)

        if request.form.get('editspending.x') is not None:
            g.budget.current_spending = g.budget.spending_list[index]
            bio.save_budget(g.budget, './saved_budgets/' + g.budget_file)
            session['spending_index'] = index
            return redirect(url_for('spending.edit'))

    return redirect(url_for('budget.edit'))
