var check_patterns = [
    '<generator>https://getnikola.com/</generator>',         // v7.6.1
    '<generator>http://getnikola.com/</generator>',          // v7.0.0
    '<generator>Nikola <http://getnikola.com/></generator>', // v6.3.0
    '<generator>nikola</generator>'                          // v6.2.1
];

var check_versions = [
    'v7.6.1 or newer',
    'v7.0.0–v7.6.0',
    'v6.3.0–v6.4.0',
    'v6.2.1'
];

function report_link_change(out) {
    $("#check-output").append('<p class="text-warning"><i class="fa fa-warning"></i> ' + out + '</p>');
}

function prepare_link_for_checking(link) {
    if (link.substring(link.length - 10) == "index.html") {
        link = link.substring(0, link.length - 10);
        report_link_change("Stripped <code>index.html</code> from link.");
    } else if (link.substring(link.length - 7) == "rss.xml") {
        // What we actually need.
        return link;
    } else if (link.charAt(link.length - 1) != "/") {
        link = link + "/";
        report_link_change("Added trailing <code>/</code> to link.");
    }
    // We check the RSS, which contains a nice <generator> tag.
    link = link + "rss.xml";
    return link;
}

$(document).ready(function() {
    $("#check-form").submit(function(event) {
        link = $("#check-url").val();
        if (link !== "") {
            $("#check-output").html("<h2>Results</h2><p>Checking site: <code>" + link + "</code>…</p>");
            link = prepare_link_for_checking(link);
        }
        // Dear W3C: fuck you.
        $.getJSON('https://users.getnikola.com/api/check?url=' + encodeURIComponent(link), function(out) {
            if (out.type === "result") {
                result = out.data;
                if (result === -1) {
                    $("#check-output").append('<p class="text-danger"><i class="fa fa-times fa-2x"></i> This is not a Nikola site.</p>');
                } else {
                    ver = check_versions[result];
                    $("#check-output").append('<p class="text-success"><i class="fa fa-check fa-2x"></i> This is a Nikola site, generated using Nikola ' + ver + '.</p>');
                }
            } else {
                $("#check-output").append('<p class="text-danger"><i class="fa fa-warning fa-2x"></i> This is not a Nikola site, or it failed to load. ' + out.data + '</p>');
            }
        }).fail(function() {
            $("#check-output").append('<p class="text-danger"><i class="fa fa-warning fa-2x"></i> Accessing the API failed.</p>');
        });
    event.preventDefault();
});
});
