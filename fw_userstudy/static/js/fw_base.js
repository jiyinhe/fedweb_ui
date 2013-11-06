$(document).ready(function () {

// Validate the registration form
$('#reg_btn').click({
	alert('alert');
});
/*
	$('#reg_form').validate({
    	rules: {
        	name: {
            		minlength: 6,
            		required: true
        	},
        	email: {
            		required: true,
            		email: true
        	},
        	password: {
            		minlength: 6,
            		required: true
        	}
    	},
    	highlight: function (element) {
        	$(element).closest('.control-group').removeClass('success').addClass('error');
    	},
    	success: function (element) {
        	element.text('OK!').addClass('valid')
            	.closest('.control-group').removeClass('error').addClass('success');
    	}
	});

*/
});//document
