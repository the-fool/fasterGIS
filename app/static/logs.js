function init_table() {
    var $table = $('#table');
    $table.bootstrapTable({
	cache: false,
	columns: [
	    {
		title: 'Time',
		field: 'time',
		align: 'center',
		sortable: true
	    }, {
		title: 'Output',
		field: 'text',
		align: 'left',
		sortable: true
	    }]
    });
}

$(function() {
    init_table();
    
});
