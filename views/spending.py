from datetime import datetime as dt

from flask import render_template, Blueprint, g, request, session, redirect, url_for

from budget.io import get_available_budgets
from budget.types import TSpending
from views.auth import required_login, get_current_user_path
from views.budget import required_budget_file, save_current_budget, load_current_budget

bp = Blueprint('spending', __name__)


@bp.before_request
@required_login
@required_budget_file
def load():
    g.saved_budgets = get_available_budgets(get_current_user_path())

    if 'spending_index' not in session:
        return redirect(url_for('main'))

    spending_index = session['spending_index']

    load_current_budget()
    g.spending_index = spending_index


@bp.route('/edit')
def edit():
    return render_template('editspending.html', budget=g.budget, budget_file=g.budget_file,
                           spending=g.budget.current_spending,
                           index=g.spending_index, consumer=None)


@bp.route('/remove-person=<consumer_number>', methods=['POST'])
def remove_person(consumer_number=0):
    index = int(consumer_number)
    if index < len(g.budget.current_spending.consumers_list):
        g.budget.current_spending.consumers_list.pop(index)

    save_current_budget()
    return redirect(url_for('spending.edit'))


@bp.route('/add-person', methods=['POST'])
def add_person():
    if request.form.get('addAll') is not None:
        g.budget.current_spending.add_consumer(g.budget.persons_list, 0)
        save_current_budget()

    if (request.form['name'] is not None) and (request.form['amount'] is not None):
        name = request.form['name']

        if name == 'Добавить всех':
            g.budget.current_spending.add_consumer(g.budget.persons_list, 0)
        else:
            person = g.budget.get_person_by_name(name)
            if person is not None:
                g.budget.current_spending.add_consumer(person, float(request.form['amount']))

        save_current_budget()

    return redirect(url_for('spending.edit'))


@bp.route('/edit-person=<consumer_number>', methods=['POST'])
def edit_person(consumer_number=0):
    index = int(consumer_number)
    if index < len(g.budget.current_spending.consumers_list):
        consumer = g.budget.current_spending.consumers_list.pop(index)

    save_current_budget()
    return render_template('editspending.html', budget=g.budget, budget_file=g.budget_file,
                           spending=g.budget.current_spending,
                           index=g.spending_index, consumer=consumer)


@bp.route('/edit-head', methods=['POST'])
def edit_head():
    amount = request.form['spendingamount']
    memo = request.form['spendingmemo']
    payer = request.form['spendingpayer']
    date = request.form['spendingdate']

    if (amount is None) or (memo is None) or (payer is None) or (date is None):
        return 'Неверный запрос'

    if not amount.replace('.', '1').isdigit():
        return 'В поле "Сумма" должно быть число!'

    datetime = dt.now()

    try:
        datetime = datetime.strptime(date, TSpending.get_date_format_s())
    except Exception:
        return 'Неверная дата! Пожалуйста, введите дату в формате ДД.ММ.ГГГГ'

    g.budget.current_spending.amount = float(amount)
    g.budget.current_spending.memo = memo
    g.budget.current_spending.date_time = datetime

    if g.budget.current_spending.amount <= 0:
        return 'Сумма траты должна быть больше 0!'

    if not g.budget.is_participant(payer):
        return 'Оплачивать трату может только участник бюджета!'

    person = g.budget.get_person_by_name(payer)
    if person is not None:
        g.budget.current_spending.payer = person

    save_current_budget()
    return redirect(url_for('spending.edit'))


@bp.route('/calc', methods=['POST'])
def calc():
    if request.form.get('aver') is not None:
        g.budget.current_spending.calc_average()
    if request.form.get('weighted') is not None:
        g.budget.current_spending.calc_weighted()

    save_current_budget()
    return redirect(url_for('spending.edit'))


@bp.route('/submit=<index>', methods=['POST'])
def submit(index='-1'):
    index = int(index)

    if request.form.get('ok') is not None:
        if index > -1:
            g.budget.spending_list.pop(index)

        g.budget.add_spending(g.budget.current_spending)
        g.budget.current_spending = None
        g.budget.calc_debt_operations_list()
        save_current_budget()

    if request.form.get('cancel') is not None:
        g.budget.current_spending = None

    return redirect(url_for('budget.edit'))
