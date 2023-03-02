
    $(window).on('load', function(){
        $('.file-msg').hide();
        description_editor = CKEDITOR.replace('id_description',
        {
            customConfig : 'config_custom.js',
            height: '20vh',
        })

        body_editor = CKEDITOR.replace('id_body',
        {
            customConfig : 'config_custom.js',
            height: '20vh',
        })
    })

    $('.fake-input-file').on('click', function(e){
        $('.hidden-input-file').click();
    })


    $(document).on('keypress',function(e) {
        if(e.which == 13) {
            $('.create-review-button').click()
        }
    });

    function readURL(input) {
        if (input.files && input.files[0]) {
            var reader = new FileReader();
            reader.readAsDataURL(input.files[0]);
        }
    }

    $("#id_image").change(function(){
        readURL(this);
        $('.file-msg').show();
    });




    $('.create-review-button').on('submit', function(e){
        let formData = new FormData();
        let id_title = $('#id_title').val();
        let id_description = $('#id_description').val()
        if($("#id_image").val() != ''){
            let id_image =  $('#id_image').prop('files')[0];
            formData.append('id_image', id_image)
            formData.append('filename', id_image.name)
        }
        let id_rating = $('input[name="rating"]:checked').val()
        let id_headline = $('#id_headline').val()

        formData.append('id_title', JSON.stringify(id_title));
        formData.append('id_description', JSON.stringify(CKEDITOR.instances['id_description'].getData()))
        formData.append('id_headline', JSON.stringify(id_headline));
        formData.append('id_body', JSON.stringify(CKEDITOR.instances['id_body'].getData()))
        formData.append('csrfmiddlewaretoken', csrf);
            $.ajax({
                url: review_view ,
                type: 'post',
                csrfmiddlewaretoken: csrf,
                cache: false,
                processData: false,
                contentType: false,
                dataType : 'json',
                data: formData,
                success: function (json) {
                }
            })
    });
