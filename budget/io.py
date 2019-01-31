from budget.types import TBudget
from budget.types import TPerson
from budget.types import TSpending
from budget.types import TDebtOperation
import pathlib


def get_report(budget, is_long=False):
    rep = ['В бюджете "' + budget.memo + '" участвуют: ']
    s = ''
    for p in budget.persons_list:
        s += p.name() + ' ({0:2.1f})'.format(p.weight())
        if p != budget.persons_list[-1]:
            s += ', '
    rep.append(s)
    rep.append('')

    rep.append("Зафиксировано операций на сумму " + '{0:7.2f}'.format(budget.get_spending_amount_total()) + " Р:")
    for s in budget.spending_list:
        n = s.payer.name() + ';'
        line = '    ' + '{0:8.2f}'.format(s.amount) + ' Р за ' + '{0:20s}'.format(s.memo) + ' заплатил ' + '{0:8s}'.format(n)

        names = []
        for c in s.consumers_list:
            names.append(c.who.name())

        line += ' потребляли:'
        for i in range(names.__len__()):
            n = ' ' + names[i]
            if i < names.__len__() - 1:
                n += ','
                line += '{0:8s}'.format(n)
            else:
                line += '{0:8s}'.format(n)

        rep.append(line)

    rep.append('')

    for p in budget.persons_list:
        s = budget.get_spending_amount_for_person(p)
        if s == 0.0:
            continue
        rep.append('{0:8s}'.format(p.name()) + ' всего потратил ' + "{0:5.2f}".format(s) + ' Р:')

        if is_long:
            for sp in budget.get_spending_list_for_person(p):
                rep.append('    ' + "{0:8.2f}".format(sp.amount) + ' Р на ' + '{0:20s}'.format(sp.memo))

    rep.append('')

    consume_amount = 0.0
    for p in budget.persons_list:
        c = budget.get_consumption_amount_for_person(p)
        rep.append('{0:8s}'.format(p.name()) + ' всего потребил на ' + "{0:8.2f}".format(c) + ' Р')
        consume_amount += c

        if is_long:
            for sp in budget.get_consumption_list_for_person(p):
                rep.append('    ' + "{0:8.2f}".format(sp.amount) + ' Р: ' +
                           '{0:20s}'.format(sp.memo) + ' за счёт ' + '{0:8s}'.format(sp.spending.payer.name()))

    rep.append('Сумма ' + '{:8.2f} Р'.format(consume_amount))
    rep.append('')

    pos_sum = 0
    for p in budget.persons_list:
        debt = budget.get_debt_for_person(p)
        line = '{0:8s}'.format(p.name()) + ' должен ' + "{0:8.2f}".format(debt) + ' Р'
        payer_name = budget.get_person_name_who_pays_for(p)
        if payer_name != '' and debt == 0.0:
            line += ' (платит ' + payer_name + ')'
        rep.append(line)
        if debt > 0:
            pos_sum += debt

    rep.append('Сумма общая:' + '{0:8.2f} Р.'.format(budget.get_debt_sum()) + ' Сумма долгов > 0: ' + '{0:8.2f} Р.'.format(pos_sum))

    rep.append('')
    trans_sum = 0
    for op in budget.debt_operations_list:
        rep.append('{0:8s}'.format(op.debtor.name()) + ' -отдаёт-> ' + '{0:8s}'.format(op.creditor.name()) + ' {0:8.2f}'.format(op.amount) + ' Р')
        trans_sum += op.amount
    rep.append('{0:2d}'.format(len(budget.debt_operations_list)) + ' переводов на сумму ' + '{0:8.2f} Р.'.format(trans_sum))

    return rep


def get_report_str(budget, is_long=False):
    rep = get_report(budget, is_long)
    s = ''
    for line in rep:
        s += line
        if line != rep[-1]:
            s += '\n'
    return s


def get_report_html(budget: TBudget, is_long=False):
    rep = ['В бюджете "' + budget.memo + '" участвуют: ']
    s = '<table>'
    for p in budget.persons_list:
        s += '<tr>'
        s += '<td>' + p.name() + '</td> <td>' + ' ({0:2.1f})</td>'.format(p.weight())
        s += '</tr>'
    s += '</table>'
    rep.append(s)
    rep.append('')

    rep.append("<br>Зафиксировано операций на сумму " + '{0:7.2f}'.format(budget.get_spending_amount_total()) + " Р:")
    line = '<table>'
    for s in budget.spending_list:
        n = s.payer.name() + ';'
        line += '<tr>'
        line += '<td>    </td><td>' + '{0:8.2f}'.format(s.amount) + ' Р </td><td>за ' + '{0:20s}</td><td>'.format(s.memo) + \
                ' заплатил </td><td>' + '{0:8s}</td>'.format(n)

        names = []
        for c in s.consumers_list:
            names.append(c.who.name())

        line += '<td> потребляли:</td><td>'
        for i in range(names.__len__()):
            n = ' ' + names[i]
            if i < names.__len__() - 1:
                n += ','
                line += '{0:8s}'.format(n)
            else:
                line += '{0:8s}'.format(n)
        line += '</td></tr>'

    line += '</table>'
    rep.append(line)

    line = '<br><table>'
    for p in budget.persons_list:
        s = budget.get_spending_amount_for_person(p)
        if s == 0.0:
            continue

        line += '<tr>'
        line += '<td>{0:8s}</td><td>'.format(p.name()) + ' всего потратил </td><td>' + "{0:5.2f}".format(s) + ' Р:</td>'

        if is_long:
            for sp in budget.get_spending_list_for_person(p):
                line += '<tr>'
                line += ('<td>    </td><td>' + "{0:8.2f}".format(sp.amount) + ' Р </td><td>на ' + '{0:20s}</td>'.format(sp.memo))
                line += '</tr>'
        line += '</tr>'

    line += '</table>'
    rep.append(line)

    consume_amount = 0.0
    line = '<br><table>'
    for p in budget.persons_list:
        c = budget.get_consumption_amount_for_person(p)
        line += '<tr>'
        line += '<td>{0:8s}</td><td>'.format(p.name()) + ' всего потребил на </td><td>' + "{0:8.2f}".format(c) + ' Р</td>'
        consume_amount += c

        if is_long:
            line += '<tr>'
            for sp in budget.get_consumption_list_for_person(p):
                line += '<tr>'
                line += '<td>    </td><td>' + "{0:8.2f}".format(sp.amount) + ' Р: </td><td>' + \
                           '{0:20s}</td><td>'.format(sp.memo) + ' за счёт </td><td>' + '{0:8s}</td>'.format(sp.spending.payer.name())
                line += '</tr>'
            line += '</tr>'

        line += '</tr>'

    line += '</table>'
    rep.append(line)
    rep.append('Сумма ' + '{0:8.2f} Р'.format(consume_amount))

    line = '<br><br><table>'
    for p in budget.persons_list:
        debt = budget.get_debt_for_person(p)
        line += '<tr>'
        line += '<td>{0:8s}</td><td>'.format(p.name()) + ' должен </td><td>' + "{0:8.2f}".format(debt) + ' Р</td>'
        payer_name = budget.get_person_name_who_pays_for(p)
        if payer_name != '' and debt == 0.0:
            line += '<td> (платит ' + payer_name + ')</td>'
        line += '</tr>'
    line += '</table>'
    rep.append(line)
    rep.append('Сумма общая:' + '{0:8.2f} Р.'.format(budget.get_debt_sum()) + ' Сумма долгов > 0: ' + '{0:8.2f} Р.'.format(budget.get_positive_debt_sum()))

    line = '<br><br><table>'
    for op in budget.debt_operations_list:
        line += '<tr>'
        line += '<td>{0:8s}</td><td>'.format(op.debtor.name()) + ' -отдаёт-> </td><td>' + \
                '{0:8s}</td><td>'.format(op.creditor.name()) + ' {0:8.2f}'.format(op.amount) + ' Р</td>'
        line += '</tr>'
    line += '</table>'
    rep.append(line)
    rep.append('0{:2d}'.format(len(budget.debt_operations_list)) + ' переводов на сумму ' + '{0:8.2f} Р.'.format(budget.get_transaction_sum()))

    s = ''
    for line in rep:
        s += line
        # if line != rep[-1]:
        #     s += '<br>'
    return s


def print_report(budget: TBudget, is_long=False):
    s = get_report_str(budget, is_long)

    print('\n*****   Отчёт по бюджету "' + budget.memo + '"   *****')
    print(s)
    print('*****   Конец отчёта   *****')


def save_report(budget: TBudget, file_name='report.txt', is_long=False):
    s = get_report_str(budget, is_long)
    f = open(file_name, 'w')
    f.write(s)
    f.close()


def get_test_budget():
    budget = TBudget('Пермь')
    budget.add_person(TPerson('Гошан', 1.0, 'Оля П'))
    budget.add_person(TPerson('Оля П', 0.5))
    budget.add_person(TPerson('Валёк', 1.0))
    budget.add_person(TPerson('Наташа', 0.5))
    budget.add_person(TPerson('Артём', 1.0, 'Юля'))
    budget.add_person(TPerson('Юля', 0.5))
    budget.add_person(TPerson('Алексей', 1.0))
    budget.add_person(TPerson('Лена', 0.3))
    budget.add_person(TPerson('Вадим Н', 1.0))
    budget.add_person(TPerson('Вадюха', 1.0))
    budget.add_person(TPerson('Сергей', 1.0, 'Оля К'))
    budget.add_person(TPerson('Оля К', 0.5))

    s = TSpending('Билеты в пещеру', budget.get_person_by_name("Гошан"), 8400)
    s.add_consumer(budget.persons_list)
    s.calc_weighted()
    budget.add_spending(s)

    s = TSpending('Такси', budget.get_person_by_name("Гошан"), 588)
    s.add_consumer(budget.persons_list)
    s.calc_weighted()
    budget.add_spending(s)

    s = TSpending('Автобус', budget.get_person_by_name("Гошан"), 50)
    s.add_consumer(budget.persons_list)
    s.calc_weighted()
    budget.add_spending(s)

    s = TSpending('Ашан', budget.get_person_by_name("Гошан"), 35)
    s.add_consumer(budget.persons_list)
    s.calc_weighted()
    budget.add_spending(s)

    s = TSpending('Лемончелла', budget.get_person_by_name("Гошан"), 1850)
    s.add_consumer(budget.persons_list)
    s.calc_weighted()
    budget.add_spending(s)

    s = TSpending('КХ', budget.get_person_by_name("Гошан"), 170)
    s.add_consumer(budget.persons_list)
    s.calc_weighted()
    budget.add_spending(s)

    s = TSpending('Такси', budget.get_person_by_name("Вадюха"), 500)
    s.add_consumer(budget.persons_list)
    s.calc_weighted()
    budget.add_spending(s)

    s = TSpending('Такси', budget.get_person_by_name("Валёк"), 460)
    s.add_consumer(budget.persons_list)
    s.calc_weighted()
    budget.add_spending(s)

    s = TSpending('Такси', budget.get_person_by_name("Сергей"), 450)
    s.add_consumer(budget.persons_list)
    s.calc_weighted()
    budget.add_spending(s)

    s = TSpending('Автобус', budget.get_person_by_name("Сергей"), 250)
    s.add_consumer(budget.persons_list)
    s.calc_weighted()
    budget.add_spending(s)

    s = TSpending('На всё про всё', budget.get_person_by_name("Артём"), 18870)
    s.add_consumer(budget.persons_list)
    s.calc_weighted()
    budget.add_spending(s)

    s = TSpending('Джин Ягер Ром', budget.get_person_by_name("Наташа"), 5768)
    s.add_consumer(budget.persons_list)
    s.calc_weighted()
    budget.add_spending(s)

    s = TSpending('КХ', budget.get_person_by_name("Алексей"), 170)
    s.add_consumer(budget.persons_list)
    s.calc_weighted()
    budget.add_spending(s)

    s = TSpending('Калуа+', budget.get_person_by_name("Алексей"), 4800)
    s.add_consumer(budget.persons_list)
    s.calc_weighted()
    budget.add_spending(s)

    s = TSpending('Ашан', budget.get_person_by_name("Вадим Н"), 10740)
    s.add_consumer(budget.persons_list)
    s.calc_weighted()
    budget.add_spending(s)

    budget.calc_debt_operations_list('monte-carlo')

    return budget


def get_available_budgets(directory_path='./'):
    path = pathlib.Path(directory_path)
    if not path.is_dir():
        return []

    budgets_list = []
    for l in path.iterdir():
        if l.is_file():
            if l.name.endswith('.bdg'):
                budgets_list.append(l.name)
    return budgets_list


def save_budget(budget: TBudget, file_name='budget.bdg'):
    if len(file_name) < 4:
        pass
    if not file_name.endswith('.bdg'):
        file_name += '.bdg'

    f = open(file_name, 'w')
    f.write('BUDGET_MEMO = ' + '{0:20s}'.format(budget.memo))
    for p in budget.persons_list:
        f.write('\n ' + '{0:10s}'.format(p.name()) + ' = {0:4.3f}'.format(p.weight()) + ' = {0:8s}'.format(p.pays_for))

    for sp in budget.spending_list:
        f.write('\nSPENDING_MEMO = ' + '{0:20s}'.format(sp.memo))
        f.write('\n SPENDING_PAYER_NAME = ' + '{0:10s}'.format(sp.payer.name()))
        f.write('\n SPENDING_AMOUNT = ' + '{0:12.6f}'.format(sp.amount))
        for p in sp.consumers_list:
            f.write('\n ' + '{0:10s}'.format(p.who.name()) + ' = ' + '{0:12.6f}'.format(p.amount))

    for debt_o in budget.debt_operations_list:
        f.write('\nDEBT_OPERATION')
        f.write('\n DEBTOR_NAME = ' + '{0:10s}'.format(debt_o.debtor.name()))
        f.write('\n CREDITOR_NAME = ' + '{0:10s}'.format(debt_o.creditor.name()))
        f.write('\n AMOUNT = ' + '{0:12.6f}'.format(debt_o.amount))

    f.close()


def load_budget(file_name):
    if len(file_name) < 4:
        pass
    if not file_name.endswith('.bdg'):
        file_name += '.bdg'

    if not pathlib.Path(file_name).is_file():
        return TBudget()

    f = open(file_name, 'r')

    # Название бюджета
    lin = f.readline().rstrip().split('=')
    if len(lin) > 1:
        lin = lin[1].strip()
    else:
        lin = ''
    budget = TBudget(lin)

    # Участники бюджета
    lin = f.readline().strip()
    while (not lin.startswith('SPENDING_MEMO')) and (lin != ''):
        lin_spl = lin.split('=')
        p = TPerson(lin_spl[0].strip(), float(lin_spl[1]), lin_spl[2].strip())
        budget.persons_list.append(p)
        lin = f.readline().strip()

    # Траты
    while lin != '' and (not lin.startswith('DEBT_OPERATION')):
        lin = lin.split('=')
        if len(lin) > 1:
            memo = lin[1].strip()
        else:
            memo = ''
        lin = f.readline().strip()
        payer_name = lin.split(' = ')[1]
        lin = f.readline().strip()
        amount = float(lin.split(' = ')[1])

        payer = budget.get_person_by_name(payer_name)

        spending = TSpending(memo, payer, amount)

        # Потребители
        lin = f.readline().strip()
        while (not lin.startswith('SPENDING_MEMO')) and (lin != '') and (not lin.startswith('DEBT_OPERATION')):
            consumer_name = lin.split(' = ')[0].strip()
            amount = float(lin.split(' = ')[1])
            consumer = budget.get_person_by_name(consumer_name)
            spending.add_consumer(consumer, amount)
            lin = f.readline().strip()

        budget.add_spending(spending)

    while lin != '':
        lin = f.readline().strip()
        debtor_name = lin.split(' = ')[1]
        lin = f.readline().strip()
        creditor_name = lin.split(' = ')[1]
        lin = f.readline().strip()
        amount = float(lin.split(' = ')[1])

        debtor = budget.get_person_by_name(debtor_name)
        creditor = budget.get_person_by_name(creditor_name)

        debt_operation = TDebtOperation(debtor, creditor, amount)

        budget.debt_operations_list.append(debt_operation)
        lin = f.readline().strip()
    f.close()
    return budget
