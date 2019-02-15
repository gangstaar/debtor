import budget.io as bio
import budget.types as b
from budget.io import is_budget_exists
from flask import render_template, Blueprint, g, request, session, redirect, url_for
from datetime import datetime as dt

bp = Blueprint('spending', __name__)


@bp.before_request
def load():
    g.saved_budgets = bio.get_available_budgets('./saved_budgets')

    budget_file = session['budget_file']
    if (budget_file is None) or (not is_budget_exists(budget_file)):
        return redirect(url_for('main'))

    spending_index = session['spending_index']
    if spending_index is None:
        return redirect(url_for('main'))

    g.budget_file = budget_file
    g.budget = bio.load_budget('./saved_budgets/' + budget_file)
    g.spending_index = spending_index


@bp.route('/edit')
def edit():
    return render_template('editspending.html', budget=g.budget, budget_file=g.budget_file,
                           spending=g.budget.current_spending,
                           index=g.spending_index)


@bp.route('/remove-person=<consumer_number>', methods=['POST'])
def remove_person(consumer_number=0):
    index = int(consumer_number)
    if index < len(g.budget.current_spending.consumers_list):
        g.budget.current_spending.consumers_list.pop(index)

    bio.save_budget(g.budget, './saved_budgets/' + g.budget_file)
    return redirect(url_for('spending.edit'))


@bp.route('/add-person', methods=['POST'])
def add_person():
    if request.form.get('addAll') is not None:
        g.budget.current_spending.add_consumer(g.budget.persons_list, 0)
        bio.save_budget(g.budget, './saved_budgets/' + g.budget_file)

    if (request.form['name'] is not None) and (request.form['amount'] is not None):
        person = g.budget.get_person_by_name(request.form['name'])
        if person is not None:
            g.budget.current_spending.add_consumer(person, float(request.form['amount']))
            bio.save_budget(g.budget, './saved_budgets/' + g.budget_file)

    return redirect(url_for('spending.edit'))


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
        datetime = datetime.strptime(date, b.TSpending.get_date_format_s())
    except Exception:
        return 'Неверная дата!'

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

    bio.save_budget(g.budget, './saved_budgets/' + g.budget_file)
    return redirect(url_for('spending.edit'))


@bp.route('/calc', methods=['POST'])
def calc():
    if request.form.get('aver') is not None:
        g.budget.current_spending.calc_average()
    if request.form.get('weighted') is not None:
        g.budget.current_spending.calc_weighted()

    bio.save_budget(g.budget, './saved_budgets/' + g.budget_file)
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
        bio.save_budget(g.budget, './saved_budgets/' + g.budget_file)

    if request.form.get('cancel') is not None:
        g.budget.current_spending = None

    return redirect(url_for('budget.edit'))