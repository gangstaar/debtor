# Файл с описанием типов
from typing import List
import random as rnd
import math
from datetime import datetime as dt, datetime

date_time_format = '%d.%m.%Y %H:%M:%S'


class TPerson:
    def __init__(self, name='', weight=1.0, pays_for=''):
        self._name = name
        self._weight = weight
        self.pays_for = pays_for

    def set_name(self, new_name):
        self._name = new_name

    def set_weight(self, new_weight):
        self._weight = new_weight

    def name(self):
        return self._name

    def weight(self):
        return self._weight


class TDebtOperation:
    def __init__(self, debtor='', creditor='', amount=0.0):
        self.debtor = debtor
        self.creditor = creditor
        self.amount = amount


class TConsumer:
    def __init__(self, spending, who=TPerson(), amount=0.0, memo=''):
        self.who = who
        self.memo = memo
        self.amount = amount
        self.spending = spending


class TSpending:
    def __init__(self, memo='', payer=TPerson(), amount=0.0, date_time=dt(2019, 1, 1, 0, 0, 0)):
        self.memo = memo
        self.payer = payer  # type: TPerson
        self.amount = amount
        self.consumers_list = []  # type: List[TConsumer]
        self.date_time = date_time  # type: datetime

    def add_consumer(self, person, amount=0.00):
        if isinstance(person, List):
            for p in person:
                if not self.is_participant(p):
                    self.consumers_list.append(TConsumer(self, p, amount, self.memo))
        else:
            if not self.is_participant(person):
                self.consumers_list.append(TConsumer(self, person, amount, self.memo))

    def calc_average(self):
        n = len(self.consumers_list)
        if n == 0:
            return
        s = self.amount / n
        for cons in self.consumers_list:
            cons.amount = s

    def calc_weighted(self):
        w = 0.0
        # Расчёт общего веса потребителей
        for cons in self.consumers_list:
            w += cons.who.weight()
        # Расчёт расходов на каждого потребителя в соответствии с его весом
        for cons in self.consumers_list:
            cons.amount = cons.who.weight() / w * self.amount

    def is_calculated(self):
        a = 0
        for cons in self.consumers_list:
            a += cons.amount

        if abs(a - self.amount) < 1e-2:
            return True
        else:
            return False

    def is_participant(self, person):
        for cons in self.consumers_list:
            if cons.who.name() == person.name():
                return True
        return False

    def get_consumption_for_person(self, person):
        for cons in self.consumers_list:
            if cons.who.name() == person.name():
                return cons
        return []

    def get_undistributed_value(self):
        a = 0
        for cons in self.consumers_list:
            a += cons.amount
        return self.amount - a


class TBudget:
    def __init__(self, memo=''):
        self.memo = memo
        self.persons_list = []
        self.spending_list = []  # type: List[TSpending]
        self.debt_operations_list = []

    def add_spending(self, spending: TSpending):
        if not spending.is_calculated():
            return

        for sp in self.spending_list:
            if spending.date_time < sp.date_time:
                self.spending_list.insert(self.spending_list.index(sp), spending)
                return

        self.spending_list.append(spending)

    def add_person(self, person: TPerson):
        if ~self.persons_list.__contains__(person):
            self.persons_list.append(person)

    # Возвращает список всех расходов person
    def get_spending_list_for_person(self, person):
        sp_list = []
        for sp in self.spending_list:
            if sp.payer.name() == person.name():
                sp_list.append(sp)
        return sp_list

    # Возвращает сумму всех расходов person
    def get_spending_amount_for_person(self, person):
        sp_list = self.get_spending_list_for_person(person)
        s = 0.00
        for sp in sp_list:
            s += sp.amount
        return s

    # Возвращает общую сумму расходов
    def get_spending_amount_total(self):
        s = 0.00
        for sp in self.spending_list:
            s += sp.amount
        return s

    # Возвращает список потребления person
    def get_consumption_list_for_person(self, person):
        c_list = []
        for spending in self.spending_list:
            if spending.is_participant(person):
                c_list.append(spending.get_consumption_for_person(person))
        return c_list

    # Возвращает сумму потребления person
    def get_consumption_amount_for_person(self, person):
        c_list = self.get_consumption_list_for_person(person)
        am = 0.00
        for c in c_list:
            am += c.amount
        return am

    # Возвращает общую сумму потребления
    def get_consumption_amount_total(self):
        c = 0
        for p in self.persons_list:
            c += self.get_consumption_amount_for_person(p)

        return c

    def get_person_name_who_pays_for(self, person: TPerson):
        for p in self.persons_list:
            if p.pays_for == person.name():
                return p.name()

        return ''

    # Рассчитывает долг person. Положительная величина
    # означает, что person потребил больше, чем потратил
    def get_debt_for_person(self, person):
        debt_own = self.get_consumption_amount_for_person(person) - \
                   self.get_spending_amount_for_person(person)

        # Если за person кто-то платит и person кому-то должен
        if self.get_person_name_who_pays_for(person) != '' and debt_own > 0:
            return 0.0

        if person.pays_for != '':
            person_for = self.get_person_by_name(person.pays_for)
            debt_for = self.get_consumption_amount_for_person(person_for) - \
                self.get_spending_amount_for_person(person_for)
            if debt_for > 0.0:
                debt_own += debt_for

        return debt_own

    def get_person_by_name(self, name):
        for p in self.persons_list:
            if p.name() == name:
                return p
        return None

    def is_participant(self, name):
        if self.get_person_by_name(name) is None:
            return False
        else:
            return True

    def get_debt_sum(self):
        s = 0
        for p in self.persons_list:
            s += self.get_debt_for_person(p)

        return s

    def get_positive_debt_sum(self):
        s = 0
        for p in self.persons_list:
            s1 = self.get_debt_for_person(p)
            if s1 > 0:
                s += s1

        return s

    def get_transaction_sum(self):
        s = 0
        for op in self.debt_operations_list:
            s += op.amount
        return s

    def is_converged(self):
        if abs(self.get_debt_sum()) < 1e-2:
            return True
        else:
            return False

    def calc_debt_operations_list(self, algorithm='simple'):
        debtors_list = []
        creditors_list = []
        debtors_amount_list = []
        creditors_amount_list = []
        for p in self.persons_list:
            d = self.get_debt_for_person(p)
            if d > 0:
                debtors_list.append(p)
                debtors_amount_list.append(d)
            if d < 0:
                creditors_list.append(p)
                creditors_amount_list.append(abs(d))

        if algorithm == 'monte-carlo':
            self.debt_operations_list = self.__monte_carlo_algorithm(debtors_list, creditors_list, debtors_amount_list,
                                                                     creditors_amount_list)
        else:
            self.debt_operations_list = self.__simple_algorithm(debtors_list, creditors_list, debtors_amount_list,
                                                                creditors_amount_list)

    @staticmethod
    def __simple_algorithm(debtors_list, creditors_list,
                           debtors_amount_list, creditors_amount_list) \
            -> List[TDebtOperation]:

        debt_operations_list = []
        for i in range(creditors_list.__len__()):
            creditor = creditors_list[i]
            amount_to_collect = creditors_amount_list[i]
            collected_from_debtors = 0

            for j in range(debtors_list.__len__()):
                debtor = debtors_list[j]
                d = debtors_amount_list[j]

                if d <= 0.:
                    continue

                # Если должник отдаст весь долг и это не погасит кредит
                if collected_from_debtors + d < amount_to_collect:
                    debt_operations_list.append(TDebtOperation(debtor, creditor, d))
                    debtors_amount_list[j] = 0.0
                    collected_from_debtors += d
                else:
                    rest = amount_to_collect - collected_from_debtors
                    debt_operations_list.append(TDebtOperation(debtor, creditor, rest))
                    debtors_amount_list[j] -= rest
                    collected_from_debtors += d
                    break

            if abs(collected_from_debtors - amount_to_collect) < 1e-2:
                continue

        return debt_operations_list

    @staticmethod
    def __monte_carlo_algorithm(debtors_list: List[TPerson], creditors_list: List[TPerson],
                                debtors_amount_list, creditors_amount_list) -> List[TDebtOperation]:
        a = debtors_amount_list
        b = creditors_amount_list

        def __sum_row(row_n):
            s = 0.0
            for col_n in range(len(c)):
                s += c[col_n][row_n] * a[col_n]
            return s

        def __sum_col(col_n):
            return sum(c[col_n])

        def __is_calculated():
            for row_n in range(len(b)):
                if not __is_row_calculated(row_n):
                    return False
            return True

        def __is_row_calculated(row_n):
            if abs(__sum_row(row_n) - b[row_n]) > 1e-3:
                return False
            return True

        max_iter = 1000
        best_debt_operations_list = []
        c = [[0] * len(b) for i in range(len(a))]

        for iter_n in range(max_iter):

            while not __is_calculated():
                row_n = rnd.random()
                row_n = math.floor(row_n * (len(b) - 1) + 0.5)

                while not __is_row_calculated(row_n):
                    k = rnd.random()
                    k = math.floor(k * (len(a) - 1) + 0.5)
                    if c[k][row_n] != 0.0:
                        continue
                    s = __sum_col(k)
                    if s > 1 - 1e-5:
                        continue

                    rest = b[row_n] - __sum_row(row_n)
                    if (1 - s) * a[k] <= rest:
                        c[k][row_n] = 1 - s
                    else:
                        c[k][row_n] = rest / a[k]

            debt_operations_list = []
            for cred_n in range(len(creditors_list)):
                for debt_n in range(len(debtors_list)):
                    if c[debt_n][cred_n] > 0:
                        debt_operations_list.append(TDebtOperation(debtors_list[debt_n], creditors_list[cred_n],
                                                                   c[debt_n][cred_n] * debtors_amount_list[debt_n]))

            if len(best_debt_operations_list) == 0 or len(debt_operations_list) < len(best_debt_operations_list):
                best_debt_operations_list = debt_operations_list

        return best_debt_operations_list
