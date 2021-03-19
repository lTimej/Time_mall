

$(window).scroll(function () {
    var scroH = $(this).scrollTop();
    var Y = 106+160*(cartLen-3)
    if (scroH<Y)
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