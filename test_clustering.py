from collections import defaultdict
from clustering import SenseClustering
import random

def simple_test():
    test_instances = defaultdict(lambda : defaultdict(int))

    words = ['hoi', 'blaat', 'hond', 'boe']
    occ_id = 0

    for i in range(50):
        for w in words:
            test_instances[occ_id][w]=6+random.randrange(-1,2)
        occ_id+=1
            
    for i in range(50):
        for w in words:
            test_instances[occ_id][w]=10+random.randrange(-1,2)
        occ_id+=1
            
    for i in range(50):
        for w in words:
            test_instances[occ_id][w]=15+random.randrange(-1,2)
        occ_id+=1
            
    # for key in test_instances:    
        # for w in words:
            # print(test_instances[key][w]),
        # print('\n'),
        
            
    clusterer = SenseClustering(test_instances, words)
    clusterer.buckshot_clustering([2,3])
    
# def real_test():

if __name__ == '__main__': #if this file is the argument to python
  simple_test()