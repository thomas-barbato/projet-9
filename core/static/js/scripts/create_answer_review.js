
    $(window).on('load', function(){

        body_editor = CKEDITOR.replace('id_body',
        {
            customConfig : 'config_custom.js',
            height: '20vh',
        })
    })

     let answer_review_array = document.URL.split('/')
     let answer_review_id = answer_review_array[answer_review_array.length-1];
     let answer_review_url = "/dashboard/flux/create_answer_review/" + answer_review_id + "?"

    $('.answer-ticket-button').on('submit', function(e){
        let this_id = "{{ ticket.id }}";
        let url = answer_review_url;
        let formData = new FormData();

        let id_rating = $('input[name="rating"]:checked').val()
        let id_headline = $('#id_headline').val()

        formData.append('id_ticket', JSON.stringify())
        formData.append('id_headline', JSON.stringify(id_headline));
        formData.append('id_body', JSON.stringify(CKEDITOR.instances['id_body'].getData()))
        formData.append('csrfmiddlewaretoken', csrf);
            $.ajax({
                url: answer_review_view ,
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
