function start_task() {
    div = $('<div class="progress"></div>');
    $('#progress').append(div);
    $.ajax({
        type: 'POST',
        url: '/foo',
        success: function(data, status, request) {
            status_url = request.getResponseHeader('Location');
            update_progress(status_url, div[0]);
        },
        error: function() {
            alert('Unexpected error');
        }
    });
}

function update_progress(status_url, status_div) {
    $.getJSON(status_url, function(data) {
        $(status_div).text(data['current']);
	if (data['state'] != 'PENDING' && data['state'] != 'PROGRESS') {
            if ('result' in data) {
                $(status_div).text('Result: ' + data['result']);
             }
            else {
		$(status_div).text('Result: ' + data['state']);
            }
        }
        else {
            setTimeout(function() {
                update_progress(status_url, status_div);
            }, 2000);
        }
    });
}
$(function() {
    $('#start-bg-job').click(start_task);
});
