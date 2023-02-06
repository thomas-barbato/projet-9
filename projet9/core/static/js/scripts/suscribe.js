$(window).on('load', function(){
    $('.color-swap:odd').addClass('color-swap-1')
    $('.color-swap:odd>button.btn').addClass('btn-light')
    $('.color-swap:even').addClass('color-swap-2')
    $('.color-swap:even>button.btn').addClass('btn-dark')
    $('.follow-policy').hide();
})

$('.follow-user-button').on('click', function(){
    let url = suscribe_view
    let username = $('#id_username').val();
    $.ajax({
        url: url,
        type: 'POST',
        dataType : 'json',
        headers: { "X-CSRFToken": csrf },
        data:{
          'csrfmiddlewaretoken': csrf,
          'username': username,
        },
        success(json){
            if(json.status == 1){
                $('.followed-users').append(
                 '<div class="row p-2 col-12 border color-swap followed-user"><p class="col-xl-10 col-md-10 col-sm-8">'+ json.username +'</p><button class="btn btn-secondary col-xl-2 col-md-2 col-sm-4">Supprimer</button></div>'
                )
                $('.color-swap:odd').addClass('color-swap-1')
                $('.color-swap:odd>button.btn').addClass('btn-light')
                $('.color-swap:even').addClass('color-swap-2')
                $('.color-swap:even>button.btn').addClass('btn-dark')

            }else{
                if(json.error){
                    $('.follow-policy').html(json.error).show()
                }
            }
        }
    })
})

$('.unfollow-user-button').on('click', function(){
    let url = unfollow_url
    let username = $('.followed-user-username').text()
    console.log(x)
    /*
    $.ajax({
        url: url,
        type: 'POST',
        dataType : 'json',
        headers: { "X-CSRFToken": csrf },
        data:{
          'csrfmiddlewaretoken': csrf,
          'username': username,
        },
        success(json){
        }
    })*/

})