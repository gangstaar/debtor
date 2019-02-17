function confirmAction(event)
{
    if (!confirm(this.getAttribute('message')))
    {
        event.preventDefault();
        return false;
    }
}

var elem = document.getElementsByClassName('confirm-required')

for (var i = 0; i < elem.length; i++)
{
    elem[i].onclick = confirmAction
}
