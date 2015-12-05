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
	sortName: 'date_begun',
	sortOrder: 'desc',
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
		title: 'Ended',
		field: 'date_done',
		align: 'center',
		sortable: true
	    }, {
                title: 'Hash',
                field: 'task_id',
                align: 'center',
             
            }, {
                title: 'Type',
                field: 'simtype',
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
	     set_tr();
         });

    $stop.click(function() {
	var data = {'tid': getIdSelections()};
	$('tr.selected').each(function() {
	    var $that = $(this).find('td').last()
	    if (($that.text() === "PENDING") || ($that.text() === "PROGRESS")) 
		{ $that.text("Shutting down"); }
	});
	
	$.ajax({
	    url: '/api/shutdown',
	    contentType: 'application/json',
	    method: 'POST',
	    data: JSON.stringify(data),
	    success: function(d,s) {
		$('tr').removeClass('selected');
		$table.bootstrapTable('uncheckAll');
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
	set_tr();
	$table.find('td:contains("PENDING"), td:contains("PROGRESS")').each(update_status);
    });
    $table.on('reset-view.bs.table', function() {
	set_tr();
    });
}

function set_tr() {
    $('tr:contains("CANCELLED")').css("background-color", "#E6C4C4");
    $('tr:contains("FINISHED")').css("background-color", "#4EA050");
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

function update_status(i, $e) {
    console.log(i); console.log($e);
}

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
	    if ('result' in data) {
                $uptext.text('Result: ' + data['status'] + ' at ' + 
			     data['current'] + ' out of ' + data['total'] +
			     ' simulations.');
		$pbar.css('width', percent+'%');
		$pbar.text(percent+'%');
		if (data['status']=='CANCELLED') {
		    $pbar.removeClass('active progress-bar-striped')
			.addClass('progress-bar-danger'); 
		} else if (data['status']=='FINISHED') {
		    $pbar.removeClass('active progress-bar-striped')
			.addClass('progress-bar-success');
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
