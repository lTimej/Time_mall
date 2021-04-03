$(function(){
	var $slides = $('.neiyi');
	var len = $slides.length;
	var nowli = 0;
	var prevli = 0;
	var $points = $('.point_neiyi li');
	var timer = null;
    $slides.not(':first').css({'opacity':0,'display':'none'});
	$slides.each(function(index, el) {
        var $li = $('<li>');
		if(index==0)
		{
			$li.addClass('active');
		}
		$li.appendTo($('.point_neiyi'));
	});
	$points = $('.point_neiyi li');
	timer = setInterval(autoplay,5000);

	$('.pos_center_con').mouseenter(function() {
		clearInterval(timer);
	});

	$('.pos_center_con').mouseleave(function() {
		timer = setInterval(autoplay,5000);
	});

	function autoplay(){
		nowli++;
		move();
		$points.eq(nowli).addClass('active').siblings().removeClass('active');
	};
	// --------------
	$points.click(function() {
		nowli = $(this).index();
		$(this).addClass('active').siblings().removeClass('active');
		move();
		console.log('------------------------',nowli);
	});
	// $prev.click(function() {
	// 	nowli--;
	// 	console.log('-------------',nowli);
	// 	move();
	// 	console.log('-------------',nowli);
	// 	$points.eq(nowli).addClass('active').siblings().removeClass('active');
	// });
	// $next.click(function() {
	// 	nowli++;
    //
	// 	move();
	// 	$points.eq(nowli).addClass('active').siblings().removeClass('active');
    //
	// });

	function move(){
		if(nowli==prevli)
		{
			return;
		}

		if(nowli<0)
		{
			nowli=len-1;
			prevli = 0;
			$slides.eq(nowli).animate({'opacity':1},800).css("display","");
			$slides.eq(prevli).animate({'opacity':0},800).css("display","none");
			prevli=nowli;
			return;
		}

		if(nowli>len-1)
		{
			nowli = 0;
			prevli = len-1;
			$slides.eq(nowli).animate({'opacity':1},800).css("display","");
			$slides.eq(prevli).animate({'opacity':0},800).css("display","none");
			prevli=nowli;
			return;
		}

		if(prevli<nowli)
		{
			$slides.eq(nowli).animate({'opacity':1},800).css("display","");
			$slides.eq(prevli).animate({'opacity':0},800).css("display","none");
			prevli=nowli;
		}
		else
		{
			$slides.eq(nowli).animate({'opacity':1},800).css("display","");
			$slides.eq(prevli).animate({'opacity':0},800).css("display","none");
			prevli=nowli;
		}
	}
});