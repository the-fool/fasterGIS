function init_table() {
    var $table = $('#table');
    $table.bootstrapTable({
	cache: false,
	showExport: true,
        exportTypes: ['json','xml','csv','txt'],
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
