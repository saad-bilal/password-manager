// This function is used to filter passwords based on their type
function filterPasswords() {
    // Get the password type from the HTML element with id "password_type"
    var passwordType = document.getElementById("password_type").value;
    // Redirect the window location to the view_passwords page with the selected password type as a query parameter
    window.location.href = "/view_passwords?password_type=" + passwordType;
}