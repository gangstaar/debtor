from datetime import datetime as dt
from os import rename
from os.path import exists, dirname
from functools import wraps

from flask import render_template, Blueprint, g, request, session, redirect, url_for

from budget.types import TBudget, TPerson, TSpending
from budget.io import is_budget_exists, get_available_budgets, load_budget, save_budget
from views.auth import required_login, get_current_user_path


bp = Blueprint('budget', __name__)


def save_current_budget():
    save_budget(g.budget, get_current_user_path() + g.budget_file)


def load_current_budget():
    g.budget_file = session['budget_file']
    g.budget = load_budget(get_current_user_path() + g.budget_file)  # type: TBudget


def is_current_budget_exists():
    budget_file = session['budget_file']
    return is_budget_exists(get_current_user_path() + budget_file)


def required_budget_file(fun):
    @wraps(fun)
    def wrapped_fun(**kwargs):
        if 'budget_file' not in session:
            return redirect(url_for('main'))
        else:
            return fun(**kwargs)

    return wrapped_fun


@bp.before_request
@required_login
@required_budget_file
def load_budgets():
    g.saved_budgets = get_available_budgets(get_current_user_path())

    if not is_current_budget_exists():
        return redirect(url_for('main'))

    load_current_budget()


@bp.route('/edit', methods=['GET'])
def edit():
    return render_template('edit.html', budget=g.budget, budget_file=g.budget_file)


@bp.route('/edit-file-name', methods=['POST'])
def edit_file_name():
    new_file_name = request.form.get('filename')

    if new_file_name is not None and len(new_file_name) > 0:
        if not new_file_name.endswith('.bdg'):
            new_file_name += '.bdg'

        if dirname(get_current_user_path() + new_file_name) == dirname(get_current_user_path() + g.budget_file):
            if exists(get_current_user_path() + new_file_name):
                return 'Файл бюджета с именем "' + new_file_name + '" уже существует. Выберите другое имя.'
            rename(get_current_user_path() + g.budget_file, get_current_user_path() + new_file_name)
            session['budget_file'] = new_file_name

    return redirect(url_for('budget.edit'))


@bp.route('/remove-person=<person_name>', methods=['POST'])
def remove_person(person_name=None):
    if person_name is not None:
        g.budget.spending_list.clear()
        g.budget.debt_operations_list.clear()
        g.budget.persons_list.remove(g.budget.get_person_by_name(person_name))
        save_current_budget()

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

    g.budget.persons_list.append(TPerson(person_name, person_weight, pays_for_name))
    save_current_budget()

    return redirect(url_for('budget.edit'))


@bp.route('/edit-memo', methods=['POST'])
def edit_memo():
    memo = request.form['memo']
    g.budget.memo = memo
    save_current_budget()

    return redirect(url_for('budget.edit'))


@bp.route('/calculate', methods=['POST'])
def calculate():
    if request.form.get('simple') is not None:
        g.budget.calc_debt_operations_list('simple')

    if request.form.get('monte-carlo') is not None:
        g.budget.calc_debt_operations_list('monte-carlo')

    save_current_budget()
    return redirect(url_for('budget.edit'))


@bp.route('/add-spending', methods=['POST', 'GET'])
def add_spending():
    g.budget.current_spending = TSpending(TPerson(''), '', 0)
    g.budget.current_spending.date_time = dt.now()

    session['spending_index'] = -1

    save_current_budget()
    return redirect(url_for('spending.edit'))


@bp.route('/add-DOI', methods=['POST'])
def add_debt_operation_inter():
    transmitter_name = request.form['transmitterName']
    receiver_name = request.form['receiverName']
    amount = request.form['amount']

    if (transmitter_name is None) or (receiver_name is None) or (amount is None):
        return 'Не заполнено(ы) поле(я) для добавления операции.'

    if (transmitter_name.isspace()) or (receiver_name.isspace()) or (amount.isspace()):
        return 'Не заполнено(ы) поле(я) для добавления операции.'

    if (transmitter_name.__len__() == 0) or (receiver_name.__len__() == 0) or (amount.__len__() == 0):
        return 'Не заполнено(ы) поле(я) для добавления операции.'

    if not amount.replace('.', '1').isdigit():
        return 'В поле "Сумма" должно быть число!'

    amount = float(amount)

    g.budget.add_debt_operation_intermediate(receiver_name, transmitter_name, amount)
    g.budget.calc_debt_operations_list()
    save_current_budget()

    return redirect(url_for('budget.edit'))


@bp.route('/remove-DOI=<debt_operation_inter_index>', methods=['POST'])
def remove_debt_operation_inter(debt_operation_inter_index=0):
    debt_operation_inter_index = int(debt_operation_inter_index)
    if debt_operation_inter_index < len(g.budget.debt_operations_list_inter):
        g.budget.debt_operations_list_inter.pop(debt_operation_inter_index)
        g.budget.calc_debt_operations_list()
        save_current_budget()

    return redirect(url_for('budget.edit'))


@bp.route('/edit_spending=<spending_number>', methods=['POST', 'GET'])
def edit_spending(spending_number='0'):
    index = int(spending_number)
    if index >= len(g.budget.spending_list):
        return redirect(url_for('budget.edit'))

    if request.form.get('deletespending.x') is not None:
        g.budget.spending_list.pop(index)
        g.budget.calc_debt_operations_list()
        save_current_budget()
        return redirect(url_for('budget.edit'))
    else:
        g.budget.current_spending = g.budget.spending_list[index]
        save_current_budget()
        session['spending_index'] = index
        return redirect(url_for('spending.edit'))


