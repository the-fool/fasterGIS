function init_task_table() {
    var $table=$('#table');
    var $add = $('#add-task');
    var $stop = $('#stop-task');
    var uid = $table.data('uid');
    var selections = [];

    $('#student-list-table').bootstrapTable({
        cache: false,
        height: 350,
        id: 'id',
	url: '/api/tasks?filter=uid_'+uid,
        columns: [
            {
                field: 'state',
                checkbox: true,
                align: 'center'
            }, {
                title: 'ID',
                field: 'id',
                align: 'center',
                sortable: true
            }, {
                title: 'Hash',
                field: 'task_id',
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
});
