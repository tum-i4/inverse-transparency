/**
 * @file
 * Functionality of the performance warnings dashboard.
 */

function populate() {
    throw "NOT IMPLEMENTED";
};

/**
 * Creates an HTML <div> element styled as an alert with the given level and text.
 * 
 * @param {String} warning_level
 *   Either "warning" or "danger"
 * @param {String} warning_text
 *   The text to appear on the warning
 */
function _create_alert(warning_level, warning_text) {
    // Invalid warning_level
    if (["warning", "danger"].indexOf(warning_level) < 0) {
        throw "Invalid warning level";
    }

    var alert = document.createElement("DIV");
    alert.className = "alert alert-" + warning_level;
    alert.setAttribute("role", "alert");
    alert.innerHTML = warning_text;

    return alert;
};

// This script is run after the document has loaded
populate();