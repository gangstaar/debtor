import budget.io as bio
import budget.types as b
from budget.io import is_budget_exists
from flask import Flask, render_template, g, request, session, redirect, url_for
from views.budget import bp as editbudget
from views.spending import bp as editspending
import os


app = Flask(__name__, static_url_path='/debtor/static')
app.config.from_mapping(SECRET_KEY='deva')
app.register_blueprint(editbudget, url_prefix='/debtor/budget')
app.register_blueprint(editspending, url_prefix='/debtor/budget/spending')


@app.before_request
def load_budgets():
    g.saved_budgets = bio.get_available_budgets('./saved_budgets')


@app.route('/debtor/', methods=['POST', 'GET'])
def main():
    session.clear()

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
            bio.save_budget(b.TBudget(), './saved_budgets/' + budget_file_name)
            session['budget_file'] = budget_file_name
            return redirect(url_for('budget.edit'))

    return render_template('index.html')


@app.route('/debtor/test-budget')
def print_test_budget():
    return str(bio.get_report_html(bio.get_test_budget(), False))


@app.route('/debtor/edit=<budget_file>')
def edit_budget(budget_file=None):
    if (budget_file is None) or (not is_budget_exists(budget_file)):
        return redirect(url_for('main'))

    session['budget_file'] = budget_file

    return redirect(url_for('budget.edit'))


@app.route('/debtor/print=<budget_file>')
def print_budget(budget_file=None):
    if (budget_file is None) or (not is_budget_exists(budget_file)):
        return redirect(url_for('main'))

    budget = bio.load_budget('./saved_budgets/' + budget_file)
    g.budget_file = budget_file

    return render_template('report.html', budget=budget, budget_file=budget_file)


@app.route('/debtor/copy=<budget_file>')
def copy_budget(budget_file=None):
    if (budget_file is not None) and (is_budget_exists(budget_file)):
        budget = bio.load_budget('./saved_budgets/' + budget_file)
        bio.save_budget(budget, './saved_budgets/' + budget_file[:-4] + ' - copy')

    return redirect(url_for('main'))


@app.route('/debtor/delete-budget=<budget_file>', methods=['POST', 'GET'])
def delete_budget(budget_file=None):
    if (budget_file is not None) and (is_budget_exists(budget_file)):
        os.remove('./saved_budgets/' + budget_file)

    return redirect(url_for('main'))
