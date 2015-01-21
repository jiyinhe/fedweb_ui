"""
Generate user gains for Marc
"""
import simplejson as js
from Configure import generalDir
import itertools

moves = 10
outputdir = 'data/'

def compute_gain(data, moves): 
    # seperate basic and category UIs
    basic = list(itertools.ifilter(lambda x: x['ui'] == 'basic', data))
    category = list(itertools.ifilter(lambda x: x['ui'] == 'category', data))
    
    # group by topics:
    basic = sorted(basic, key=lambda x: x['topic'])
    basic_data = []
    for k, g in itertools.groupby(basic, lambda x: x['topic']): 
        gains = []
        for gg in g:
            if gg['status'] == 'completed_task':
                gain = sum([int(a[1] == 1) for a in gg['actions'][0:moves]])
                gains.append(({'user':gg['user'], 'gain':gain}))
        if not gains == []:
            basic_data.append({'topic': k, 'gain_data': gains})
    

    category = sorted(category, key=lambda x: x['topic'])
    cat_data = []
    for k, g in itertools.groupby(category, lambda x: x['topic']): 
        gains = []
        for gg in g:
            if gg['status'] == 'completed_task':
                gain = sum([int(a[1] == 1) for a in gg['actions'][0:moves]])
                gains.append(({'user':gg['user'], 'gain':gain}))
        if not gains == []:
            cat_data.append({'topic': k, 'gain_data': gains})
 
    return {'basic_data': basic_data, 'category_data': cat_data}


if __name__ == '__main__':
    f = open(generalDir.processed_userdata)
    data = js.load(f)
    f.close() 

    data = compute_gain(data, moves)

    outputfile = '%s/usergain_moves%s.json'%(outputdir, moves)
    f = open(outputfile, 'w')
    js.dump(data, f)
    f.close()






