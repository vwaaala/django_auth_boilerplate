const usernameField = document.querySelector('#usernameField');
const feedBackFeedUsername = document.querySelector(".username");

const emailField = document.querySelector('#emailField');
const feedBackFeedEmail = document.querySelector('.email')

usernameField.addEventListener('keyup', (event)=>{
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
                    usernameField.classList.add("is-invalid");
                    feedBackFeedUsername.style.display = 'block';
                    feedBackFeedUsername.innerHTML = `<p>${data.username_error}</p>`;
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
                emailField.classList.add('is-invalid');
                feedBackFeedEmail.style.display = 'block';
                feedBackFeedEmail.innerHTML = `<p>${data.email_error}</p>`
            }
        })
    }
})