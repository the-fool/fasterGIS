function start_task() {
    div = $('<div class="cel_progress"></div><div><button id="input-foo">Scale Foo</button><br>');
    $('#progress').append(div);
    $.ajax({
        type: 'POST',
        url: '/tasks/foo',
        success: function(data, status, request) {
            status_url = request.getResponseHeader('Progress');            
	    $('#input-foo').data('url', request.getResponseHeader('Input'))
		.click(signal_foo);
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
function signal_foo() {
    console.log("signalling");
    url = $(this).data('url');
    $.ajax({
        type: 'POST',
        url: url,
        success: function(data, status, request) {
            console.log("success");
	},
        error: function() {
            alert('Unexpected error');
        }
    });
}
$(function() {
    $('#start-bg-job').click(start_task);
});
