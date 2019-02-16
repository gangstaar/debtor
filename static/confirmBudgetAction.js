function confirmDeleteBudget(event, budget_file)
{
    if (!confirm('Удалить бюджет "' + budget_file + '" ?'))
    {
        event.preventDefault();
    }
    return false;
}
function confirmCopyBudget(event, budget_file)
{
    if (!confirm('Создать копию бюджета "' + budget_file + '" ?'))
    {
        event.preventDefault();
    }
    return false;
}
function confirmDeletePerson(event, name)
{
    if (!confirm('Удаление участника бюджета приведёт к очистке списка операций бюджета. Удалить участника по имени "'+name+'" ?'))
    {
        event.preventDefault();
    }
    return;
}

function confirmDeleteSpending(event, index)
{
    if (!confirm('Удалить трату № ' + index + ' ?'))
    {
        event.preventDefault();
    }
    return;
}