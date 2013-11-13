var resultlist = [];

$(document).ready(function(){

//prepare results	
$('#results').ready(function(){
	cache_results();
});

//When click document title, show document
$('.doc_title').click(function(){
	ele_id = $(this).attr('id');
	doc_click(ele_id);
	//set the modal title
	title = $('#'+ele_id+'_title').attr('name');
	$('#modal_title').html(title);
});

//When click bookmark, bookmark document
$('.bookmark').click(function(){
	ele_id = $(this).attr('id');
	doc_bookmark(ele_id);
});

// adjust the category area length
$('#category_area').ready(function(){
	$('#category_area').height($(window).height()-70);	
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

function cache_results(){
	for (var i = 0; i < total_num_docs; i++){
		ele = document.getElementById('rank_'+i);	
		resultlist.push(ele);
	}
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

//Documents in array
//[(rank, doc)]
function load_documents(docs){
	results = []
	for (d in docs){
	    var rank = d;
	    var doc = docs[d][1];
	    var html = [
		'<div id="rank_'+rank+'" class="list-group-item">',
		'<div id="'+doc['id']+'_title" name="'+doc['title']+'" class="list-group-item-heading">',
	        '<span class="glyphicon glyphicon-star-empty bookmark" id="'+doc['id']+'_bookmark"></span>',
		'<span class="doc_title" id="'+doc['id']+'" data-toggle="modal", data-target="#docModal">',
		doc['title'],
		'</span>',
		'</div>',
		'<div class="doc_url" id="url_'+doc['id']+'" >'+doc['url']+'</div>',
		'<div class="list-group-item-text">'+doc['summary']+'</div>',
		'</div>',
		];
	    results.push(html.join('\n'));
	}
	$('#results').html(results.join('\n'))
} 


function category_click(ele_id){
	//find the previously active one, release active
	$('#'+current_active_category).toggleClass('active');
	//set this category to active
	$('#'+ele_id).toggleClass('active');
	current_active_category = ele_id;
	if (current_active_category == 'category_all'){
		//set everyone to be active
		var html = [];
		for (r in resultlist){
			content = '<div id="rank_"+' + r + '" class="list-group-item" name="doc-item">';
			content += resultlist[r].innerHTML;
			content += '</div>';
			html.push(content);		
		}
		$('#results').html(html.join('\n'));
	}
	else{
		var html = [];
		var docs = cate[parseInt(ele_id.replace('category_', ''))]['doc_ranks'];
		for (d in docs){
			content = '<div id="rank_' + docs[d] + '" class="list-group-item" name="doc-item">';
			content += resultlist[docs[d]].innerHTML;
			content += '</div>';
			html.push(content);		
		}
		$('#results').html(html.join('\n'));

	}
}




