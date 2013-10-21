from collections import defaultdict
from clustering import SenseClustering
import random

import document_counter
from docreader import Doc #needed for pickling call
import utilities

# werkt niet meer zo na maken threaded
"""
def simple_test():
  test_instances = defaultdict(lambda : defaultdict(int))

  words = ['hoi', 'blaat', 'hond', 'boe']
  occ_id = 0

  for i in range(20):
    for w in words:
      test_instances[occ_id][w]=5+random.randrange(-1,2)
    occ_id+=1
       
  for i in range(20):
    for w in words:
      test_instances[occ_id][w]=10+random.randrange(-1,2)
    occ_id+=1
       
  for i in range(20):
    for w in words:
       test_instances[occ_id][w]=15+random.randrange(-1,2)
    occ_id+=1
         
  print utilities.getDictString(test_instances)

      
         
  clusterer = SenseClustering(test_instances, words)
  # print clusterer.eucl_distance(test_instances[10], test_instances[30])
  # print clusterer.eucl_distance(test_instances[10], test_instances[11])
  # print clusterer.eucl_distance(test_instances[30], test_instances[60])
  # print clusterer.eucl_distance(test_instances[30], test_instances[31])
  # print clusterer.eucl_distance(test_instances[10], test_instances[60])   
  # print clusterer.eucl_distance(test_instances[61], test_instances[60])   
  
  #clusterer.buckshot_clustering([2,3])
   
"""

def rl_test():
  (queryWords, queryDict, allContextWords) = document_counter.getQueriesAndQuerySensesDictAndCW()
  
  #print queryWords
  #print utilities.getDictString(queryDict)
  
  #queryWord = queryWords[2]
  #allQuerySenses = queryDict[queryWord]
  #print queryWord
  #print utilities.getDictString(allQuerySenses)
  
  clusterer = SenseClustering(queryWords, queryDict, allContextWords, list_of_k=[2,3])
  
  clusterer.run()
  
  resultPerQuery  = clusterer.resultPerQuery
  
  print utilities.getDictString(resultPerQuery[queryWords[2]])
  
if __name__ == '__main__': #if this file is the argument to python
  #simple_test()
  rl_test()
