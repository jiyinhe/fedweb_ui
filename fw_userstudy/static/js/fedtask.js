$(document).ready(function(){

//load results	
//$('#results').ready(function(){
//	load_results();
//});

$('.doc_title').click(function(){
	ele_id = $(this).attr('id');
	doc_click(ele_id);
	//set the modal title
	title = $('#'+ele_id+'_title').attr('name');
	$('#modal_title').html(title);
});

$('.bookmark').click(function(){
	ele_id = $(this).attr('id');
	doc_bookmark(ele_id);
});

// adjust the category area length
$('#category_area').ready(function(){
	$('#category_area').height($(window).height());	
});	

//response to click on category
$('.category').click(function(){
	ele_id = $(this).attr('id');
	category_click(ele_id);
})

//category tooltip
$('[rel=tooltip]').tooltip({
	placement: "auto",
});

});//document


// get results for given topic_id, run_id
// This is not currently used.
// Currently we direct send data when loading the page
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
	//Request the html file with this docid
	$.ajax({
                type: "POST",
                url: document_url,
                data: {
                        ajax_event: 'fetch_document',
			doc_id: ele_id,
                }
        }).done(function(response) {
		console.log(response);
		$("#doc_content").html(response);
        });

}

//when a document is bookmarked
function doc_bookmark(ele_id){
	//change the class and icon
	$('#'+ele_id).toggleClass('bookmark-selected');
	if ($('#'+ele_id).hasClass('glyphicon-star-empty')){
		$('#'+ele_id).removeClass('glyphicon-star-empty');
		$('#'+ele_id).addClass('glyphicon-star');
	}
	else{
	        $('#'+ele_id).removeClass('glyphicon-star');
                $('#'+ele_id).addClass('glyphicon-star-empty');
	}
	//send selection to db
}


function category_click(ele_id){
	//find the previously active one, release active
	$('#'+current_active_category).toggleClass('active');
	//set this category to active
	$('#'+ele_id).toggleClass('active');
	current_active_category = ele_id;
	//filter the results
	var cid = parseInt(ele_id.replace('category_', ''));
	console.log(cate[cid]["doc_ranks"])
}




