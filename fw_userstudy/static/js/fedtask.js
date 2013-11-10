$(document).ready(function(){
//load results	
$('#results').ready(function(){
//	load_results();
});

});//document

// get results for given topic_id, run_id
function load_results(){
        $.ajax({
                type: "POST",
                url: results_url,
                data: {
                        ajax_event: 'fetch_results',
			topic_id: topic_id,
			run_id: run_id,
                }
        }).done(function(response) {
        });

}
