/**
 * @file
 * Functionality of the performance warnings dashboard.
 */

function warn_overseer(data_owner_id, affected_data) {
    if (!currentUser) {
        fetch("/jira/rest/auth/1/session")
            .then(function (r) {
                if (r.ok) {
                    return r.json();
                } else {
                    console.error("JIRA API call failed");
                    return "undefined";
                }
            })
            .then(function (rJson) {
                if (!rJson) {
                    currentUser = "NOT_SET";
                } else {
                    currentUser = rJson.name;
                }

                // Reentrance after completion
                warn_overseer(data_owner_id, affected_data);
            });

        // Reentrance happens in the callback
        return;
    }

    var formData = new FormData();
    formData.append("do", data_owner_id);
    formData.append("du", currentUser);
    formData.append("app", "jira");
    formData.append("data", affected_data);

    var fetchBody = {
        method: "POST",
        mode: "no-cors",
        body: formData
    };

    // TODO: Adapt URL
    const fetchUrl = "http://localhost:5000/see";

    fetch(fetchUrl, fetchBody);
};

/**
 * Creates an HTML <div> element styled as an alert with the given level and text.
 * 
 * @param {String} warning_level
 *   Either "warning" or "danger"
 * @param {Array} warning_text_children
 *   The HTML elements describing the warning text.
 */
function _create_alert(warning_level, warning_text_children) {
    // Invalid warning_level
    if (["warning", "danger"].indexOf(warning_level) < 0) {
        throw "Invalid warning level";
    }

    var alert = document.createElement("DIV");
    alert.className = "alert alert-" + warning_level;
    alert.setAttribute("role", "alert");
    warning_text_children.forEach(function (warning_text_child) {
        alert.appendChild(warning_text_child);
    });

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
    a.setAttribute("href", "/jira/secure/ViewProfile.jspa?name=" + username);
    a.className = "alert-link";
    a.innerHTML = "@" + username;

    warn_overseer(username, "?? TODO ??");

    return a;
}

/** Creates an HTML <span> element containing the given text. */
function _span(text) {
    var s = document.createElement("SPAN");
    s.innerHTML = text;
    return s;
}

function populate() {
    // 1. Load warnings
    console.error("WARNINGS ARE CURRENTLY FAKE!");
    var warnings = [
        { level: "danger", children: [_span("(!) Debug code – warnings are fake (!)")] },
        { level: "warning", children: [_create_user_link("frauke"), _span(" worked overtime three days in a row.")] },
        { level: "danger", children: [_create_user_link("admin"), _span(" has violated the policy \"no-work-during-holidays\"!")] },
        { level: "danger", children: [_create_user_link("frauke"), _span(" worked overtime five days in a row.")] },
        { level: "warning", children: [_span("There are 10 open and overdue tasks!")] },
    ];

    var alertlist = document.querySelector("#alertlist");

    // 2. Remove "Loading..." placeholder
    if (alertlist.childElementCount != 1) {
        throw "Invalid DOM state!";
    }
    alertlist.removeChild(alertlist.children[0]);

    // 3. Populate interface
    warnings.forEach(function (warning) {
        var warning_alert = _create_alert(warning.level, warning.children);
        alertlist.appendChild(warning_alert);
    });
};

function recalculate_height() {
    console.error("NOT IMPLEMENTED: recalculate_height()");
}

// This script is run after the document has loaded
populate();
recalculate_height();
