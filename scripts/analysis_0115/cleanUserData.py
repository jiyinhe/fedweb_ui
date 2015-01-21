"""
Clean up the raw user data, generate the user data
for analysis
"""
from Configure import generalDir
import itertools
from datetime import datetime
from datetime import timedelta
from dateutil.parser import *
import simplejson as js

outputfile = generalDir.processed_userdata

def load_user_data():
    f = open(generalDir.raw_userdata)
    content = f.read()
    data = eval(content)
    f.close()
    return data    

def get_bookmarks(entry):
# First get all the bookmarks
    norank = 0
    clicked = []
    bookmarks = list(itertools.ifilter(lambda x: x[2] == 'bookmark' or (x[2] ==
'mouse_click'), entry))
    for i in range(len(bookmarks)):
        time, url, action, postlist, info = bookmarks[i]
        # We only care about the correct bookmarks
        if action == 'bookmark':
            #if info[2] == -1:
            #    continue
            rel = info[2]
 
            time = parse(time)
            # find previous and next click
            time1, time2, info1, info2 = [0, 0, [], []]
            j = i - 1 
            bookmarks1, bookmarks2 = [], []
            while j >= 0:
                # If postlists are not the same, they are not the same event
                if bookmarks[j][2] == 'mouse_click' and bookmarks[j][3] == postlist:
                    time1, url1, action1, postlist1, info1 = bookmarks[j]
                    if info1 == []:
                        j += -1
                        continue
                    bookmarks1 =  bookmarks[j]
                    break
                j += -1 

            j = i + 1
            while j < len(bookmarks):
                if bookmarks[j][2] == 'mouse_click' and bookmarks[j][3] == postlist:
                    time2, url2, action2, postlist2, info2 = bookmarks[j]
                    if info2 == []:
                        j += 1
                        continue
                    bookmarks2 =  bookmarks[j]
                    break
                j += 1

            # Get the cloest click which has the same postlist
            clicked_rank = 'rank'
            delta1 = timedelta(seconds=1)
            if not time1 == 0:
                delta1 = time - parse(time1)
            delta2 = timedelta(seconds=1)
            if not time2 == 0:
                delta2 = parse(time2) - time

            #print time1, delta1, info1
            #print time2, delta2, info2

            # delta should be smaller than 1s 
            if (delta1 == timedelta(seconds=1) and delta2 == timedelta(seconds=1)):
                print 'ERROR: both empty'
            else: 
                if delta1 == timedelta(seconds=1):
                    if info2 == []:
                        norank += 1
                    else:
                        clicked_rank = (int(info2[0].split('_')[1]), rel)
                #    print clicked_rank
                elif delta2 == timedelta(seconds=1):
                    if info1 == []:
                        norank += 1
                    else:
                        clicked_rank = (int(info1[0].split('_')[1]), rel)
                #    print clicked_rank
                else:
                    if delta1 < delta2:
                        if info1 == []:
                            norank += 1
                        else:
                            clicked_rank = (int(info1[0].split('_')[1]), rel)
                    #    print clicked_rank
                    elif  delta2 < delta1:
                        if info2 == []:
                            norank += 1
                        else:
                            clicked_rank = (int(info2[0].split('_')[1]), rel)
            if not clicked_rank == 'rank':
                clicked.append(clicked_rank)
    return clicked, norank

def user_sequence(data):
# For each user and query,  generate the sequence of
# actions and documents exmined 
# Information in each sequence:
# - action_type
# - relevance of each document dealt 
# 1: cheked and relevant; -1: checked and not relevant; 0: not checked
    sessions = []
    completed = 0
    for d in data:
        user, query = d
        if user == '':
            print d
        elif user%2 == 1:
            user_type = 'category'
        else:
            user_type = 'basic'
#        print user_type
        session_type = 'unknown'
        # First get bookmarks
        bookmarks, norank = get_bookmarks(data[d])
        bookmarks = dict(bookmarks)
        # use this to keep track of the visit of snippet in the last page
        last_hover = 0
        i = 0
        actions = []
        for time, url, action, postlist, info  in data[d]:
            #print time, url, action, postlist, info
            if action == 'mouse_movements' or action == 'mouse_click':
                if not (info == [] or ('example' in [str(x).split('_')[0] for x in
info])):
                    last_hover = i
            elif action == 'paginate':
                # Assume user has examined all docs in previous page
                for rank in postlist:
                    # check if this rank is relevant in bookmarks
                    gain = bookmarks.get(rank, 0)
                    actions.append(['examine', gain])
                actions.append(['pagination', 0])

            elif action == 'category_filter':
                for rank in postlist:
                    # check if this rank is relevant in bookmarks
                    gain = bookmarks.get(rank, 0)
                    actions.append(['examine', gain])
                actions.append(['category_filter', 0])
            elif action == 'completed_task' or action == 'give_up_task':
                if action == 'completed_task':
                    completed += 1
                session_type = action
                #print data[d][last_hover]
                # Get last hover, that's the stop point of examine
                lasthover = sorted([int(x.replace('rank_', '')) for x in data[d][last_hover][-1]])
                for rank in postlist:
                    gain = bookmarks.get(rank, 0)
                    actions.append(('examine', gain))
                    if rank == lasthover[-1]:
                        break; 
            i += 1
        # Some sessions are not finished, but put them in anyways
        if session_type == 'unknown':
            if len(data[d]) > 0:
                lasthover = sorted([int(str(x).replace('rank_', '')) for x in data[d][last_hover][-1]])
                for rank in postlist:
                    gain = bookmarks.get(rank, 0)
                    actions.append(('examine', gain))
                    if not(lasthover == []) and rank == lasthover[-1]:
                        break; 
        sessions.append({'user': user, 'topic': query, 'status': session_type,
'ui': user_type, 'actions': actions})
    print completed
    return sessions
 
if __name__ == '__main__':
    data = load_user_data() 
    sessions = user_sequence(data)

    f = open('%s'%outputfile, 'w')
    js.dump(sessions, f)
    f.close()






