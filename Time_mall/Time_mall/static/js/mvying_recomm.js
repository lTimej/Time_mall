$(function(){
	var $slides = $('.mvying_recomm');
	var len = $slides.length;
	var nowli = 0;
	var prevli = 0;
	var $clickChange = $('.mvying_change');
	var timer = null;
    $slides.not(':first').css({'opacity':0,'display':'none'});
	function autoplay(){
		nowli++;
		move();
	};
	$clickChange.click(function() {
		autoplay()
	});

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