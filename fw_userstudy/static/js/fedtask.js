$(document).ready(function(){
//load results	
$('#results').ready(function(){
//	load_results();
});

$('.doc_title').click(function(){
	ele_id = $(this).attr('id');
	doc_click(ele_id);
})
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

// when a document is clicked, get the html file, set url to "visited"
function doc_click(ele_id){
	console.log(ele_id);
}
