function init_task_table() {
    var $table=$('#table');
    var $add = $('#add-task');
    var $stop = $('#stop-task');
    var uid = $table.data('uid');
    var selections = [];

    $table.bootstrapTable({
        cache: false,
	showExport: true,
	exportTypes: ['json','xml','csv','txt'],
//	height: 350,
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
                title: 'Type',
                field: 'type',
                align: 'center',
                sortable: true
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
    $table.on('load-success.bs.table', function() {
	$add.prop('disabled', false);
	$stop.prop('disabled', true);
    });
    
}

$(function() {
    init_task_table();
    
    $('#table').on('expand-row.bs.table', function(e, index, row, $detail) {
	$detail.html('<div class="well status-well"><div class="row"><div class="col-md-12"><h4 class="update-text"></h4></div></div><div class="progress"><div class="progress-bar progress-bar-striped active" role="progressbar" aria-valuenow="40" aria-valuemin="0" aria-valuemax="100" style="width:40%">Waiting . . .</div></div><div class="row text-center"><button class="btn btn-large btn-info logs"><i class="glyphicon glyphicon-book"></i> &nbsp Logs</button>&nbsp &nbsp <button class="btn btn-large btn-success results"><i class="glyphicon glyphicon-download-alt"></i> &nbsp Results</button></div></div></div>')

	var $progbar = $detail.find('.progress-bar');
	var $progtext = $detail.find('.update-text');
	var progress_url = '/tasks/simul_status/'+ row['task_id'];
	update_progress(progress_url, $progbar, $progtext);

	$detail.find('.logs').click(function() {
	    location.href = "logs/" + row['task_id'];
	});
	$detail.find('.results').click(function() {
	    location.href = "results/" + row['task_id'];
	});
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
	console.log(percent);
	if (data['state'] != 'PENDING' && data['state'] != 'PROGRESS') {
            console.log(data['status']);
	    if ('result' in data) {
                $uptext.text('Result: ' + data['status'] + ' at ' + 
			     data['current'] + ' out of ' + data['total'] +
			     ' simulations.');
		$pbar.css('width', percent+'%');
		$pbar.text(percent+'%');
		if (data['status']=='CANCELLED') {
		    $pbar.addClass('progress-bar-danger'); 
		} else if (data['status']=='FINISHED') {
		    $pbar.addClass('progress-bar-success');
		}
	    }
            else {
		$uptext.text('Result: ' + data['state']);
            }
        }
        else {
            setTimeout(function() {
                update_progress(url, $pbar, $uptext);
            }, 2000);
        }
    });
}
