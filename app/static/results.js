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
    $dl.click(function() {
	console.log(getIdSelections());
	var data = {'path': getIdSelections()};
	$.ajax({
	    url: '/api/zip_results',
	    contentType: 'application/json',
	    method: 'POST',
	    data: JSON.stringify(data),
	    success: function(d,s) {
		console.log(d);
		window.location.href = '/api/download/' + d['fname'];
	    },
	    error: function() {
		alert("unexpected error");
	    }
	});
    });
    function getIdSelections() {
        return $.map($table.bootstrapTable('getSelections'), function (row) {
            return row['path'];
        });
    }
}

$(function() {
    init_table();
    $('#table').on('click-row.bs.table', function(e, row, $element){
	console.log(e); console.log(row); console.log($element);
	var $mod = $('#img-modal');
	var src = 'img/' + row['name'];
	$mod.find('img').attr("src", src);
	$mod.modal('show');
	
    });
});
