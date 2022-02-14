import os

from flask import Flask, render_template, g, request, session, redirect, url_for

from budget.io import get_available_budgets, load_budget, save_budget, get_report_html, get_test_budget, is_budget_exists
from budget.types import TBudget

from views.budget import bp as bp_edit_budget
from views.spending import bp as bp_edit_spending
from views.auth import bp as auth
from views.auth import required_login, is_someone_logged_in, get_current_user_path
from auth_utils import user_data_path


app = Flask(__name__, static_url_path='/debtor/static')
app.config.from_mapping(SECRET_KEY='deva')
app.register_blueprint(bp_edit_budget, url_prefix='/debtor/budget')
app.register_blueprint(bp_edit_spending, url_prefix='/debtor/budget/spending')
app.register_blueprint(auth, url_prefix='/debtor/auth')


if not os.path.exists(user_data_path):
    os.mkdir(user_data_path)


@app.before_request
def load_budgets():
    if is_someone_logged_in():
        g.saved_budgets = get_available_budgets(get_current_user_path(), 1)
    else:
        g.saved_budgets = []


@app.route('/debtor/', methods=['POST', 'GET'])
def main():
    if 'budget_file' in session:
        session.pop('budget_file')

    g.budget_file = ''

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
            budget_path = get_current_user_path()
            budget_name = budget_file_name
            save_budget(TBudget(), budget_path + budget_name)
            session['budget_file'] = budget_name
            return redirect(url_for('budget.edit'))

    return render_template('index.html')


@app.route('/debtor/test-budget')
def print_test_budget():
    return str(get_report_html(get_test_budget(), False))


@app.route('/debtor/edit=<budget_file>')
@required_login
def edit_budget(budget_file=None):
    if budget_file is None:
        return redirect(url_for('main'))

    session['budget_file'] = budget_file

    return redirect(url_for('budget.edit'))


@app.route('/debtor/print=<budget_file>')
@required_login
def print_budget(budget_file=None):
    if (budget_file is None) or (not is_budget_exists(get_current_user_path() + budget_file)):
        return redirect(url_for('main'))

    budget = load_budget(get_current_user_path() + budget_file)
    g.budget_file = budget_file

    return render_template('report.html', budget=budget, budget_file=budget_file)


@app.route('/debtor/copy=<budget_file>')
@required_login
def copy_budget(budget_file=None):
    if (budget_file is not None) and (is_budget_exists(get_current_user_path() + budget_file)):
        budget = load_budget(get_current_user_path() + budget_file)
        new_budget_file = budget_file[:-4] + ' - copy.bdg'
        save_budget(budget, get_current_user_path() + new_budget_file)
        session['budget_file'] = new_budget_file
        return redirect(url_for('budget.edit'))

    return redirect(url_for('main'))


@app.route('/debtor/delete-budget=<budget_file>', methods=['POST', 'GET'])
@required_login
def delete_budget(budget_file=None):
    if (budget_file is not None) and (is_budget_exists(get_current_user_path() + budget_file)):
        os.remove(get_current_user_path() + budget_file)

    return redirect(url_for('main'))


@app.route('/debtor/about')
def about():
    return render_template('about.html')
