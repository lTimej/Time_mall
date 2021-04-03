function xuanfu(cartsLen) {
    if (cartsLen>=3)
    {
        $("#cart_bar").css({
            "position":"fixed",
            "bottom":0
        })
    }
    $(window).scroll(function () {
    var scrollH = $(this).scrollTop();
    var Y = 116+158*(cartsLen-3)
    if (scrollH<Y)
    {
        $("#cart_bar").css({
            "position":"fixed",
            "bottom":0
        })
    }else{
        $("#cart_bar").css({
            "position":"relative",
        })
    }
})
}