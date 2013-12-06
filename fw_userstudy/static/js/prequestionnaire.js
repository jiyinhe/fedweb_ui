$(document).ready(function () {

// When submit button is clicked 
$('#preqst_btn').click(function(){
	return validate_prequestionnaire_form();	
});
// Enable buttons
$('.btn').button();
$('.likert').click(function(){
	//set everything to inactive
	var prefix = $(this).attr('id').split('_')[0];
	for (var i = 0; i<=5; i++){
		$('#'+prefix+'_'+i).removeClass('active');
	}
	//toggle activated type
	$(this).addClass('active');
})
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
	for (r in rules){
		if (r in errs && errs[r]){
			//Show error message
			$('#err_'+r).html(errs[r]);
			//Show error sign
			$('#errsign_'+r).removeClass('errsign-valid').addClass('errsign-err');
			//Show error area
			$('#errarea_'+r).addClass('alert-danger');
			success = false;	
			focus = r;
		}
		else{
			//remove error message
			$('#err_'+r).html('');
			//remove error sign
			$('#errsign_'+r).removeClass('errsign-err').addClass('errsign-valid');	
			//remove error area
			$('#errarea_'+r).removeClass('alert-danger');

			if("radio" in rules[r] || "checkbox" in rules[r]){ 
				data[r]=$('input[name="'+r+'"]:checked').val();
			}else{ // get normal value
				data[r]= $("#"+r).val();
			}
			//console.log(data[r])
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


