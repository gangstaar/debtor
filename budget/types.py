# Файл с описанием типов
from typing import List
import random as rnd
import math
from datetime import datetime as dt, datetime


class TPerson:
    def __init__(self, name='', weight=1.0, pays_for=''):
        self.name = name  # type: str
        self.weight = weight  # type: float
        self.pays_for = pays_for  # type: str


class TDebtOperation:
    def __init__(self, debtor, creditor, amount=0.0):
        self.debtor = debtor  # type: TPerson
        self.creditor = creditor  # type: TPerson
        self.amount = amount


class TConsumer:
    def __init__(self, spending, person, amount=0.0, memo=''):
        self.person = person  # type: TPerson
        self.memo = memo
        self.amount = amount
        self.spending = spending  # type: TSpending


class TSpendingAttr:
    def __init__(self, key=None, color_rgb=None, memo=''):
        if color_rgb is None:
            color_rgb = [0.3, 0.3, 0.3]
        self.colorRGB = color_rgb
        self.memo = memo
        if key is None:
            key = -1
        self.key = key


class TSpending:
    def __init__(self, payer, memo='', amount=0.0, date_time=dt(2019, 1, 1, 0, 0, 0), attr=TSpendingAttr()):
        self.memo = memo
        self.payer = payer  # type: TPerson
        self.amount = amount
        self.consumers_list = []  # type: List[TConsumer]
        self.date_time = date_time  # type: datetime
        self.attr = attr  # type : TSpendingAttr

    @staticmethod
    def get_datetime_format_s():
        return '%d.%m.%Y %H:%M:%S'

    @staticmethod
    def get_date_format_s():
        return '%d.%m.%Y'

    def set_attr(self, attr):
        self.attr = attr

    def get_attr(self):
        return self.attr

    def get_date_s(self):
        return self.date_time.strftime(self.get_date_format_s())

    def is_participant(self, person_name):
        if isinstance(person_name, TPerson):
            person_name = person_name.name

        for cons in self.consumers_list:
            if cons.person.name == person_name:
                return True
        return False

    def add_consumer(self, persons, amount=0.00):
        if isinstance(persons, List):
            for p in persons:
                if not self.is_participant(p):
                    self.consumers_list.append(TConsumer(self, p, amount, self.memo))
        else:
            if not self.is_participant(persons):
                self.consumers_list.append(TConsumer(self, persons, amount, self.memo))

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
            w += cons.person.weight
        # Расчёт расходов на каждого потребителя в соответствии с его весом
        for cons in self.consumers_list:
            cons.amount = cons.person.weight / w * self.amount

    def is_calculated(self):
        a = 0
        for cons in self.consumers_list:
            a += cons.amount

        if abs(a - self.amount) < 1e-2:
            return True
        else:
            return False

    def get_consumption_for_person(self, person_name):
        # type: (str) -> TConsumer
        if isinstance(person_name, TPerson):
            person_name = person_name.name

        for cons in self.consumers_list:
            if cons.person.name == person_name:
                return cons
        return None

    def get_consumption_amount_for_person(self, person_name):
        # type: (str) -> float
        if isinstance(person_name, TPerson):
            person_name = person_name.name

        cons = self.get_consumption_for_person(person_name)

        if cons is None:
            return 0
        else:
            return cons.amount

    def get_undistributed_value(self):
        a = 0
        for cons in self.consumers_list:
            a += cons.amount
        return self.amount - a


class TBudget:
    def __init__(self, memo=''):
        self.memo = memo
        self.persons_list = []  # type: List[TPerson]
        self.spending_list = []  # type: List[TSpending]
        self.debt_operations_list_inter = []  # type: List[TDebtOperation]
        self.debt_operations_list = []  # type: List[TDebtOperation]
        self.current_spending = None  # type: TSpending

    def get_person_by_name(self, person_name):
        for p in self.persons_list:
            if p.name == person_name:
                return p
        return None

    def get_spendings_by_attr(self, attr):
        # type: (TSpendingAttr) -> List[TSpending]
        ret_list = []
        for s in self.spending_list:
            if attr.key == s.attr.key:
                ret_list.append(s)

        return ret_list

    def get_all_attrs(self):
        ret_list = []  # type: List[TSpendingAttr]

        for s in self.spending_list:
            if s not in ret_list:
                ret_list.append(s)

        return ret_list

    def is_participant(self, person_name):
        if isinstance(person_name, TPerson):
            person_name = person_name.name

        if self.get_person_by_name(person_name) is None:
            return False
        else:
            return True

    def add_spending(self, spending):
        #  type: (TSpending) -> None
        if not spending.is_calculated():
            return

        for c in spending.consumers_list:
            if not self.is_participant(c.person.name):
                return

        for sp in self.spending_list:
            if spending.date_time < sp.date_time:
                self.spending_list.insert(self.spending_list.index(sp), spending)
                return

        self.spending_list.append(spending)

    def add_person(self, person):
        #  type: (TPerson) -> None
        if self.is_participant(person.name):
            return

        if person.weight < 0:
            return

        self.persons_list.append(person)

    def add_debt_operation_intermediate(self, receiver_name, transmitter_name, amount):
        #  type: (str, str, int) -> None
        if not self.is_participant(transmitter_name) or not self.is_participant(receiver_name):
            return
        if amount <= 0.:
            return

        debtor = self.get_person_by_name(receiver_name)
        creditor = self.get_person_by_name(transmitter_name)

        self.debt_operations_list_inter.append(TDebtOperation(debtor, creditor, amount))

    # Возвращает список всех расходов person_name
    def get_spending_list_for_person(self, person_name):
        if isinstance(person_name, TPerson):
            person_name = person_name.name

        sp_list = []
        for sp in self.spending_list:
            if sp.payer.name == person_name:
                sp_list.append(sp)
        return sp_list

    # Возвращает сумму всех расходов person_name
    def get_spending_amount_for_person(self, person_name):
        if isinstance(person_name, TPerson):
            person_name = person_name.name

        sp_list = self.get_spending_list_for_person(person_name)
        s = 0.00
        for sp in sp_list:
            s += sp.amount

        return s

    # Возвращает сумму всех расходов person_name на самого себя
    def get_spending_amount_own_for_person(self, person_name):
        if isinstance(person_name, TPerson):
            person_name = person_name.name

        s = self.get_consumption_amount_for_person(person_name) - \
            self.get_consumption_amount_not_payed_by_him_for_person(person_name)

        return s

    # Возвращает общую сумму расходов
    def get_spending_amount_total(self):
        s = 0.00
        for sp in self.spending_list:
            s += sp.amount
        return s

    # Возвращает список потребления person_name
    def get_consumption_list_for_person(self, person_name):
        if isinstance(person_name, TPerson):
            person_name = person_name.name

        c_list = []
        for spending in self.spending_list:
            if spending.is_participant(person_name):
                c_list.append(spending.get_consumption_for_person(person_name))
        return c_list

    # Возвращает сумму потребления person_name
    def get_consumption_amount_for_person(self, person_name):
        if isinstance(person_name, TPerson):
            person_name = person_name.name

        c_list = self.get_consumption_list_for_person(person_name)
        am = 0.00
        for c in c_list:
            am += c.amount

        return am

    # Возвращает сумму потребления person_name, за которые он не платил
    def get_consumption_amount_not_payed_by_him_for_person(self, person_name):
        if isinstance(person_name, TPerson):
            person_name = person_name.name

        c_list = self.get_consumption_list_for_person(person_name)
        s = 0.00
        for c in c_list:
            if c.spending.payer.name != person_name:
                s += c.amount

        return s

    # Возвращает общую сумму потребления
    def get_consumption_amount_total(self):
        c = 0
        for p in self.persons_list:
            c += self.get_consumption_amount_for_person(p.name)

        return c

    def get_person_name_who_pays_for(self, person_name):
        if isinstance(person_name, TPerson):
            person_name = person_name.name

        for p in self.persons_list:
            if p.pays_for == person_name:
                return p.name

        return ''

    # Рассчитывает долг person. Положительная величина
    # означает, что person потребил больше, чем потратил
    def get_debt_for_person(self, person_name):
        if isinstance(person_name, TPerson):
            person_name = person_name.name

        # Потребил - потратил
        debt_own = self.get_consumption_amount_for_person(person_name) - \
            self.get_spending_amount_for_person(person_name)

        # Если за person кто-то платит и person кому-то должен
        if self.get_person_name_who_pays_for(person_name) != '' and debt_own > 0:
            return 0.0

        p = self.get_person_by_name(person_name)

        # Если за кого-то платит
        if p.pays_for != '':
            person_for = p.pays_for
            debt_for = self.get_consumption_amount_for_person(person_for) - \
                self.get_spending_amount_for_person(person_for)
            if debt_for > 0.0:
                debt_own += debt_for

        # Принимал от кого-то промежуточный расчёт
        for dop in self.debt_operations_list_inter:
            if dop.debtor.name == person_name:
                debt_own += dop.amount

        # Отдавал кому-то в промежуточном расчёте
        for dop in self.debt_operations_list_inter:
            if dop.creditor.name == person_name:
                debt_own -= dop.amount

        return debt_own

    # Рассчитывает долг person_name. Положительная величина
    # означает, что person потребил больше, чем потратил.
    # Не учитываются долги участников, за которых платит person_name,
    # а также те, кто оплачивает долг person_name
    def get_debt_for_person_pure(self, person_name):
        if isinstance(person_name, TPerson):
            person_name = person_name.name

        # Потребил - потратил
        debt_own = self.get_consumption_amount_for_person(person_name) - \
                   self.get_spending_amount_for_person(person_name)

        # Принимал от кого-то промежуточный расчёт
        for dop in self.debt_operations_list_inter:
            if dop.debtor.name == person_name:
                debt_own += dop.amount

        # Отдавал кому-то в промежуточном расчёте
        for dop in self.debt_operations_list_inter:
            if dop.creditor.name == person_name:
                debt_own -= dop.amount

        return debt_own

    def get_debt_sum(self):
        s = 0
        for p in self.persons_list:
            s += self.get_debt_for_person(p.name)

        return s

    def get_positive_debt_sum(self):
        s = 0
        for p in self.persons_list:
            s1 = self.get_debt_for_person(p.name)
            if s1 > 0:
                s += s1

        return s

    def get_transaction_sum(self):
        s = 0
        for op in self.debt_operations_list:
            s += op.amount
        return s

    def is_converged(self):

        if len(self.debt_operations_list) == 0:
            return False

        eps_debt = abs(self.get_debt_sum())
        eps_trans = abs(self.get_positive_debt_sum() - self.get_transaction_sum())
        eps_cons = abs(self.get_consumption_amount_total() - self.get_spending_amount_total())

        if (eps_debt < 1e-2) and (eps_trans < 1e-2) and (eps_cons < 1e-2):
            return True
        else:
            return False

    def calc_debt_operations_list(self, algorithm='simple'):
        debtors_list = []
        creditors_list = []
        debtors_amount_list = []
        creditors_amount_list = []

        # Добавление долгов тем, кто оплачивает чужие долги
        for p in self.persons_list:
            d = self.get_debt_for_person(p.name)
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
