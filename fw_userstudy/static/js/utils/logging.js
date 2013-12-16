// include logging listeners here that need to be included in all
// templates that include fw_base
$(document).ready(function(){
	$('#logout_link').click(function(){
		console.log('logout');
		ILPSLogging.userLogout();
	});

	$('#login_link').click(function(){
		console.log('login');
		user = $('#id_username').val();
		console.log(user);
		ILPSLogging.userLogin(user);
	});
});
