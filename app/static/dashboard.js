function init_task_table() {
    var $table=$('#table');
    var $add = $('#add-task');
    var $stop = $('#stop-task');
    var uid = $table.data('uid');
    var selections = [];

    $table.bootstrapTable({
        cache: false,
        height: 350,
        id: 'id',
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
                  $add.prop('disabled', !$table.bootstrapTable('getSelections').length);
                  $table.data('selections', getIdSelections());
              });

    function getIdSelections() {
        return $.map($table.bootstrapTable('getSelections'), function (row) {
            return row['id'];
        });
    }
}

$(function() {
    init_task_table();
    $('#table').on('expand-row.bs.table', function(e, index, row, $detail) {
	console.log("clicked");
	$detail.html('<div class="well inset-well"><div class="progress"><div class="progress-bar progress-bar-striped active" role="progressbar" aria-valuenow="40" aria-valuemin="0" aria-valuemax="100" style="width:40%">Place holder</div></div><table></table></div>').find('table').bootstrapTable({
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
	$detail.find('.progress-bar').text(row['task_id']);
    });
    $('table').on('click-row.bs.table', function(e,row,$tr) {
        $tr.find('>td>.detail-icon').trigger('click');
    });

});
