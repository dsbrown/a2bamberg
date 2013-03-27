// Url for videos JSON
var videoJsonUrl = 'http://localhost:5000/api/list?order=rating&direction=ascending';
var videoTagTemplate = 
	'<video class="video-js vjs-default-skin" controls width="100" height="100" preload="false" data-setup="{}">' +
	   '<source type="video/mp4" src="{url}">' +
	'</video>';


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
			$.each(d, function() {
				$('#videos tbody').append('<tr><td>' + videoTagTemplate.replace('{url}', this.s3_url) + '</td><td>' + this.name + '</td><td>' + this.rating + '</td><td>' + '' + '</td></tr>');
			});
		}
	});
}

