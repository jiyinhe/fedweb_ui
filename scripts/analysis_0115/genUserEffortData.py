"""
Generate user gains for Marc
"""
import simplejson as js
from Configure import generalDir
import itertools

outputdir = 'data/'

def compute_gain(data): 
    # seperate basic and category UIs
    basic = list(itertools.ifilter(lambda x: x['ui'] == 'basic', data))
    category = list(itertools.ifilter(lambda x: x['ui'] == 'category', data))
    
    # group by topics:
    basic = sorted(basic, key=lambda x: x['topic'])
    basic_data = []
    for k, g in itertools.groupby(basic, lambda x: x['topic']): 
        efforts = []
        for gg in g:
            if gg['status'] == 'completed_task':
                effort = len(gg['actions'])
                efforts.append(({'user':gg['user'], 'effort':effort}))
        if not efforts == []:
            basic_data.append({'topic': k, 'effort_data': efforts})
    

    category = sorted(category, key=lambda x: x['topic'])
    cat_data = []
    for k, g in itertools.groupby(category, lambda x: x['topic']): 
        efforts = []
        for gg in g:
            if gg['status'] == 'completed_task':
                effort = len(gg['actions'])
                efforts.append(({'user':gg['user'], 'effort':effort}))

        if not efforts == []:
            cat_data.append({'topic': k, 'effort_data': efforts})
 
    return {'basic_data': basic_data, 'category_data': cat_data}


if __name__ == '__main__':
    f = open(generalDir.processed_userdata)
    data = js.load(f)
    f.close() 

    data = compute_gain(data)

    outputfile = '%s/usereffort.json'%(outputdir)
    f = open(outputfile, 'w')
    js.dump(data, f)
    f.close()






