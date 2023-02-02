
    $('#username_error, #password_error').hide()
    $('.return-button').on('click', function(){
        window.location.href = login_view;
    });

    $('.signup-button').on('click', function(){
        let username = $('#id_username').val();
        let password = $('#id_password').val();
        let password2 = $('#id_password2').val();
        $.ajax({
            url: registration_view,
            type: 'POST',
            dataType : 'json',
            headers: { "X-CSRFToken": csrf },
            data:{
              'csrfmiddlewaretoken': csrf,
              'username': username,
              'password': password,
              'password2': password2
            },
            success(json){
                if(json.status == 1){
                    window.location = login_view
                }else{
                    let password_elem = $('#password_error')
                    let username_elem = $('#username_error')
                    $.each(json.errors, function( index, value ) {
                      if(index === "password" || index === "password2" || index === "__all__"){
                        password_elem.html(value);
                        password_elem.show().fadeOut(5000);
                      }else if(index === "username"){
                        username_elem.html(value);
                        username_elem.show().fadeOut(5000);
                      }
                    });
                }

            }

        })
    })