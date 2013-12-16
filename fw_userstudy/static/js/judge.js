$(document).ready(function(){
	//set the active crawl tab
	set_active_crawl();
	$('.crawl_tab').click(function(){
		console.log($(this).attr('value'));
		change_crawl($(this).attr('value'));
	});					

	//filter tooltip
	$('[rel=tooltip]').tooltip({
		placement: "auto",
	});

	//to filter snippets
	$('#hide_nonrel').click(function(){
		//change the button label
		console.log($(this).text())
		if ($(this).text().trim() == 'Filter snippets'){
			filter_snippets();
			$(this).text('un-Filter snippets');
		}
		else{
			unfilter_snippets();
			$(this).text('Filter snippets');
		}
	});
	//dropwdown
	$('.collapse').collapse()

	//change query
	$('.query-item').click(function(){
		change_query($(this));
	});
});

// adjust the category area length
$('.affix-right').ready(function(){
	$('.affix-right').height($(window).height()-70);	
});	

//global variable

var rel_levels = ['Nav', 'Key', 'HRel', 'Rel', 'Non', 'Spam'];
var colors = ['primary', 'success', 'info', 'warning', 'danger', 'default'];
var total_docs = 0;
var judged_s = 0;
var judged_p = 0;

function set_active_crawl(){
	id = '#crawl_li'+current_crawl;
	$(id).addClass('active');
	load_docs();
}

function change_crawl(crawl_id){
	$('#crawl_li'+current_crawl).removeClass('active');
	$('#crawl_li'+crawl_id).addClass('active');
	current_crawl = crawl_id;
	$('#crawl_id').html(crawl_id);
	load_docs();
}
function load_docs(){
	if (current_crawl == -1 || current_query == -1){
		$('#documents').html('You have completed judging current query and crawl, thank you!');
	}
	
	//send selection to db
	$.ajax({
                type: "POST",
                url: load_results_url,
                data: {
			current_crawl: current_crawl,
			current_query: current_query,
                      }
        }).done(function(response) {
		show_results(response);		
		set_progress_bar(response);	
	});
}

function show_results(docs){	
    var html = []
    if (docs.length == 0)
	$('#document').html('No results were crawled.');

    for (var i = 0; i<docs.length; i++){
	r = docs[i][0]
	result_html = []
	
	result_html.push('<div class="list-group-item doc-item" name="doc-item" id="doc-item_'+r['id']+'">');
	result_html.push('<div id="result-item_'+r['id']+'" class="result-item">');

	result_html.push('<div id="'+r['id']+'_title" name="'+r['title']+'" class="list-group-item-heading">');
	result_html.push('<span class="label label-info">'+r['site_name']+' #'+r['rank']+'</span>')
	result_html.push('<span class="doc_title" id="'+r['id']+'" data-toggle="modal" data-target="#docModal">');
	result_html.push(r['title']);
	result_html.push('</span>');
	result_html.push('<span class="pull-right">#'+(i+1)+'</span>')	
	result_html.push('</div>'); //Group heading
	result_html.push('<div class="doc_url" id="url_'+r['id']+'" >'+r['url']+'</div>');
	result_html.push('<div class="judge" id="judge_snippet_'+r['id']+'">'+'</div>');
	result_html.push('<div class="list-group-item-text" id="summary_'+r['id']+'">');
	result_html.push(r['summary']);
	result_html.push('</div>');//Group-item-text
	result_html.push('</div>');//result-item

	//the judgement bar for snippets
	result_html.push('<div class="alert alert-warning space5">');
	result_html.push('<span class="pull-right save_s" id="save_s_'+r['id']+'">');
	//set the saved value label
	saved_label = set_saved_value(r['id'], 'snippet', r['judge']);
	result_html.push(saved_label);
	result_html.push('<span class="pull-right">Snippet relevance: </span></span> ');
	//draw the buttons
	result_html.push(judge_buttons(r['id'], 'snippet', r['judge']));
	result_html.push('</div>');

	//the judgement bar for document
	result_html.push('<div class="alert alert-success space5">');
	result_html.push('<span class="pull-right save_p" id="save_p_'+r['id']+'">');
	//set the saved value_label
	saved_label = set_saved_value(r['id'], 'page', r['judge']);	
	result_html.push(saved_label);
	result_html.push('<span class="pull-right">Page relevance:</span></span> ');
	//show the saved result
	result_html.push(judge_buttons(r['id'], 'page', r['judge']));
	result_html.push('</div>');

	result_html.push('</div>');//doc-item
	html.push(result_html.join('\n'));
	}
   $('#documents').html(html.join('\n'));
   //enable buttons
   $('.btn').button();
}

//Create the button for relevance judgement
function judge_buttons(res_id, rel_type, judge){
	html = []
	//get the saved relevance judgement
	var rel = 0;
	if (rel_type == 'snippet')
		rel = judge['relevance_snippet'];
	else if (rel_type == 'page')
		rel = judge['relevance_doc'];
	var select_id = 6-rel;
	var active = ''
	for (var i = 0; i<6; i++){
		if (select_id == i){
			active = 'active';
			checked = 'checked';
		}
		else{
			active = '';
			checked = '';
		}	
		html.push('<div class="btn-group" id="btn-group_'+res_id+'">');
		btn_id = [rel_levels[i], res_id, rel_type].join('_')
  		html.push('<label class="btn btn-'+colors[i]+' btn-xs '+active+'" id="'+btn_id+'" onClick=rel_click(id)>');
    		html.push('<input type="radio" value="'+rel_levels[i]+'" id="radio_'+btn_id+'" '+checked+'>');
		html.push(rel_levels[i]);
  		html.push('</label>');
		html.push('</div>');
	}
	return html.join('\n')
}

function set_saved_value(result_id, result_type, judge){
	saved_value = [];
	if (result_type == 'snippet' && judge['relevance_snippet']>0){
		label_idx = 6 - judge['relevance_snippet'];
		id = 'save_s_'+result_id;
		saved_value = ['<span class="label label-'+colors[label_idx]+' pull-right" id="'+id+'">'];
		saved_value.push(rel_levels[label_idx]);
		saved_value.push('</span>');
	
	}
	else if (result_type == 'page' && judge['relevance_doc']>0){
		label_idx = 6 - judge['relevance_doc'];
		id = 'save_p_'+result_id;
		saved_value = ['<span class="label label-'+colors[label_idx]+' pull-right" id="'+id+'">'];
		saved_value.push(rel_levels[label_idx]);
		saved_value.push('</span>');
	}
	return saved_value.join('\n');
}


function rel_click(id){
	strs = id.split('_');
	rel = strs[0];
	//set all others to inactive, and set the selected one to active
	for (i in rel_levels){
		idx = [rel_levels[i], strs[1], strs[2]].join('_');
		$('#'+idx).removeClass('active');
		$('#radio_'+idx).prop('checked', false);
	}
	$('#'+id).addClass('active');
	$('#radio_'+id).prop('checked', true);

	//save the click
 	$.ajax({
                type: "POST",
                url: save_judge_url,
                data: {
			current_query: current_query,
			current_crawl: current_crawl,
			result_id: strs[1],
			judge_type: strs[2],
			judge: strs[0],
			total_docs: total_docs,
			s_count: judged_s,
			p_count: judged_p,
	}
        }).done(function(response) {
		//get the progress
		judged_s = response['s_count'];
		judged_p = response['p_count'];
		//console.log(judged_s+' '+judged_p);

		label_idx = rel_levels.indexOf(strs[0]);
		saved_value = ['<span class="label label-'+colors[label_idx]+' pull-right save_label">'];
		saved_value.push(strs[0])
		saved_value.push('</span>')
		//show the saved result
		if (strs[2] == 'snippet'){
			saved_value.push('<span class="pull-right">Snippet relevance: </span>');
			$('#save_s_'+strs[1]).html(saved_value.join('\n'));
			// if snippet is Non or Spam, then by default set doc to Non/spam
			// so also show the doc judgement
			if (response['relevance_snippet']<3){
                		label_idx = 6-response['relevance_doc'];
                		saved_value[0] = ['<span class="label label-'+colors[label_idx]+' pull-right">'];
				saved_value[1] = rel_levels[label_idx]; 
				saved_value[saved_value.length-1] = '<span class="pull-right">Page relevance: </span>';
				$('#save_p_'+strs[1]).html(saved_value.join('\n'));
				//also update the button selection
				//set all others to inactive, and set the selected one to active
				for (i in rel_levels){
					idx = [rel_levels[i], strs[1], 'page'].join('_');
					$('#'+idx).removeClass('active');
					$('#radio_'+idx).prop('checked', false);
				}
				var page_id = id.replace('snippet', 'page');
				$('#'+page_id).addClass('active');
				$('#radio_'+page_id).prop('checked', true);
				//also update progress
				update_progress_bar('page');	
			}
		}
		else if (strs[2] == 'page'){
			saved_value.push('<span class="pull-right">Page relevance: </span>');
			$('#save_p_'+strs[1]).html(saved_value.join('\n'));
		}
		update_progress_bar(strs[2]);
        });

}

//filer out snippets that are judged non-relevant or spam
function filter_snippets(){
	X = $('.doc-item').filter(function(index){
		id = '#save_s_'+$(this).attr('id').split('_')[1];
		val = $(id).text().split('Snippet')[0].trim();
		return val=='Non' || val == 'Spam';
	})
	X.addClass('hidden');
}
	
function unfilter_snippets(){
	$('.hidden').removeClass('hidden');
}	

function set_progress_bar(){
	//get the total number of docs in this crawl
	total_docs = $('.doc-item').length;
	//get the judged ones	
	judged_s = $('.save_s').filter(function(index){
		return $(this).text().split('Snippet')[0].trim() != ''
	}).length;	
	judged_p = $('.save_p').filter(function(index){
		return $(this).text().split('Page')[0].trim() != ''
	}).length;

	$('#pg_s').html(judged_s+'/'+total_docs);
	$('#pg_p').html(judged_p+'/'+total_docs);
	$('#pgbar_s').attr('aria-valuenow', judged_s/total_docs*100).css('width', judged_s/total_docs*100+'%');
	$('#pgbar_p').attr('aria-valuenow', judged_p/total_docs*100).css('width', judged_p/total_docs*100+'%');	
}

function update_progress_bar(judge_type){
	if (judge_type == 'snippet'){
		$('#pg_s').html(judged_s+'/'+total_docs);
		$('#pgbar_s').attr('aria-valuenow', judged_s/total_docs*100).css('width', judged_s/total_docs*100+'%');
	}
	else if (judge_type == 'page'){
		$('#pg_p').html(judged_p+'/'+total_docs);
		$('#pgbar_p').attr('aria-valuenow', judged_p/total_docs*100).css('width', judged_p/total_docs*100+'%');	
	}
}


function change_query(query_item){
	qid = query_item.attr('id').split('_')[1];	
	//set the form value
	$('#query_select').attr('value', qid);
	//submit the form to the same url
	$('#query').submit();
}


