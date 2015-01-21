"""
Analyze the correlation between predicted and actual user effort/gain
"""
from Configure import util, generalDir, perQueryEffort, perQueryGain
import simplejson as js
import itertools
import numpy as np
from scipy import stats
import pylab

userdata_dir = 'data/'
user_effort_file = '%s/usereffort.json'%userdata_dir
user_gain_file = lambda x: '%s/usergain_moves%s.json'%(userdata_dir, x)

def load_data(datafile):
    f = open(datafile)
    data = js.load(f)
    f.close()
    return data

def simple_stats(data):
    # simple statistics, to verify with previous results
    completed_basic = list(itertools.ifilter(lambda x: x['status']=='completed_task' and
x['ui'] == 'basic', data))
    completed_cat = list(itertools.ifilter(lambda x: x['status']=='completed_task' and
x['ui'] == 'category', data))

    completed_basic.sort(key=lambda x: x['topic'])
    basic_per_task = [(len(list(g))) for k, g in itertools.groupby(completed_basic, lambda x: x['topic'])]

    completed_cat.sort(key=lambda x: x['topic'])
    cat_per_task = [(len(list(g))) for k, g in itertools.groupby(completed_cat, lambda x: x['topic'])]

    print 'Completed tasks - basic: %s'%len(completed_basic)
    print 'Median completion per topic:', np.median(basic_per_task)
    print 'Completed tasks - category: %s'%len(completed_cat)
    print 'Median completion per topic:', np.median(cat_per_task)


def get_effort_data(): 
    data = load_data(user_effort_file) 
    basic_data = dict([(d['topic'], np.median([x['effort'] for x in d['effort_data']])) for d in data['basic_data']])
    cat_data = dict([(d['topic'], np.median([x['effort'] for x in d['effort_data']])) for d in data['category_data']])
    keys = sorted(list(set(cat_data).intersection(set(basic_data))))
    return basic_data, cat_data, keys

def get_gain_data(moves):
    data = load_data(user_gain_file(moves))
    basic_data = dict([(d['topic'], np.median([x['gain'] for x in d['gain_data']])) for d in data['basic_data']])
    cat_data = dict([(d['topic'], np.median([x['gain'] for x in d['gain_data']])) for d in data['category_data']])
    keys = sorted(list(set(cat_data).intersection(set(basic_data))))
    return basic_data, cat_data, keys


def correlate_user_basic_facet():
    # Correlation between user effort/gain on faceted interface and basic interface 
    # Effort based
    print 'Does user performance of a faceted UI correlates to their performance with a basic UI?'
    print 
    basic_data, cat_data, keys = get_effort_data()
    X = [basic_data[x] for x in keys]
    Y = [cat_data[x] for x in keys]
    r, p = stats.pearsonr(X, Y)
    print 'Median number of moves to achieve 10 relevant documents:', 'basic -', np.median(X), np.percentile(X, 25), np.percentile(X, 75), 'category-', np.median(Y), np.percentile(Y, 25), np.percentile(Y, 75)
    print 'Correlation actual user effort with basic vs. facet UI:', r, p
    print

    # Gain based
    for moves in [10, 20, 50, 100, 200, 500]:
        basic_data, cat_data, keys = get_gain_data(moves)
        X = [basic_data[x] for x in keys]
        Y = [cat_data[x] for x in keys]
        r, p = stats.pearsonr(X, Y)
        print 'Moves=', moves
        print 'Correlation actual user gain with basic vs. facet UI:', r, p



def correlate_user_effort_gain():
    # What's the relation between effort and gain? On real user data
    print 
    print 'What is the relation between effort and gain -- observations from real user data'
    basic_data, cat_data, keys = get_effort_data()
    basic_effort = [basic_data[x] for x in keys]
    cat_effort = [cat_data[x] for x in keys]
 
    for moves in [10, 20, 50, 100, 200, 500]:
        basic_data, cat_data, keys2 = get_gain_data(moves)
        # make keys2 a dummy variable, use keys from effort data
        basic_gain = [basic_data[x] for x in keys]
        cat_gain = [cat_data[x] for x in keys]
 
        print 'Moves = %s'%moves
        r, p = stats.pearsonr(basic_effort, basic_gain)
        print 'Correlation between effort and gain - basic UI:', r, p
        r, p = stats.pearsonr(cat_effort, cat_gain)
        print 'Correlation between effort and gain - facet UI', r, p
        print
    print


if __name__ == '__main__':
    correlate_user_basic_facet()
    correlate_user_effort_gain()





