var RESULTLIST = [];
var ALLRANKS = [];
var CURRENTPAGE = 1;
var PAGESIZE = 10;

$(document).ready(function(){


// when done button for training task is pressed update session
$("#done").click(function(){
	submit_complete_task();	
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


load_results(); // also caches the results

bind_resultlist_listeners();
//When click document title, show document
});//document

function bind_resultlist_listeners(){
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
	$('.pagination').click(function(){
		ele_id = $(this).attr('id');
		update_pagination(ele_id);
	});
}

// get all results for given topic_id, run_id
function load_results(){
        $.ajax({type: "POST",
                url: results_url,
                data: { ajax_event: 'fetch_results',
						topic_id: topic_id,
						run_id: run_id,
						page: 1,
                }
        }).done(function(response) {
			RESULTLIST = create_resultlist(response);
			for (var i = 0; i < RESULTLIST.length; i++) {
				ALLRANKS.push(i);
			}
			$('#results').html(RESULTLIST.slice(0,PAGESIZE).join('\n'));
			// create_pagination expects a parameter, so we pass
			// response, it is just to get the lenght
			$('#pagination').html(create_pagination(response));
			//clear the modal section
			$('#modal_title').html('');
			$('#doc_content').html('');

			//rebind the listner for clicking documents
			bind_resultlist_listeners();
			//window go back to top
			$('html, body').animate({scrollTop: 0}, 0);
        });
}

//function cache_results(){
//	RESULTLIST = $('div[id^="rank_"]');
//}

function create_resultlist(response){
	var reslist=[];
	for (var i=0; i<response.length; i++){
		var d = response[i];
		// choose bookmarked / not bookmarked glyph style
		var bookmark = "";
		if (d[1].bookmarked == 1){
			// t is the template
	    	t='<span class="glyphicon glyphicon-star bookmark bookmark-selected" id="{0}_bookmark"></span>'
			bookmark = $.validator.format(t,d[1].id);
		}else{
			t='<span class="glyphicon glyphicon-star-empty bookmark" id="{0}_bookmark"></span>'
			bookmark = $.validator.format(t,d[1].id);
		}

		// setup templates and fillers for formatting of a result snippet
		var doc= [
['<div id="rank_{0}" class="list-group-item" name="doc-item">',d[0]],
['<div id="result-item_{0}" class="result-item">',d[1].id],
['<div id="{0}_title" name="{1}"class="list-group-item-heading">',[d[1].id,d[1].title]],
['{0}',bookmark],
['<span class="doc_title" id="{0}"data-toggle="modal" data-target="#docModal">{1}</span></div>',[d[1].id,d[1].title]],
['<div class="doc_url" id="url_{0}">{1}</div>',[d[1].id,d[1].url]],
['<div class="list-group-item-text">{0}</div></div></div>',d[1].summary]];
	
		// format the result snippet
		var lines = [];
		for (var j=0; j<doc.length; j++){
			lines.push($.validator.format(doc[j][0],doc[j][1]));
		}
		// push snippet on result list stack
		reslist.push(lines.join('\n'));	
	}
	return reslist
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
    selected=0;
	//change the class and icon
	$('#'+ele_id).toggleClass('bookmark-selected');
	if ($('#'+ele_id).hasClass('glyphicon-star-empty')){
		$('#'+ele_id).removeClass('glyphicon-star-empty');
		$('#'+ele_id).addClass('glyphicon-star');
        selected=1;
	}
	else{
	        $('#'+ele_id).removeClass('glyphicon-star');
			$('#'+ele_id).addClass('glyphicon-star-empty');
	}
	//send selection to db
	$.ajax({
                type: "POST",
                url: bookmark_url,
                data: {
                        ajax_event: 'bookmark_document',
                        selected_state: selected, 
                        session_id: session_id,
                        topic_id: topic_id,
                        doc_id: ele_id,
                      }
        }).done(function(response) {
			// get the doc id (remove '_bookmark' from ele_id
			doc_id = ele_id.substr(0,ele_id.lastIndexOf("_"));
			// only show feedback when training is true
			if (training == true){
				if (response.feedback == "positive_feedback"){
					$("#"+doc_id+"_title").toggleClass("alert alert-success");
					$("#result-item_"+doc_id).toggleClass("result-item-correct");
					$("#feedback_"+doc_id).html(
					'<span class="bookcorrect glyphicon glyphicon-ok pull-right"></span>'
					);

				}else if(response.feedback == "negative_feedback"){
					$("#"+doc_id+"_title").toggleClass("alert alert-danger");
					$("#result-item_"+doc_id).toggleClass("result-item-error");
				        $("#feedback_"+doc_id).html( 
                                        '<span class="bookerror glyphicon glyphicon-remove pull-right"></span>'
                                        );   

				}else if(response.feedback == "delete_feedback"){
					$("#"+doc_id+"_title").removeClass("alert alert-danger alert-success");
					$("#result-item_"+doc_id).removeClass("result-item-correct result-item-error");
					$("#feedback_"+doc_id).html('');
				}
				else{
					console.log("no_feedback");		
				}
				notify_feedback(response.feedback);
			}
			$("#bookmark_count").html(response.count);

			if (response.done == true){
				submit_complete_task()	
			}
			// update resultlist cache
			rankid = $('#result-item_'+doc_id).parent().attr('id');
			rankindex = parseInt(rankid.replace('rank_',''));
			item = '<div id="'+rankid+'" class="list-group-item" name="doc-item">';
			item += $('#'+rankid).html();
			item += '</div>';
			RESULTLIST[rankindex]=item;
        });
}

function submit_complete_task(){
	console.log("submit complete task")
	window.location = submit_complete_task_url;
}

function category_click(ele_id){
	$('#'+current_active_category).toggleClass('active');
	//set this category to active
	$('#'+ele_id).toggleClass('active');
	current_active_category = ele_id;
	pagination();
}

function update_pagination(ele_id){
	var docs = ALLRANKS
	if (typeof(current_active_category) != 'undefined'){	
		if (current_active_category != 'category_all'){
			docs = cate[1+parseInt(current_active_category.replace('category_',''))]['doc_ranks'];
		}
	}
	if (ele_id == 'pagination_first'){CURRENTPAGE = 1;}
	if (ele_id == 'pagination_last'){
		CURRENTPAGE = Math.ceil(docs.length/10);
	}
	if (ele_id == 'pagination_prev'){
		if (CURRENTPAGE > 1){CURRENTPAGE--;}}
	if (ele_id == 'pagination_next'){
		if (CURRENTPAGE < Math.ceil(docs.length/10)){
			CURRENTPAGE++;
		}
	}
	pagination();
}

function pagination(){
	var docs = ALLRANKS; // category_all
	if (typeof(current_active_category) != 'undefined'){	
		if (current_active_category != 'category_all'){
			docs = cate[1+parseInt(current_active_category.replace('category_',''))]['doc_ranks'];
		}
	}
	var html = [];

	pagination_html = create_pagination(docs);

	startindex = (CURRENTPAGE-1) * PAGESIZE;
	endindex = CURRENTPAGE * PAGESIZE;
	if (endindex > docs.length){ endindex = docs.length;}
	docs = docs.slice(startindex,endindex);
	for (d in docs){
		content = RESULTLIST[docs[d]];
		html.push(content);
	}
	$('#results').html(html.join('\n'));
	$('#pagination').html(pagination_html);
	bind_resultlist_listeners()

    $('html, body').animate({scrollTop: 0}, 0);
}

function create_pagination(docs){
	var prevpage = '-';
	if (CURRENTPAGE > 1){ prevpage = CURRENTPAGE - 1; }
	
	var nextpage = '-';
	if (CURRENTPAGE < docs.length/10){ nextpage = CURRENTPAGE + 1;}
	html = [
	'<ul class="pager">',
	  '<li><a id="pagination_first" class="pagination"><span',
			'class="pull-left">First</span><span class="badge',
			'pull-right">1</span></a></li>',
	  '<li><a id="pagination_prev" class="pagination"><span',
			'class="pull-left">Prev</span><span class="badge',
			' pull-right">',
			prevpage,
			' </span></a></li>',
	  '<li><a id="pagination_page" class="pagination"><span',
			'class="pull-left">Page</span><span class="badge',
			' pull-right">',
			CURRENTPAGE,
			'</span></a></li>',
	  '<li><a id="pagination_next" class="pagination"><span',
			'class="pull-left">Next</span><span class="badge',
			' pull-right">',
			nextpage,
			'</span></a></li>',
	  '<li><a id="pagination_last" class="pagination"><span',
			'class="pull-left">Last</span><span class="badge',
			' pull-right">',
			Math.ceil(docs.length/PAGESIZE),
			'</span></a></li>',
	  '</ul>']
	return 	html.join( '\n');
}
