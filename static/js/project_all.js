$('document').ready(function() {
    $.ajax({
        type: 'GET',
        url: 'project_list_all',
        success: function (data) {
            $(".potrr").html(data.html_project_list);
        },
        error: function(data) {
            $(".potrr").html("Something went wrong!");
        }
    });
});