
$(document).ready(function(){


	querying();
	$('input.input-area').focus();

	

});

function querying()
{
	var jieba_reswrap = $('.res-jieba');
	$('.input-area').keyup(function(e){
		var query = $.trim($(this).val());

		
		$('.loading-icon').toggleClass('hide');
		$.getJSON('/api/tokenize/'+query, function(data){
			jieba_reswrap.html('');
			$.each(data.res, function(i, obj){
				$('<span/>').addClass('token').text(obj).appendTo(jieba_reswrap)
			});
			$('.loading-icon').toggleClass('hide');
			// jieba_reswrap.slideDown(10);
		});
	});
}
