function toggleFormType(value) {
    const staffForm = document.getElementById('staff-form');
    const operatorForm = document.getElementById('operator-form');

    staffForm.style.display = value === 'staff' ? 'block' : 'none';
    operatorForm.style.display = value === 'operator' ? 'block' : 'none';

    setFormFieldsEnabled(staffForm, value === 'staff');
    setFormFieldsEnabled(operatorForm, value === 'operator');
}

function setFormFieldsEnabled(section, enabled) {
    const fields = section.querySelectorAll('input, select, textarea');

    fields.forEach(field => {
        field.disabled = !enabled;
    });
}

document.addEventListener('DOMContentLoaded', function () {
    const userTypeSelect = document.getElementById('user_type');
    const initialType = userTypeSelect.getAttribute('data-user-type') || userTypeSelect.value;

    toggleFormType(initialType);

    userTypeSelect.addEventListener('change', function () {
        toggleFormType(this.value);
    });
});

document.querySelector(".register-form").addEventListener("submit", function () {
    console.log("Submitting...");
    console.log("Disabled staff fields:", document.querySelectorAll("#staff-form input:disabled, #staff-form select:disabled, #staff-form textarea:disabled").length);
    console.log("Disabled operator fields:", document.querySelectorAll("#operator-form input:disabled, #operator-form select:disabled, #operator-form textarea:disabled").length);
});