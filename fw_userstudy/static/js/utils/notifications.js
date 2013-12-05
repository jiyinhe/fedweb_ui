// basic
$(document).ready(function(){
	$("#notification_container").notify();
	notify_onstart();
});

var block_notifications = {};

function notify_onstart(){
	if (typeof block_notifications.close_notifications == 'undefined'){
		$("#notification_container").notify("create",{
				title:'Notifications', 
				text:'These notifications provide hints. To get rid of them click on the x.'
			},{
				close: function(){
					block_notifications.close_notifications=true;
				},
				expires: false
		});
	}

	if (typeof block_notifications.topic_description == 'undefined'){
		$("#notification_container").notify("create","topic-panel-notification",{
				title:'Topic descrition', 
				text:'The topic description asks to find 10 documents that a user who typed these keywords would find relevant.'
			},{
				close: function(){
					block_notifications.topic_description=true;
					$("#topic-panel").removeClass("panel-hover");
				},
				expires: false
		});

		$(".topic-panel-notification").mouseenter(function(){
			$("#topic-panel").addClass("panel-hover");
		});
		$(".topic-panel-notification").mouseleave(function(){
			$("#topic-panel").removeClass("panel-hover");
		});
	}

	if (typeof block_notifications.view_doc == 'undefined'){
		$("#notification_container").notify("create","docview-notification",{
				title:'Viewing documents', 
				text:'By clicking the URL you can inspect the complete document.'
			},{
				close: function(){
					block_notifications.view_doc=true;
					$("#rank_0").find(".doc_title").removeClass("panel-hover");
				},
				expires: false
		});

		$(".docview-notification").mouseenter(function(){
			$("#rank_0").find(".doc_title").addClass("panel-hover");
		});
		$(".docview-notification").mouseleave(function(){
			$("#rank_0").find(".doc_title").removeClass("panel-hover");
		});
	}
}

function notify_feedback(feedback){
	console.log(block_notifications.positive_feedback);
	console.log(block_notifications.negative_feedback);
	console.log(block_notifications.delete_feedback);
	if (feedback == "positive_feedback"){	
		if (typeof block_notifications.positive_feedback == 'undefined'){
			$("#notification_container").notify("create",{
					title:'Bookmarking documents', 
					text:'Great, you bookmarked one of the documents relevant to the topic!'
				},{
					close: function(){
						block_notifications.positive_feedback=true;
					},
					speed: 1000
			});
		}
	}
	if (feedback == "negative_feedback"){
		if (typeof block_notifications.negative_feedback == 'undefined'){
			$("#notification_container").notify("create",{
					title:'Bookmarking documents', 
					text:'Hmm, you bookmarked a document that does not seem very relevant to the topic. '
				},{
					close: function(){
						block_notifications.negative_feedback=true;
					},
					speed: 1000
			});
		}
	}
	if (feedback == "delete_feedback"){
		if (typeof block_notifications.delete_feedback == 'undefined'){
			$("#notification_container").notify("create",{
					title:'Bookmarking documents', 
					text:'Yes, by clicking the bookmark button again you can delete previously bookmarked documents.'
				},{
					close: function(){
						block_notifications.delete_feedback=true;
					},
					speed: 1000
			});
		}
	}
}
