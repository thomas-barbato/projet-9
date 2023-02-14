$(window).on('load', function(){
    $('.color-swap:odd').addClass('color-swap-1')
    $('.color-swap:odd>button.btn').addClass('btn-light')
    $('.color-swap:even').addClass('color-swap-2')
    $('.color-swap:even>button.btn').addClass('btn-dark')
})
