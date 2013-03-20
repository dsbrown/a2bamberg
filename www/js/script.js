// Url for videos JSON
var videoJsonUrl = 'videos.json';

$(document).ready(function(){

	_initializeVideosList();
	
});

function _initializeVideosList() {
	if ($('#videos').length == 0) return;
	$.ajax({
		url:videoJsonUrl,
		dataType:"json",
		success:function(d){
			console.log(d);
			$.each(d.videos, function() {
				$('#videos tbody').append('<tr><td>' + '(image)' + '</td><td>' + this.title + '</td><td>' + this.rating + '</td><td>' + '' + '</td></tr>');
			});
		}
	});
}

