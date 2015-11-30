function init_task_table() {
    var $table=$('#table');
    var $add = $('#add-task');
    var $stop = $('#stop-task');
    var uid = $table.data('uid');
    var selections = [];

    $table.bootstrapTable({
        cache: false,
        height: 350,
        id: 'task_id',
	detailView: true,
	url: '/api/tasks?filter=uid_'+uid,
        columns: [
            {
                field: 'state',
                checkbox: true,
                align: 'center'
            }, {
                title: 'ID',
                field: 'id',
		visible: false,
		align: 'center',
                sortable: true
            }, {
		title: 'Name',
		field: 'name',
		align: 'center',
		sortable: true
	    }, {
		title: 'Started',
		field: 'date_begun',
		align: 'center',
		sortable: true
	    }, {
                title: 'Hash',
                field: 'task_id',
                align: 'center',
             
            }, {
                title: 'Status',
                field: 'status',
                align: 'center',
                sortable: true
            }]
        });

    $table.on('check.bs.table uncheck.bs.table ' +
         'check-all.bs.table uncheck-all.bs.table', function () {
             $add.prop('disabled', 
		       $table.bootstrapTable('getSelections').length);
             $stop.prop('disabled', 
			 !$table.bootstrapTable('getSelections').length);
	     $table.data('selections', getIdSelections());
         });
    
    $stop.click(function() {
	var data = {'tid': getIdSelections()};
	$.ajax({
	    url: '/api/shutdown',
	    contentType: 'application/json',
	    method: 'POST',
	    data: JSON.stringify(data),
	    success: function(d,s) {
		console.log('data:' + d);
		console.log('status:' + s);
	    },
	    error: function() {
		alert("error");
	    }	      
	});
    });

    function getIdSelections() {
        return $.map($table.bootstrapTable('getSelections'), function (row) {
            return row['task_id'];
        });
    }
}

$(function() {
    init_task_table();
    
    $('#table').on('expand-row.bs.table', function(e, index, row, $detail) {
	console.log("clicked");
	$detail.html('<div class="well status-well"><div class="row"><div class="col-md-12"><h4 class="update-text"></h4></div></div><div class="progress"><div class="progress-bar progress-bar-striped active" role="progressbar" aria-valuenow="40" aria-valuemin="0" aria-valuemax="100" style="width:40%">Place holder</div></div><table></table></div>').find('table').bootstrapTable({
	    columns: [{
		title: 'Time',
		field: 'time',
		align: 'center',
		sortable: true
	    }, {
		title: 'Log',
		field: 'log',
		align: 'left'
	    }],
	    data: [{
		time: '1:03',
		log: 'it started'
	    }, {
		time: '1:04',
		log: 'it went'
	    }]
	});
	var $progbar = $detail.find('.progress-bar');
	var $progtext = $detail.find('.update-text');
	var progress_url = '/tasks/simul_status/'+ row['task_id'];
	update_progress(progress_url, $progbar, $progtext);
    });
    $('table').on('click-row.bs.table', function(e,row,$tr) {
        $tr.find('>td>.detail-icon').trigger('click');
    });

});

function update_progress(url, $pbar, $uptext) {
    $.getJSON(url, function(data) {
	if (isNaN(data['current'])) { 
	    percent = 0;
	    $pbar.text("Pending . . . ");
	    $uptext.text("Task is pending");
	} else {
	    percent = parseInt(data['current'] * 100 / data['total']);
	    $pbar.css('width', percent+'%').attr('aria-valuenow', percent);
	    $uptext.text(data['current'] + " out of " + data['total']);
	    $pbar.text(percent + "%");
	}
	if (data['state'] != 'PENDING' && data['state'] != 'PROGRESS') {
            if ('result' in data) {
                $pbar.text('Result: ' + data['result']);
            }
            else {
		$(status_div.childNodes[3]).text('Result: ' + data['state']);
            }
        }
        else {
            setTimeout(function() {
                update_progress(url, $pbar, $uptext);
            }, 2000);
        }
    });
}
