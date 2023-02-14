
$('.login-policy').hide()

// " " are used to define django values.
// only work with instruction which don't use keyword like url...
"{% if messages %}"
    $('ul.messages').fadeOut(5000);
"{% endif %}"

$('.login-button').on('click', function(){
    let url = login_view
    let username = $('#id_username').val();
    let password = $('#id_password').val();
    $.ajax({
        url: url,
        type: 'POST',
        dataType : 'json',
        headers: { "X-CSRFToken": csrf },
        data:{
          'csrfmiddlewaretoken': csrf,
          'username': username,
          'password': password,
        },
        success(json){
            if(json.status == 1){
                window.location = flux_view
            }else{
                if(json.errors){
                    $('.login-policy').show().fadeOut(5000);
                }
            }
        }
    })
})

$('.welcome-msg').fadeOut(5000);