
    $('#username_error, #password_error').hide()
    $('.return-button').on('click', function(){
    console.log("ok")
        window.location.href = login_view;
    });

    $('form>input').on('change', function(){
        $(this).css('border','');
    })

    $(document).on('keypress',function(e) {
        if(e.which == 13) {
            $('.signup-button').click()
        }
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
                    let index_error = ['password', 'password2', '__all__', 'username']
                    let array = $.each(json.errors, function(key, value){
                        return [key, value]
                    })
                    $.each(index_error, function(index){
                        if(index_error[index] in array){
                            if(index_error[index] == "password" || index_error[index] == "password2"){
                               $('#id_password, #id_password2').css('border', '2px solid red');
                                $(password_elem).html(array["password2"]).show().fadeOut(5000);
                            }else if(index_error[index] == "__all__"){
                                $('form>input').css('border', '2px solid red');
                                $(password_elem).html(array["__all__"]).show().fadeOut(5000);
                            }else if(index_error[index] == "username"){
                                $("#id_username").css('border', '2px solid red');
                                $(username_elem).html(array["username"]).show().fadeOut(5000);
                            }
                        }else{
                            $('#id_'+index_error[index]).css('border', '2px solid green');
                        }
                    })
                    $(document).ready(function () {
                        setTimeout( function(){
                            $('form>input').css('border','');
                        },5000);
                    });

                }
            }

        })
    })