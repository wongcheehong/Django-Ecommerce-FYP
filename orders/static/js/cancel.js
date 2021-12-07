$(".cancel-btn").click(function(e){
    const id = $(this).data('id');
    Swal.fire({
      title: 'Are you sure you want to cancel this order',
      text: "You won't be able to revert this!",
      icon: 'warning',
      showCancelButton: true,
      confirmButtonColor: '#3085d6',
      cancelButtonColor: '#d33',
      confirmButtonText: 'Yes',
      cancelButtonText: 'No'
    }).then((result) => {
      if (result.isConfirmed) {
        $.post({
        url: cancel_url,
        data: {id: id},
        success: function(response){
            console.log(response)
            if(response['status']=='ok')
            {
                Swal.fire(
                  'Cancelled!',
                  'Your order has been deleted.',
                  'success'
                )
                $(".swal2-confirm").click(function(e){
                    location.reload();
                })
            }
        }
        });
      };
    });
});