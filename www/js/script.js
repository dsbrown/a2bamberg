
var videoTagTemplate = 
	'<video class="video-js vjs-default-skin" controls width="100" height="100" preload="false" data-setup="{}">' +
	   '<source type="video/mp4" src="{url}">' +
	'</video>';

$(document).ready(function(){

	_initializeVideosList();
	_initializeRateButton();
	_initializeDeleteButton();
	
});

function _initializeVideosList() {
	if ($('#videos').length == 0) return;
	refreshList();
}

function _initializeRateButton() {
	$('#videos').on('click', '.rate', function() {
		$this = $(this);
		$.ajax({
			type: "POST",
			url:'/api/rate',
			dataType:"json",
			data: {
				"id": $this.parents('tr').data('id'),
				"rating": $this.parents('tr').find('.rate-scale').val()
			},
			success:function(d) {
				$this.parents('tr').find('.rate-scale, .rate').attr('disabled','disabled');
				$this.parents('tr').find('.rating').html(Math.round(d.new_rating*10)/10 + ' / 5');
			},
			error: function(d) {
				alert('An ajax error occurred: ' + d.responseText);
			}
		});
	});
}

function _initializeDeleteButton() {
	$('#videos').on('click', '.delete', function() {
		$this = $(this);
		if (confirm("Are you sure you want to delete this video?")) {
			$.ajax({
				type: "POST",
				url:'/api/delete',
				dataType:"json",
				data: {
					"id": $this.parents('tr').data('id')
				},
				error: function(d) {
					alert('An ajax error occurred: ' + d.responseText);
				},
				complete:function() {
					refreshList();
				}
			});
		}
	});
}

function refreshList() {
	$.ajax({
		url:'/api/list',
		dataType:"json",
		success:function(d){
			console.log(d);
			$('#videos tbody').html(''); // Clear existing data
			$.each(d, function() {
				$('#videos tbody').append('<tr data-id="' + this.id + '"><td>' 
					//+ videoTagTemplate.replace('{url}', this.s3_url) 
					//+ '</td><td>' 
					+ '<a href="/api/item/{id}">{name}</a>'.replace('{id}', this.id).replace('{name}', this.name)
					+ '</td><td class="rating">' + Math.round(this.rating*10)/10 + ' / 5'
					+ '</td><td class="inline"><select class="rate-scale" style="width: 50px;"><option>1</option><option>2</option><option>3</option><option>4</option><option>5</option></select>' 
					+ '</td><td><button class="btn rate">Submit Rating</button>'
					+ '</td><td><button class="btn btn-danger delete">Delete</button>'
					+ '</td></tr>');
			});
		},
		error: function(d) {
			alert('An ajax error occurred: ' + d.responseText);
		}
	});
}