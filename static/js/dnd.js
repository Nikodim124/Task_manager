var modal = document.getElementById("myModal");

function details(element) {
  det = $(element);
  modal.style.display = 'block';
  $("#modal-response").empty();
  $.ajax({
        type: 'GET',
        url: det.attr('data-url'),
        success: function (data) {
            $('#modal-response').empty();
            $('#modal-response').html(data.html_form);
        },
        error: function(data) {
            location.href = 'error';
        }
  });
};

window.onclick = function(event) {
  if (event.target == modal) {
    modal.style.display = "none";
  }
}

$('#new').click(function() {
    modal.style.display = "block";
});

function foo(obj) {
    setTimeout(function() {
        location.href = 'contracts';
    }, 2000);
}

$("#status_field").change( function(){
    form = $(this);
    var status = $("#status_field").val();
    $.ajax({
        url: $('#st_status').attr('data-url'),
        data: {'status': status},
        dataType: 'json',
        success: function (data) {
          $('.modal_curator_form').empty();
          $.each(data.data, function(first_name, last_name) {
            $('.modal_curator_form').append($('<option/>', {
                value: last_name.id,
                text: last_name.first_name+' '+last_name.last_name
            }));
          });
        }
    });
});
