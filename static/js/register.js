function toggleFormType(value) {
    document.getElementById('staff-form').style.display = value === 'staff' ? 'block' : 'none';
    document.getElementById('operator-form').style.display = value === 'operator' ? 'block' : 'none';
}

document.addEventListener('DOMContentLoaded', function () {
    var initialType = document.getElementById('user_type').getAttribute('data-user-type') || '';
    if (initialType) {
        toggleFormType(initialType);
    }
});
