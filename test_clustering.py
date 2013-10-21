from collections import defaultdict
from clustering import SenseClustering
import random

import document_counter
from docreader import Doc #needed for pickling call
import utilities

def get_fake_data():
  test_instances = defaultdict(lambda : defaultdict(lambda : defaultdict(int)))

  query_words = ['hoi', 'doei']
  c_words = ['hoi', 'blaat', 'hond', 'boe']
  
  for qw in query_words: 
    
    occ_id = 0

    for i in range(20):
      for w in c_words:
        test_instances[qw][occ_id][w]=5+random.randrange(-1,2)
      occ_id+=1  
    
    for i in range(20):
      for w in c_words:
        test_instances[qw][occ_id][w]=10+random.randrange(-1,2)
      occ_id+=1
         
    for i in range(20):
      for w in c_words:
         test_instances[qw][occ_id][w]=15+random.randrange(-1,2)
      occ_id+=1     
  
  return(query_words, test_instances, c_words)
         
  
   

def rl_test():
  (queryWords, queryDict, allContextWords) = document_counter.getQueriesAndQuerySensesDictAndCW()
  # (queryWords, queryDict, allContextWords) = get_fake_data()
  
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
