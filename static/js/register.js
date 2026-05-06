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

function updateRegisterHero(userType) {
  const eyebrow = document.getElementById("register-eyebrow");
  const title = document.getElementById("register-title");
  const description = document.getElementById("register-description");
  const benefit1 = document.getElementById("benefit-1");
  const benefit2 = document.getElementById("benefit-2");
  const benefit3 = document.getElementById("benefit-3");

  if (!eyebrow || !title || !description || !benefit1 || !benefit2 || !benefit3) {
    return;
  }

  if (userType === "staff") {
    eyebrow.textContent = "Staff Profile";
    title.textContent = "Get found for shifts that fit.";
    description.textContent =
      "Create a worker profile, set your availability, and build trust through completed shifts.";

    benefit1.textContent = "Set your role and availability";
    benefit2.textContent = "Apply for open hospitality shifts";
    benefit3.textContent = "Build reliability as you complete work";
  } else if (userType === "operator") {
    eyebrow.textContent = "Operator Account";
    title.textContent = "Find better staff, faster.";
    description.textContent =
      "Post shifts, match with available workers, and invite staff based on role, distance, and reliability.";

    benefit1.textContent = "Post shifts for your venues";
    benefit2.textContent = "Invite matched available workers";
    benefit3.textContent = "Track completed shifts and reliability";
  } else {
    eyebrow.textContent = "Join Disco";
    title.textContent = "Create your hospitality profile.";
    description.textContent =
      "Choose whether you're joining as staff or an operator. Disco will show the right setup flow for you.";

    benefit1.textContent = "Staff can set availability and accept shifts";
    benefit2.textContent = "Operators can post shifts and find matched workers";
    benefit3.textContent = "Reliability grows as shifts are completed";
  }
}

function toggleFormType(userType) {
  const staffForm = document.getElementById("staff-form");
  const operatorForm = document.getElementById("operator-form");

  if (staffForm) {
    staffForm.style.display = userType === "staff" ? "block" : "none";
  }

  if (operatorForm) {
    operatorForm.style.display = userType === "operator" ? "block" : "none";
  }

  updateRegisterHero(userType);
}

document.addEventListener("DOMContentLoaded", function () {
  const userTypeSelect = document.getElementById("user_type");

  if (userTypeSelect) {
    const initialUserType =
      userTypeSelect.dataset.userType || userTypeSelect.value || "";

    userTypeSelect.value = initialUserType;
    toggleFormType(initialUserType);
  }
});