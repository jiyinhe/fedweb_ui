$(document).ready(function () {

// When submit button is clicked 
$('#preqst_btn').click(function(){
	return validate_prequestionnaire_form();	
});

});//document

function validate_prequestionnaire_form(){
	rules = {
		'consent': {'required': true, 'checkbox': true, 'terms': true },
		'gender': {'required': true},
		'age': {'required': true },
		'education': {'required': true},
		'computer': {'required': true, 'radio': true},
		'english': {'required': true, 'radio': true},
		'search': {'required': true, 'radio': true},
	};
	errs = validate(rules);
	success = true;
	data = {};
	focus = undefined;
	return submit_preqst();	 
	for (r in rules){
		if (r in errs && errs[r]){
			//Show error message
			$('#err_'+r).html(errs[r]);
			//Show error sign
			$('#errsign_'+r).removeClass('errsign-valid').addClass('errsign-err');
			success = false;	
			focus = r;
		}
		else{
			//remove error message
			$('#err_'+r).html('');
			//remove error sign
			$('#errsign_'+r).removeClass('errsign-err').addClass('errsign-valid');	
			
			if("radio" in rules[r] || "checkbox" in rules[r]){ 
				data[r]=$('input[name="'+r+'"]:checked').val();
			}else{ // get normal value
				data[r]= $("#"+r).val();
			}
		}
	}	
	//Try to register, fail if username is taken
	if (success){
		return submit_preqst();
	}
	else{
// hack so radio buttons grouped by name are also in focus
		value = $("#"+focus); 
		if(value.length == 0){
			$('[name="'+focus+'"]').focus();					
		}else{
			value.focus();
		}
	}
	return false;
}	

function submit_preqst(){
		$('#prequest_form').submit();
		return true;
}


