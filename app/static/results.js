function init_table() {
    var $table = $('#table');
    var $dl = $('#download');

    $table.bootstrapTable({
	cache: false,
     	columns: [
	    {
                field: 'state',
                checkbox: true,
                align: 'center'
            },{
		title: 'File Name',
		field: 'name',
		align: 'center',
		sortable: true
	    }, {
		visible: false,
		title: 'Path',
		field: 'path',
	    }
	]
    });
    $table.on('check.bs.table uncheck.bs.table ' +
         'check-all.bs.table uncheck-all.bs.table', function () {
             $dl.prop('disabled',
                         !$table.bootstrapTable('getSelections').length);
             $table.data('selections', getIdSelections());
         });
    
    function getIdSelections() {
        return $.map($table.bootstrapTable('getSelections'), function (row) {
            return row['path'];
        });
    }
}

$(function() {
    init_table();
    
});
