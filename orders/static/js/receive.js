$(".receive-btn").click(function(e){
    const id = $(this).data('id');
    $.post({
        url: receive_url,
        data: {id: id},
        success: function(response){
            console.log(response)
            if(response['status']=='ok')
            {
                Swal.fire(
                  'Order Completed!',
                  'Thank you for your support!',
                  'success'
                )
                $(".swal2-confirm").click(function(e){
                    location.reload();
                })
            }
        }
    });
});