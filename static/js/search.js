$('#search_here').keyup(function () {
        $.ajax({
            type: 'GET',
            url: 'search',
            data: {
                q: $('input[id=search_here]').val()
            },
            success: function (data) {
                $(".potrr").empty();
                $(".potrr").html(data.html_project_list);
            },
            error: function(data) {
                $(".potrr").html("Something went wrong!");
            }
        });
    });