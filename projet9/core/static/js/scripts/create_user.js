function create_user(url, url_redirect){
    $('#username_error, #password_error').hide()
    $('.return-button').on('click', function(){
        let url = "{% url 'login_view' %}";
        window.location.href = url;
    });

    $('.signup-button').on('click', function(){
        console.log(url)
        let username = $('#id_username').val();
        let password = $('#id_password').val();
        let password2 = $('#id_password2').val();
        $.ajax({
            url: url,
            type: 'POST',
            dataType : 'json',
            headers: { "X-CSRFToken": "{{ csrf_token }}" },
            data:{
              'csrfmiddlewaretoken': '{{ csrf_token }}',
              'username': username,
              'password': password,
              'password2': password2
            },
            success(json){
                if(json.status == 1){
                    window.location = url_redirect
                }else{
                    let password_elem = $('#password_error')
                    let username_elem = $('#username_error')
                    $.each(json.errors, function( index, value ) {
                      if(index === "password" || index === "password2" || index === "__all__"){
                        password_elem.html(value).show()
                      }else if(index === "username"){
                        username_elem.html(value).show()
                      }
                    });
                }

            }

        })
    })
}