// Function to update the password based on user's selection
function updatePassword(event) {
    var passwordTypeSelect = document.getElementById("password_type");
    var randomPasswordOptions = document.getElementById("random_password_options");
    var passphraseOptions = document.getElementById("passphrase_options");
    var lengthInput = document.getElementById("length");

    if (passwordTypeSelect.value == "random") {
        randomPasswordOptions.style.display = "block";
        passphraseOptions.style.display = "none";
        lengthInput.value = Math.max(16, Math.min(64, lengthInput.value));
        updateRandomPassword();
    } else if (passwordTypeSelect.value == "passphrase") {
        randomPasswordOptions.style.display = "none";
        passphraseOptions.style.display = "block";
        lengthInput.value = Math.max(3, Math.min(10, lengthInput.value));
        updatePassphrase();
    } else {
        randomPasswordOptions.style.display = "none";
        passphraseOptions.style.display = "none";
        document.getElementById("password").value = "";
    }
}

// Function to generate a random password
function updateRandomPassword() {
    var xhr = new XMLHttpRequest();
    xhr.open("POST", "/generate_password", true);
    xhr.setRequestHeader("Content-Type", "application/x-www-form-urlencoded");

    xhr.onload = function () {
        handlePasswordResponse(this);
    };

    var params =
        "length=" + encodeURIComponent(document.getElementById("length").value || 16) +
        "&use_random_password=1" +
        (document.getElementById("include_uppercase").checked ? "&include_uppercase=1" : "") +
        (document.getElementById("include_lowercase").checked ? "&include_lowercase=1" : "") +
        (document.getElementById("include_numbers").checked ? "&include_numbers=1" : "") +
        (document.getElementById("include_special").checked ? "&include_special=1" : "");

    xhr.send(params);
}

// Function to generate a passphrase
function updatePassphrase() {
    var xhr = new XMLHttpRequest();
    xhr.open("POST", "/generate_password", true);
    xhr.setRequestHeader("Content-Type", "application/x-www-form-urlencoded");

    xhr.onload = function () {
        handlePasswordResponse(this);
    };

    var params =
        "length=" + encodeURIComponent(document.getElementById("length").value || 3) +
        "&use_passphrase=1" +
        (document.getElementById("capitalize").checked ? "&capitalize=1" : "") +
        (document.getElementById("add_numbers").checked ? "&add_numbers=1" : "") +
        "&separator=" + encodeURIComponent(document.getElementById("separator").value);

    xhr.send(params);
}

// Function to handle the response from the server
function handlePasswordResponse(xhr) {
    if (xhr.status === 200) {
        try {
            var response = JSON.parse(xhr.responseText);
            document.getElementById("password").value = response.password;
            updatePasswordStrength();
        } catch (error) {
            console.error("Error parsing JSON response:", error);
        }
    } else {
        console.error("Request failed with status:", xhr.status);
    }
}

window.addEventListener("load", function () {
    updatePassword();

    // Call updatePasswordStrength to update the password strength based on the initial password
    updatePasswordStrength();

    // Call updatePasswordStrength whenever the password input field changes
    document.getElementById("password").addEventListener("input", updatePasswordStrength);
});

// Function to update the password strength
function updatePasswordStrength() {
    var password = document.getElementById("password").value;
    var estimation = zxcvbn(password);

    var passwordStrengthElement = document.getElementById("password_strength");
    if (estimation.score <= 1) {
        passwordStrengthElement.textContent = "Password strength: Very weak";
        passwordStrengthElement.style.color = "darkred";
    } else if (estimation.score <= 2) {
        passwordStrengthElement.textContent = "Password strength: Weak";
        passwordStrengthElement.style.color = "red";
    } else if (estimation.score <= 3) {
        passwordStrengthElement.textContent = "Password strength: Medium";
        passwordStrengthElement.style.color = "goldenrod";
    } else {
        passwordStrengthElement.textContent = "Password strength: Strong";
        passwordStrengthElement.style.color = "darkgreen";
    }
}