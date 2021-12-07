
$(document).ready(function(){
    jQuery.validator.addMethod("lettersonly", function(value, element) {
        return this.optional(element) || /^[a-z\s]+$/i.test(value);
    }, "Only alphabetical characters");
    // Create Address
    $('#address_creation_form').validate({
        errorClass: "invalid-feedback",
        highlight: function(element, errorClass, validClass) {
            $(element).next().addClass(errorClass);
        },
        unhighlight: function(element, errorClass, validClass) {
            $(element).next().removeClass(errorClass);
        },
        rules:{
            address_name:{required:true, lettersonly: true},
            address:{required:true},
            address_state:{required:true},
            address_city:{required:true, lettersonly: true},
            address_zip:{required:true, number:true}
        },
        submitHandler: function(form){
            $.post({
            url: $('#address_creation_form').attr('action'),
            data: {
                address_name: $('#id_address_name').val(),
                address: $('#id_address').val(),
                address_state: $('#id_address_state').val(),
                address_city: $('#id_address_city').val(),
                address_zip: $('#id_address_zip').val(),
            },
            success: function(response){
                location.reload();
            },
            dataType: 'json'
        });
        }
    });
});
