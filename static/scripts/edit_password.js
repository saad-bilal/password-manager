// Function to update the password based on user's selection
function updatePassword(event) {
    var passwordTypeSelect = document.getElementById("password_type");
    var randomPasswordOptions = document.getElementById("random_password_options");
    var passphraseOptions = document.getElementById("passphrase_options");
    var lengthInput = document.getElementById("length");

    if (passwordTypeSelect.value == "random") {
        randomPasswordOptions.style.display = "block";
        passphraseOptions.style.display = "none";
        lengthInput.value = Math.max(16, Math.min(64, Number(lengthInput.value)));  // Ensure length is within valid range
        updateRandomPassword();
    } else if (passwordTypeSelect.value == "passphrase") {
        randomPasswordOptions.style.display = "none";
        passphraseOptions.style.display = "block";
        lengthInput.value = Math.max(3, Math.min(10, Number(lengthInput.value)));  // Ensure length is within valid range
        updatePassphrase();
    } else {
        randomPasswordOptions.style.display = "none";
        passphraseOptions.style.display = "none";
        document.getElementById("password").value = "";
    }
}

// Function to validate the length of the password
function validateLength(min, max) {
    var lengthInput = document.getElementById("length");
    var length = parseInt(lengthInput.value, 10);
    if (length < min) {
        lengthInput.value = min;
    } else if (length > max) {
        lengthInput.value = max;
    }
}

// Function to update the random password
function updateRandomPassword() {
    var xhr = new XMLHttpRequest();
    xhr.open("POST", "/generate_password", true);
    xhr.setRequestHeader("Content-Type", "application/x-www-form-urlencoded");

    xhr.onload = function () {
        handlePasswordResponse(this);
    };

    var params =
        "length=" + encodeURIComponent(document.getElementById("length").value) +
        "&use_random_password=1" +
        (document.getElementById("include_uppercase").checked ? "&include_uppercase=1" : "") +
        (document.getElementById("include_lowercase").checked ? "&include_lowercase=1" : "") +
        (document.getElementById("include_numbers").checked ? "&include_numbers=1" : "") +
        (document.getElementById("include_special").checked ? "&include_special=1" : "");

    xhr.send(params);
}

// Function to update the passphrase
function updatePassphrase() {
    var xhr = new XMLHttpRequest();
    xhr.open("POST", "/generate_password", true);
    xhr.setRequestHeader("Content-Type", "application/x-www-form-urlencoded");

    xhr.onload = function () {
        handlePasswordResponse(this);
    };

    var params =
        "length=" + encodeURIComponent(document.getElementById("length").value) +
        "&use_passphrase=1" +
        (document.getElementById("capitalize").checked ? "&capitalize=1" : "") +
        (document.getElementById("add_numbers").checked ? "&add_numbers=1" : "") +
        "&separator=" + encodeURIComponent(document.getElementById("separator").value);

    xhr.send(params);
}

// Function to handle the password response
function handlePasswordResponse(xhr) {
    if (xhr.status === 200) {
        try {
            var response = JSON.parse(xhr.responseText);
            document.getElementById("password").value = response.password;

            // Update password strength
            updatePasswordStrength();
        } catch (error) {
            console.error("Error parsing JSON response:", error);
        }
    } else {
        console.error("Request failed with status:", xhr.status);
    }
}

// Event listener for the window load event
window.addEventListener("load", function () {
    // Determine the existing password type (random or passphrase) and set the UI accordingly
    var existingPasswordType = document.getElementById("password_type").value;
    var randomPasswordOptions = document.getElementById("random_password_options");
    var passphraseOptions = document.getElementById("passphrase_options");
    var lengthInput = document.getElementById("length");

    if (existingPasswordType === "random") {
        randomPasswordOptions.style.display = "block";
        passphraseOptions.style.display = "none";
        lengthInput.value = 16;  // Set default length for random password
    } else if (existingPasswordType === "passphrase") {
        randomPasswordOptions.style.display = "none";
        passphraseOptions.style.display = "block";
        lengthInput.value = 3;   // Set default length for passphrase
    }

    // Trigger the updatePassword function to set the UI based on the existing password type
    updatePassword();
    // Call updatePasswordStrength to update the password strength based on the initial password
    updatePasswordStrength();

    // Call updatePasswordStrength whenever the password input field changes
    document.getElementById("password").addEventListener("input", updatePasswordStrength);
});

// Function to update the password strength
function updatePasswordStrength() {
    var password = document.getElementById("password").value;
    // Estimate the strength of the password
    var estimation = zxcvbn(password);

    // Update password strength indicator
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