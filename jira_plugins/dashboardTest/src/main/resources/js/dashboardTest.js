/**
 * @file
 * Functionality of the performance warnings dashboard.
 */

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

/**
 * Creates an HTML <a> element linking to the given user.
 * 
 * @param {String} username
 *   The username (may not contain "@")
 */
function _create_user_link(username) {
    if (username.includes("@")) {
        throw "user_name may not contain \"@\"";
    }

    var a = document.createElement("A");
    a.setAttribute("target", "_parent");
    a.setAttribute("href", "/jira/secure/ViewProfile.jspa?name=" + username)
    a.className = "alert-link";
    a.innerHTML = "@" + username;

    return a;
}

function populate() {
    // 1. Load warnings
    console.error("WARNINGS ARE CURRENTLY FAKE!")
    var warnings = [
        { level: "danger", text: "(!) Debug code – warnings are fake (!)" },
        { level: "warning", text: _create_user_link("frauke") + "worked overtime three days in a row." },
        { level: "danger", text: _create_user_link("admin") + "has violated the policy \"no-work-during-holidays\"!" },
        { level: "danger", text: _create_user_link("frauke") + "worked overtime five days in a row." },
        { level: "warning", text: "There are 10 open and overdue tasks!" },
    ];

    var alertlist = document.querySelector("#alertlist");

    // 2. Remove "Loading..." placeholder
    if (alertlist.childElementCount != 1) {
        throw "Invalid DOM state!";
    }
    alertlist.removeChild(alertlist.children[0]);

    // 3. Populate interface
    warnings.forEach(function(warning) {
        var warning_alert = _create_alert(warning.level, warning.text);
        alertlist.appendChild(warning_alert);
    });
};

// This script is run after the document has loaded
populate();