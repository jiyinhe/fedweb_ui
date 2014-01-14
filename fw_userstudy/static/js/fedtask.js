var RESULTLIST = [];
var ALLRANKS = [];
var CURRENTPAGE = 1;
var PAGESIZE = 10;
var CURRENT_PAGINATION_START = 1
var PAGINATION_SIZE = 1

$(document).ready(function(){
//var viewportWidth  = $(window).width()
//  , viewportHeight = $(window).height()
//console.log(viewportWidth);
//console.log(viewportHeight);


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
	add_click();
})

load_results(); // also caches the results

bind_resultlist_listeners();


});//document

function bind_resultlist_listeners(){
	//When click bookmark, bookmark document
	$('.bookmark').click(function(){
		var ele_id = $(this).attr('id');
		doc_bookmark(ele_id);
	});
	//when doc_title is clicked, also bookmark it
	$('.doc_title').click(function(){
		var ele_id = $(this).attr('id')+'_bookmark';
		doc_bookmark(ele_id);
	})

	//pagination clicked
	$('.page').click(function(){
		var ele_id = $(this).attr('id');
		update_pagination(ele_id);
		add_click();
	});
}

// get all results for given topic_id, run_id
function load_results(){
		var startRequest = Date.now();
        $.ajax({type: "POST",
                url: results_url,
                data: { ajax_event: 'fetch_results',
						topic_id: topic_id,
						run_id: run_id,
						page: 1,
                }
        }).done(function(response) {
			var responseTime = Date.now() - startRequest;
			RESULTLIST = create_resultlist(response);
			for (var i = 0; i < RESULTLIST.length; i++) {
				ALLRANKS.push(i);
			}
			var page1_snippetlist = RESULTLIST.slice(0,PAGESIZE);
			$('#results').html(page1_snippetlist.join('\n'));

			// log login
			var state = ILPSLogging.getState();

			state['current_category']="";
			if (typeof(current_active_category) != "undefined"){
				state['current_category']=current_active_category;
			};
			state['topic_id']=topic_id;
			state['run_id']=run_id;
			state['session_id']=session_id;
			state['results_list'] = ALLRANKS.slice(0,PAGESIZE);
			state['query'] = {'query_string':topic_id,
							  'current_page_n':CURRENTPAGE,};
			ILPSLogging.setState(state);
			ILPSLogging.userLogin(username,{
				'n_total_results':RESULTLIST.length, 
				'n_displayed_results':ALLRANKS.slice(0,PAGESIZE).length,
				'query_time_ms':responseTime,
			},false);

			ILPSLogging.queryResults
			// create_pagination expects a parameter, so we pass
			// response, it is just to get the lenght
			$('#pagination').html(create_pagination(response));

			//rebind the listner for clicking documents
			bind_resultlist_listeners();
			//window go back to top
			$('html, body').animate({scrollTop: 0}, 0);
        });
}

function create_resultlist(response){
	var reslist=[];
	for (var i=0; i<response.length; i++){
		var d = response[i];
		// choose bookmarked / not bookmarked glyph style
		// if bookmarked add relevant/not relevant feedback
		// bookmarked one of {1,0,-1}
		// 1 is bookmarked and relevant
		// -1 is bookmarked and not relevant
		// 0 is not bookmarked
		// the bookmark icon (star full/empty)
		var bookmark ='';
		// t is the template
		var t = '';
		// contains the alert class (alert-danger/alert-success/empty)
		var feedback_alert = '';
		// contains the icon to display (bookcorrect/bookerror)
		var feedback_icon = '';
		// result-item class: result-item-error/ result-item-correct
		var feedback_result_item =''
		if (d[1].bookmarked === 1){
			t='<span data-ilpslogging-groupid="rank_{0}" class="glyphicon glyphicon-star bookmark bookmark-selected" id="{1}_bookmark"></span>';
			feedback_alert = ' alert alert-success';
			feedback_icon = '<span data-ilpslogging-groupid="rank_{0}" class="bookcorrect glyphicon glyphicon-ok pull-right"></span>';
			 feedback_result_item ='result-item-correct'
		}else if (d[1].bookmarked === -1){
			t='<span data-ilpslogging-groupid="rank_{0}" class="glyphicon glyphicon-star bookmark bookmark-selected" id="{1}_bookmark"></span>';
			feedback_alert = ' alert alert-danger';
			feedback_icon = '<span data-ilpslogging-groupid="rank_{0}" class="bookerror glyphicon glyphicon-remove pull-right"></span>';
			 feedback_result_item ='result-item-error'
		}else{
			t='<span data-ilpslogging-groupid="rank_{0}" class="glyphicon glyphicon-star-empty bookmark" id="{1}_bookmark"></span>'
		}
		// format the glyph icon (full/empty)
		bookmark = $.validator.format(t,[d[0],d[1].id]);
        feedback_icon = $.validator.format(feedback_icon,d[0]);
		// setup templates and fillers for formatting of a result snippet
		var doc= [
	['<div data-ilpslogging-groupid="rank_{0}" id="rank_{1}" class="list-group-item" name="doc-item">',[d[0],d[0]]],
	['<div data-ilpslogging-groupid="rank_{0}" id="feedback_{1}">{2}</div>', [d[0],d[1].id, feedback_icon]],
	['<div data-ilpslogging-groupid="rank_{0}" id="result-item_{1}" class="result-item {2}">',[d[0],d[1].id, feedback_result_item]],
	['<div data-ilpslogging-groupid="rank_{0}" id="{1}_title" name="{2}" class="list-group-item-heading{3}">',
		[d[0],d[1].id, d[1].title, feedback_alert]],
	['{0}',bookmark],
	['<span data-ilpslogging-groupid="rank_{0}" class="doc_title" id="{1}">{2}</span></div>',[d[0],d[1].id, d[1].title]],
	['<div data-ilpslogging-groupid="rank_{0}" class="doc_url" id="url_{1}">{2}</div>',[d[0],d[1].id, d[1].url]],
	['<div data-ilpslogging-groupid="rank_{0}" class="list-group-item-text">{1}</div></div></div>',[d[0],d[1].summary]]];
	
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
	ILPSLogging.logEvent("doc_view_try",{"node_id":ele_id});	
	//Request the html file with this docid
	var startRequest = Date.now();
	$.ajax({
                type: "POST",
                url: document_url,
                data: {
                        ajax_event: 'fetch_document',
			doc_id: ele_id,
                }
        }).done(function(response) {
			var responseTime = Date.now() - startRequest;
			ILPSLogging.logEvent("doc_view",{"node_id":ele_id,
						"query_time_ms":responseTime,});	
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
		ILPSLogging.logEvent("bookmark_try",{"node_id":ele_id});	
	}
	else{
		$('#'+ele_id).removeClass('glyphicon-star');
		$('#'+ele_id).addClass('glyphicon-star-empty');
		ILPSLogging.logEvent("unbookmark_try",{"node_id":ele_id});	
	}
	//send selection to db
	var startRequest = Date.now();
	$.ajax({
                type: "POST",
                url: bookmark_url,
                data: {
                        ajax_event: 'bookmark_document',
                        selected_state: selected, 
                        session_id: session_id,
                        topic_id: topic_id,
                        doc_id: ele_id,
			task_id: task_id,
                      }
        }).done(function(response) {
			// log time and action
			var responseTime = Date.now() - startRequest;
			if (selected == 1){
				ILPSLogging.logEvent("bookmark",{"node_id":ele_id,
					"query_time_ms":responseTime,
				 	"response":response});
			}else{
				ILPSLogging.logEvent("unbookmark",{"node_id":ele_id,
					"query_time_ms":responseTime,
					"response":response});
			}
			//console.log(response);
			// get the doc id (remove '_bookmark' from ele_id
			doc_id = ele_id.substr(0,ele_id.lastIndexOf("_"));
			// remove any previous feedback
			remove_feedback(doc_id);
			// show feedback, i.e., whether doc is relevant or not
			if (response.feedback === 1){
				add_pos_feedback(doc_id);
			}else if(response.feedback === -1){
				add_neg_feedback(doc_id);
			}else{ 
				console.log("error, no feedback");
			}
			
			// update the score (number of relevant documents found)
			update_user_score(response.userscore);
			// if the target of number of relevant documents has been
			// reached, quit this task. 
			if (response.done == true){
				submit_complete_task();
			}

			// update resultlist cache (with feedback and bookmark
			// decorations)
			rankid = $('#result-item_'+doc_id).parent().attr('id');
			//console.log(rankid);
			rankindex = parseInt(rankid.replace('rank_',''));
			item = '<div data-ilpslogging-groupid="'+rankid+'" id="'+rankid+'" class="list-group-item" name="doc-item">';
			item += $('#'+rankid).html();
			item += '</div>';
			RESULTLIST[rankindex]=item;
        });
}

// helper functions
// remove any type of feedback from a snippet
function remove_feedback(doc_id){
	$("#"+doc_id+"_title").removeClass("alert alert-danger alert-success");
	$("#result-item_"+doc_id).removeClass("result-item-correct result-item-error");
	$("#feedback_"+doc_id).html('');
}
// add positive feedback to a snippet
function add_pos_feedback(doc_id){
	$("#"+doc_id+"_title").toggleClass("alert alert-success");
	$("#result-item_"+doc_id).toggleClass("result-item-correct");
	$("#feedback_"+doc_id).html('<span data-ilpslogging-groupid="'+doc_id+'" class="bookcorrect glyphicon glyphicon-ok pull-right"></span>');
}
// add negative feedback to a snippet
function add_neg_feedback(doc_id){
	$("#"+doc_id+"_title").toggleClass("alert alert-danger");
	$("#result-item_"+doc_id).toggleClass("result-item-error");
	$("#feedback_"+doc_id).html('<span data-ilpslogging-groupid="'+doc_id+'" class="bookerror glyphicon glyphicon-remove pull-right"></span>'	);   
}

function update_user_score(userscore){
//	console.log(userscore.clicksleft);
	$('#clicks_left').html(userscore.clicksleft);
	$('#rel_found').html(userscore.rel_to_reach);
	$('#pgbar_c').attr('aria-valuenow', userscore.clicksleft);
	$('#pgbar_c').attr('style', "width:"+userscore.clicks_perc+'%');
	$('#pgbar_t').attr('aria-valuenow', userscore.relnum);
	$('#pgbar_t').attr('style', "width:"+userscore.rel_perc+'%');
}

function submit_complete_task(){
	//console.log("submit complete task")
	ILPSLogging.logEvent("completed_task",{});
	window.location = submit_complete_task_url;
}

function submit_uncomplete_task(){
	//console.log("submit uncomplete task")
	ILPSLogging.logEvent("gave_up_task",{});
	window.location = submit_uncomplete_task_url;
}

function category_click(ele_id){
	$('#'+current_active_category).toggleClass('active');
	//set this category to active
	$('#'+ele_id).toggleClass('active');
	// log category click
	ILPSLogging.logEvent("category_filter",{"node_id": ele_id});
	// change current category in state
	current_active_category = ele_id;
	var state = ILPSLogging.getState();
	state['current_category'] = ele_id;
	ILPSLogging.setState(state);
	//reset current_page to 1
	CURRENTPAGE = 1
	//reset current_pageination to 1
	CURRENT_PAGINATION_START = 1
	//Then regenerate the pagination
	pagination();
}

//Update the result list and pagination when an element 
//in the pagination is clicked
function update_pagination(ele_id){
//	var docs = ALLRANKS
//	if (typeof(current_active_category) != 'undefined'){	
//		if (current_active_category != 'category_all'){
//			docs = cate[1+parseInt(current_active_category.replace('category_',''))]['doc_ranks'];
//		}
//	}
	/*
	if (ele_id == 'pagination_first'){
		ILPSLogging.paginate(1,CURRENTPAGE);
		CURRENTPAGE = 1;
		pagination();
	}
	if (ele_id == 'pagination_last'){
		var lastpage = Math.ceil(docs.length/10);
		ILPSLogging.paginate(lastpage, CURRENTPAGE);
		CURRENTPAGE = lastpage;
		pagination();
	}
	if (ele_id == 'pagination_prev'){
		if (CURRENTPAGE > 1){
			ILPSLogging.paginate(CURRENTPAGE-1, CURRENTPAGE);
			CURRENTPAGE--;
			pagination();
		}
	}
	if (ele_id == 'pagination_next'){
		if (CURRENTPAGE < Math.ceil(docs.length/10)){
			ILPSLogging.paginate(CURRENTPAGE+1, CURRENTPAGE);
			CURRENTPAGE++;
			pagination();
		}
	}*/

	//It doesn't change the result list, just the
	//pagination options shown in the pagination	
	//Rotate pagination 1 step, and rebind the listener for logging
	//and clicking  
	if (ele_id == 'page_prev'){
        ILPSLogging.paginate(CURRENTPAGE-1, CURRENTPAGE);
		CURRENT_PAGINATION_START = CURRENT_PAGINATION_START-PAGINATION_SIZE;	
		CURRENTPAGE = CURRENT_PAGINATION_START+PAGINATION_SIZE-1;
		//pagination_html = create_pagination(docs);
		//update the look: but not updating the page!
		//$('#pagination').html(pagination_html);
		pagination();

	}
	else if (ele_id == 'page_next'){
        ILPSLogging.paginate(CURRENTPAGE+1, CURRENTPAGE);
		CURRENT_PAGINATION_START = CURRENT_PAGINATION_START + PAGINATION_SIZE;
		CURRENTPAGE = CURRENT_PAGINATION_START;

		//create the pagination look
		//pagination_html = create_pagination(docs);
		//update the look: but not updating the page!
		//$('#pagination').html(pagination_html);
		pagination();

	}
	//In this case, the look of pagination doesn't change
	//but the result list should change.
	else{
		CURRENTPAGE = parseInt(ele_id.split('_')[1]);
        ILPSLogging.paginate(CURRENTPAGE, CURRENTPAGE);
		pagination();
	}
//	bind_resultlist_listeners()
}

function pagination(){
	var docs = ALLRANKS; // category_all
	if (typeof(current_active_category) != 'undefined'){	
		if (current_active_category != 'category_all'){
			docs = cate[1+parseInt(current_active_category.replace('category_',''))]['doc_ranks'];
		}
	}
	$('#n_query_results').html(docs.length);
	// all future log events wiil have the updated list
	var state = ILPSLogging.getState();
	state['results_list'] = docs.slice(0,PAGESIZE);
	ILPSLogging.setState(state);

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
	var num_pages = Math.ceil(docs.length/10);
	//console.log(num_pages);
	var html = [];
	/*
	var prevpage = '-';
	if (CURRENTPAGE > 1){ prevpage = CURRENTPAGE - 1; }
	
	var nextpage = '-';
	if (CURRENTPAGE < docs.length/10){ nextpage = CURRENTPAGE + 1;}
	html = [
	'<ul class="pager">',
	  '<li><a id="pagination_first" class="pagination_marc"><span',
			'class="pull-left">First</span><span class="badge',
			'pull-right">1</span></a></li>',
	  '<li><a id="pagination_prev" class="pagination_marc"><span',
			'class="pull-left">Prev</span><span class="badge',
			' pull-right">',
			prevpage,
			' </span></a></li>',
	  '<li><a id="pagination_page" class="pagination_marc"><span',
			'class="pull-left">Page</span><span class="badge',
			' pull-right">',
			CURRENTPAGE,
			'</span></a></li>',
	  '<li><a id="pagination_next" class="pagination_marc"><span',
			'class="pull-left">Next</span><span class="badge',
			' pull-right">',
			nextpage,
			'</span></a></li>',
	  '<li><a id="pagination_last" class="pagination_marc"><span',
			'class="pull-left">Last</span><span class="badge',
			' pull-right">',
			Math.ceil(docs.length/PAGESIZE),
			'</span></a></li>',
	  '</ul>']
	*/

	html.push('<ul data-ilpslogging-groupid="pagination" class="pagination">');
	if (CURRENT_PAGINATION_START != 1){
		html.push('<li><a data-ilpslogging-groupid="pagination" id="page_prev" class="page">&laquo; Previous</a></li>');
	}
	// show the first 10 pages in pagination when new pagination is generated
	var last_page_show = Math.min(CURRENT_PAGINATION_START + PAGINATION_SIZE-1, num_pages);
	for (var i = CURRENT_PAGINATION_START; i <= last_page_show; i++){
		p = $.validator.format('<li><a data-ilpslogging-groupid="pagination" class="page" id="page_{0}">{1}</a></li>');
		//set current page
		if (i == CURRENTPAGE)
			p = $.validator.format('<li data-ilpslogging-groupid="pagination" class="active"><a class="page" id="page_{0}">{1}</a></li>');
		html.push(p(i, i));
	}
	//if there are more than 
	if (last_page_show < num_pages){
		html.push('<li><a data-ilpslogging-groupid="pagination" id="page_next" class="page">More &raquo; </a></li>');
	}	
	html.push('</ul>');
	return 	html.join( '\n');
}


function add_click(){
        $.ajax({type: "POST",
                url: add_click_url,
                data: { 
			task_id: task_id,
                }
        }).done(function(response) {
		update_user_score(response.userscore);		
		//console.log(response.userscore.clicksleft);
        if (response.done == true){
            submit_complete_task();
        }
	});
}

