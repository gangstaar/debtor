from budget.types import TBudget
from budget.types import TPerson
from budget.types import TSpending, TSpendingAttr
from budget.types import TDebtOperation
import pathlib
from datetime import datetime as dt
import os


def get_report(budget, is_long=False):
    rep = ['В бюджете "' + budget.memo + '" участвуют: ']
    spend = ''
    for p in budget.persons_list:
        spend += p.name + ' ({0:2.1f})'.format(p.weight)
        if p != budget.persons_list[-1]:
            spend += ', '
    rep.append(spend)
    rep.append('')

    rep.append("Зафиксировано трат на сумму " + '{0:7.2f}'.format(budget.get_spending_amount_total()) + " Р:")
    for spend in budget.spending_list:
        n = spend.payer.name + ';'
        line = '    ' + spend.date_time.strftime('%d.%m.%Y %H:%M') + ' {0:9.2f}'.format(spend.amount) + \
               ' Р за ' + '{0:20s}'.format(spend.memo) + ' заплатил ' + '{0:8s}'.format(n)

        names = []
        for c in spend.consumers_list:
            names.append(c.person.name)

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

    def app_hor_line(str_in):
        str_in.append('+ {0:s}+'.format('- ' * 55))

    app_hor_line(rep)
    rep.append('| {0:9s} | '.format("Имя") + '{0:9s} | '.format("Потребил")
               + '{0:14s} | '.format("За чужой счёт") + '{0:9s} | '.format("Потратил")
               + '{0:9s} | '.format("На себя") + '{0:19s} | '.format("Потребил - потратил")
               + '{0:9s} | '.format("Долг*") + '{0:10s} |'.format("Кто платит"))
    app_hor_line(rep)
    cons_not_payed_sum = 0.0
    spend_own_sum = 0.0
    for p in budget.persons_list:
        cons = budget.get_consumption_amount_for_person(p)
        cons_not_payed = budget.get_consumption_amount_not_payed_by_him_for_person(p)
        cons_not_payed_sum += cons_not_payed
        spend = budget.get_spending_amount_for_person(p)
        spend_own = budget.get_spending_amount_own_for_person(p)
        spend_own_sum += spend_own
        debt = budget.get_debt_for_person(p)

        pays_for_name = budget.get_person_name_who_pays_for(p)

        s = '| {0:9s} | '.format(p.name) + "{0:9.2f} | ".format(cons) + "{0:14.2f} | ".format(cons_not_payed) \
            + "{0:9.2f} | ".format(spend) + "{0:9.2f} | ".format(spend_own) + "{0:19.2f} | ".format(cons - spend)\
            + "{0:9.2f} | ".format(debt) + "{0:10s} |".format(pays_for_name)

        rep.append(s)
        if is_long:
            for sp in budget.get_spending_list_for_person(p):
                rep.append('    ' + "{0:9.2f}".format(sp.amount) + ' Р на ' + '{0:20s}'.format(sp.memo))


    cons = budget.get_consumption_amount_total()
    spend = budget.get_spending_amount_total()
    debt = budget.get_debt_sum()
    app_hor_line(rep)
    rep.append('| {0:9s} | '.format("Всего") + "{0:9.2f} | ".format(cons) + "{0:14.2f} | ".format(cons_not_payed_sum)
               + "{0:9.2f} | ".format(spend) + "{0:9.2f} | ".format(spend_own_sum) + "{0:19.2f} | ".format(cons-spend)
               + "{0:9.2f} | ".format(debt) + "{0:10s} |".format(''))
    app_hor_line(rep)

    rep.append('* - Долг участника рассчитывается с учётом его потреблений, трат, промежуточных операций  по долгам, а также его')
    rep.append('    обязательств по оплате долгов других участников. Другими словами - это то количество денег, которое участник')
    rep.append('    должен отдать.')
    rep.append('')
    rep.append('Сумма долгов > 0: ' + '{0:9.2f} Р.'.format(budget.get_positive_debt_sum()))

    rep.append('')
    rep.append('Промежуточные операции по долгам:')
    for op in budget.debt_operations_list_inter:
        rep.append('{0:8s}'.format(op.creditor.name) + ' -отдал-> ' + '{0:8s}'.format(op.debtor.name) + ' {0:9.2f}'.format(op.amount) + ' Р')

    rep.append('')
    rep.append('Операции по долгам:')
    trans_sum = 0
    for op in budget.debt_operations_list:
        rep.append('{0:8s}'.format(op.debtor.name) + ' -отдаёт-> ' + '{0:8s}'.format(op.creditor.name) + ' {0:9.2f}'.format(op.amount) + ' Р')
        trans_sum += op.amount

    rep.append('')
    rep.append('{0:2d}'.format(len(budget.debt_operations_list)) + ' переводов на сумму ' + '{0:9.2f} Р.'.format(trans_sum))

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
        s += '<td>' + p.name + '</td> <td>' + ' ({0:2.1f})</td>'.format(p.weight)
        s += '</tr>'
    s += '</table>'
    rep.append(s)
    rep.append('')

    rep.append("<br>Зафиксировано операций на сумму " + '{0:7.2f}'.format(budget.get_spending_amount_total()) + " Р:")
    line = '<table>'
    for s in budget.spending_list:
        n = s.payer.name + ';'
        line += '<tr>'
        line += '<td>    </td><td>' + s.date_time.strftime('%d.%m.%Y %H:%M') + '</td><td>' + \
                '{0:8.2f}'.format(s.amount) + \
                ' Р </td><td>за ' + '{0:20s}</td><td>'.format(s.memo) + \
                ' заплатил </td><td>' + '{0:8s}</td>'.format(n)

        names = []
        for c in s.consumers_list:
            names.append(c.person.name)

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
        line += '<td>{0:8s}</td><td>'.format(p.name) + ' всего потратил </td><td>' + "{0:5.2f}".format(s) + ' Р:</td>'

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
        line += '<td>{0:8s}</td><td>'.format(p.name) + ' всего потребил на </td><td>' + "{0:8.2f}".format(c) + ' Р</td>'
        consume_amount += c

        if is_long:
            line += '<tr>'
            for sp in budget.get_consumption_list_for_person(p):
                line += '<tr>'
                line += '<td>    </td><td>' + "{0:8.2f}".format(sp.amount) + ' Р: </td><td>' + \
                           '{0:20s}</td><td>'.format(sp.memo) + ' за счёт </td><td>' + '{0:8s}</td>'.format(sp.spending.payer.name)
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
        line += '<td>{0:8s}</td><td>'.format(p.name) + ' должен </td><td>' + "{0:8.2f}".format(debt) + ' Р</td>'
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
        line += '<td>{0:8s}</td><td>'.format(op.debtor.name) + ' -отдаёт-> </td><td>' + \
                '{0:8s}</td><td>'.format(op.creditor.name) + ' {0:8.2f}'.format(op.amount) + ' Р</td>'
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

    s = TSpending(budget.get_person_by_name("Гошан"), 'Лемончелла', 1850, dt(2018, 12, 28, 13, 0, 0))
    s.add_consumer(budget.persons_list)
    s.calc_weighted()
    budget.add_spending(s)

    s = TSpending(budget.get_person_by_name("Алексей"), 'Калуа+', 4800, dt(2018, 12, 28, 14, 0, 0))
    s.add_consumer(budget.persons_list)
    s.calc_weighted()
    budget.add_spending(s)

    s = TSpending(budget.get_person_by_name("Наташа"), 'Джин Ягер Ром', 5768, dt(2018, 12, 28, 15, 0, 0))
    s.add_consumer(budget.persons_list)
    s.calc_weighted()
    budget.add_spending(s)

    s = TSpending(budget.get_person_by_name("Гошан"), 'Такси', 588, dt(2018, 12, 31, 17, 0, 0))
    s.add_consumer(budget.persons_list)
    s.calc_weighted()
    budget.add_spending(s)

    s = TSpending(budget.get_person_by_name("Сергей"), 'Такси', 450, dt(2018, 12, 31, 17, 31, 0))
    s.add_consumer(budget.persons_list)
    s.calc_weighted()
    budget.add_spending(s)

    s = TSpending(budget.get_person_by_name("Вадим Н"), 'Ашан', 10740, dt(2018, 12, 31, 17, 15, 0))
    s.add_consumer(budget.persons_list)
    s.calc_weighted()
    budget.add_spending(s)

    s = TSpending(budget.get_person_by_name("Гошан"), 'Ашан', 7035, dt(2018, 12, 31, 17, 25, 0))
    s.add_consumer(budget.persons_list)
    s.calc_weighted()
    budget.add_spending(s)

    s = TSpending(budget.get_person_by_name("Гошан"), 'Автобус', 50, dt(2019, 1, 2, 9, 0, 0))
    s.add_consumer(budget.persons_list)
    s.calc_weighted()
    budget.add_spending(s)

    s = TSpending(budget.get_person_by_name("Гошан"), 'Билеты в пещеру', 8400, dt(2019, 1, 2, 13, 0, 0))
    s.add_consumer(budget.persons_list)
    s.calc_weighted()
    budget.add_spending(s)

    s = TSpending(budget.get_person_by_name("Сергей"), 'Автобус', 250, dt(2019, 1, 2, 20, 0, 0))
    s.add_consumer(budget.persons_list)
    s.calc_weighted()
    budget.add_spending(s)

    s = TSpending(budget.get_person_by_name("Вадюха"), 'Такси', 500, dt(2019, 1, 4, 10, 0, 0))
    s.add_consumer(budget.persons_list)
    s.calc_weighted()
    budget.add_spending(s)

    s = TSpending(budget.get_person_by_name("Валёк"), 'Такси', 460, dt(2019, 1, 4, 10, 10, 0))
    s.add_consumer(budget.persons_list)
    s.calc_weighted()
    budget.add_spending(s)

    s = TSpending(budget.get_person_by_name("Алексей"), 'КХ', 170, dt(2019, 1, 4, 12, 0, 0))
    s.add_consumer(budget.persons_list)
    s.calc_weighted()
    budget.add_spending(s)

    s = TSpending(budget.get_person_by_name("Гошан"), 'КХ', 170, dt(2019, 1, 4, 12, 0, 0))
    s.add_consumer(budget.persons_list)
    s.calc_weighted()
    budget.add_spending(s)

    s = TSpending(budget.get_person_by_name("Артём"), 'На всё про всё', 18870, dt(2019, 1, 4, 15, 0, 0))
    s.add_consumer(budget.persons_list)
    s.calc_weighted()
    budget.add_spending(s)

    budget.add_debt_operation_intermediate("Гошан", "Валёк", 3000)
    budget.add_debt_operation_intermediate("Гошан", "Лена", 904.34)

    budget.calc_debt_operations_list('simple')

    return budget


def get_available_budgets(directory_path='./', sortByTime=0):
    path = pathlib.Path(directory_path)
    if not path.is_dir():
        return []

    budget_files_list = []
    for l in path.iterdir():
        if l.is_file():
            if l.name.endswith('.bdg'):
                budget_files_list.append(l)

    def getFileLastEditTime(file):
        return file.stat().st_mtime

    def getFileBirthTime(file):
        return file.stat().st_ctime

    if sortByTime == 1:
        budget_files_list.sort(reverse=True, key=getFileBirthTime)

    budgets_list = []
    for file in budget_files_list:
        budgets_list.append(file.name)


    return budgets_list


def save_budget(budget, file_name='budget.bdg'):
    #  type: (TBudget, str) -> None
    if len(file_name) < 4:
        pass
    if not file_name.endswith('.bdg'):
        file_name += '.bdg'

    f = open(file_name, 'w', encoding='utf-8')
    f.write('BUDGET_MEMO = ' + '{0:20s}'.format(budget.memo))
    for p in budget.persons_list:
        f.write('\n ' + '{0:10s}'.format(p.name) + ' = {0:4.3f}'.format(p.weight) + ' = {0:8s}'.format(p.pays_for))

    for sp in budget.spending_list:
        f.write('\nSPENDING_MEMO = ' + '{0:20s}'.format(sp.memo))
        f.write('\n SPENDING_DATETIME = ' + sp.date_time.strftime(TSpending.get_datetime_format_s()))
        f.write('\n SPENDING_PAYER_NAME = ' + '{0:10s}'.format(sp.payer.name))
        f.write('\n SPENDING_AMOUNT = ' + '{0:12.6f}'.format(sp.amount))
        for p in sp.consumers_list:
            f.write('\n ' + '{0:10s}'.format(p.person.name) + ' = ' + '{0:12.6f}'.format(p.amount))
        f.write('\n SPENDING_ATTR_KEY = ' + '{0:8d}'.format(sp.attr.key))
        f.write('\n SPENDING_ATTR_MEMO = ' + '{0:20s}'.format(sp.attr.memo))
        f.write('\n SPENDING_ATTR_COLOR = ' +   '{0:04.2f}'.format(sp.attr.colorRGB[0]) +
                                                ' {0:04.2f}'.format(sp.attr.colorRGB[1]) +
                                                ' {0:04.2f}'.format(sp.attr.colorRGB[2]))

    if budget.current_spending is not None:
        sp = budget.current_spending
        f.write('\nC_SPENDING_MEMO = ' + '{0:20s}'.format(sp.memo))
        f.write('\n SPENDING_DATETIME = ' + sp.date_time.strftime(TSpending.get_datetime_format_s()))
        f.write('\n SPENDING_PAYER_NAME = ' + '{0:10s}'.format(sp.payer.name))
        f.write('\n SPENDING_AMOUNT = ' + '{0:12.6f}'.format(sp.amount))
        for p in sp.consumers_list:
            f.write('\n ' + '{0:10s}'.format(p.person.name) + ' = ' + '{0:12.6f}'.format(p.amount))
        f.write('\n SPENDING_ATTR_KEY = ' + '{0:8d}'.format(sp.attr.key))
        f.write('\n SPENDING_ATTR_MEMO = ' + '{0:20s}'.format(sp.attr.memo))
        f.write('\n SPENDING_ATTR_COLOR = ' +   '{0:04.2f}'.format(sp.attr.colorRGB[0]) +
                                                ' {0:04.2f}'.format(sp.attr.colorRGB[1]) +
                                                ' {0:04.2f}'.format(sp.attr.colorRGB[2]))

    for debt_o in budget.debt_operations_list_inter:
        f.write('\nDEBT_OPERATION_INTERMEDIATE')
        f.write('\n DEBTOR_NAME = ' + '{0:10s}'.format(debt_o.debtor.name))
        f.write('\n CREDITOR_NAME = ' + '{0:10s}'.format(debt_o.creditor.name))
        f.write('\n AMOUNT = ' + '{0:12.6f}'.format(debt_o.amount))

    for debt_o in budget.debt_operations_list:
        f.write('\nDEBT_OPERATION')
        f.write('\n DEBTOR_NAME = ' + '{0:10s}'.format(debt_o.debtor.name))
        f.write('\n CREDITOR_NAME = ' + '{0:10s}'.format(debt_o.creditor.name))
        f.write('\n AMOUNT = ' + '{0:12.6f}'.format(debt_o.amount))

    f.close()


def load_budget(file_name):
    if len(file_name) < 4:
        pass
    if not file_name.endswith('.bdg'):
        file_name += '.bdg'

    if not pathlib.Path(file_name).is_file():
        return TBudget()

    f = open(file_name, 'r', encoding='utf-8')

    # Название бюджета
    lin = f.readline().rstrip().split('=')
    if len(lin) > 1:
        lin = lin[1].strip()
    else:
        lin = ''
    budget = TBudget(lin)

    # Участники бюджета
    lin = f.readline().strip()
    while (not (lin.startswith('SPENDING_MEMO') or lin.startswith('C_SPENDING_MEMO')
                or lin.startswith('DEBT_OPERATION') )) and (lin != ''):
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

        if lin[0].strip() == 'C_SPENDING_MEMO':
            is_c_spending = True
        else:
            is_c_spending = False

        lin = f.readline().strip()
        if lin.startswith('SPENDING_DATETIME'):
            datetime = dt.strptime(lin.split(' = ')[1], TSpending.get_datetime_format_s())
            lin = f.readline().strip()
        else:
            datetime = None

        if not is_c_spending:
            payer_name = lin.split(' = ')[1]
            lin = f.readline().strip()
            amount = float(lin.split(' = ')[1])
            payer = budget.get_person_by_name(payer_name)
        else:
            if len(lin.split(' = ')) == 2:
                payer_name = lin.split(' = ')[1]
                payer = budget.get_person_by_name(payer_name)
            else:
                payer = TPerson()

            lin = f.readline().strip()

            if len(lin.split(' = ')) == 2:
                amount = float(lin.split(' = ')[1])
            else:
                amount = 0

        if datetime is not None:
            spending = TSpending(payer, memo, amount, datetime)
        else:
            spending = TSpending(payer, memo, amount)

        # Потребители
        lin = f.readline().strip()
        while (not(lin.startswith('SPENDING_MEMO') or
                   lin.startswith('C_SPENDING_MEMO') or
                   lin.startswith('DEBT_OPERATION') or
                   lin.startswith('SPENDING_ATTR_KEY')) and
                (lin != '')):
            consumer_name = lin.split(' = ')[0].strip()
            amount = float(lin.split(' = ')[1])
            consumer = budget.get_person_by_name(consumer_name)
            spending.add_consumer(consumer, amount)
            lin = f.readline().strip()

        # Атрибуты
        attr = TSpendingAttr()
        if lin.startswith('SPENDING_ATTR_KEY'):
            attr.key = int(lin.split(' = ')[1])
            lin = f.readline().strip()
            val = lin.split(' = ')
            if val.__len__() > 1:
                attr.memo = val[1].strip()
            else:
                attr.memo = ''
            lin = f.readline().strip()
            colors = lin.split(' = ')[1].split(' ')
            attr.colorRGB = [float(colors[0]), float(colors[1]), float(colors[2])]
            lin = f.readline().strip()

        spending.set_attr(attr)

        if is_c_spending:
            budget.current_spending = spending
        else:
            budget.add_spending(spending)

    # Промежуточные операции по долгам
    while lin != '' and lin.strip() != 'DEBT_OPERATION':
        lin = f.readline().strip()
        debtor_name = lin.split(' = ')[1]
        lin = f.readline().strip()
        creditor_name = lin.split(' = ')[1]
        lin = f.readline().strip()
        amount = float(lin.split(' = ')[1])

        budget.add_debt_operation_intermediate(debtor_name, creditor_name, amount)
        lin = f.readline().strip()

    # Операции по долгам
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


def is_budget_exists(budget_name):
    path = os.path.dirname(budget_name)
    saved_budgets = get_available_budgets(path)
    if os.path.basename(budget_name) in saved_budgets:
        return True
    else:
        return False
