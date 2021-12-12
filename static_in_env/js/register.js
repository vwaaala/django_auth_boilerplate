const usernameField = document.querySelector('#usernameField');
const feedBackFeedUsername = document.querySelector(".username");

const emailField = document.querySelector('#emailField');
const feedBackFeedEmail = document.querySelector('.email');

const passwordField = document.querySelector('#passwordField');
const showPasswordToggle = document.querySelector('.showPasswordToggle');

const submitBtn = document.querySelector('.submit-btn');

const handleShowPasswordToggle = (event) => {
    if (showPasswordToggle.textContent === 'Show password') {
        showPasswordToggle.textContent = 'Hide password';
        passwordField.setAttribute("type", "text");
    } else {
        showPasswordToggle.textContent = 'Show password';
        passwordField.setAttribute("type", "password");
    }

};

usernameField.addEventListener('keyup', (event) => {
    // catch username value from input field
    const username = event.target.value;

    usernameField.classList.remove("is-invalid");
    feedBackFeedUsername.style.display = "none";

    if (username.length > 0) {
        // make api call
        fetch('/authentication/validate-username', {
            body: JSON.stringify({username: username}),
            method: 'POST',

        })
            .then((response) => response.json())
            .then((data) => {
                if (data.username_error) {
                    submitBtn.disabled = true;
                    usernameField.classList.add("is-invalid");
                    feedBackFeedUsername.style.display = 'block';
                    feedBackFeedUsername.innerHTML = `<p>${data.username_error}</p>`;
                } else {
                    submitBtn.removeAttribute("disabled");
                }
            })
    }
});

emailField.addEventListener('keyup', (event) => {
    const email = event.target.value;

    emailField.classList.remove('is-invalid');
    feedBackFeedEmail.style.display = 'none';

    if (email.length > 0) {
        fetch('/authentication/validate-email', {
            body: JSON.stringify({email: email}),
            method: 'POST',
        })
            .then((response) => response.json())
            .then((data) => {
                if (data.email_error) {
                    submitBtn.disabled = true;
                    emailField.classList.add('is-invalid');
                    feedBackFeedEmail.style.display = 'block';
                    feedBackFeedEmail.innerHTML = `<p>${data.email_error}</p>`
                } else {
                    submitBtn.removeAttribute("disabled");
                }
            })
    }
});

showPasswordToggle.addEventListener('click', handleShowPasswordToggle);