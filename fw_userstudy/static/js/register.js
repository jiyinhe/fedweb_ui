$(document).ready(function () {

// When submit button is clicked 
$('#reg_btn').click(function(){
	validate_registration_form();	
});

});//document

function validate_registration_form(){
	//Username
	rules = {
		'reg_username': {'minlength': 6, 'required': true},
		'reg_email': {'required': true, 'email': true},
		'reg_pass1': {'required': true, 'minlength': 6},
		'reg_pass2': {'required': true, 'equals': 'reg_pass1'},
	};
	
	err_user_id = 'err_reg_username';
	sign_user_id = 'errsign_username'; 
	errs = validate(rules)	
	for (e in errs){
		console.log(e+' '+errs[e]);
	}	
}
