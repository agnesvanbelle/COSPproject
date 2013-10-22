from collections import defaultdict
from clustering import SenseClustering
import random

import document_counter
from docreader import Doc #needed for pickling call
import utilities
import similaritiesWriter as sim_w

def get_fake_data_sim():
  docs = defaultdict(lambda : defaultdict(lambda : defaultdict(double)))
  query_words = ['hoi', 'kameel', 'betalen', 'bank']
  c_words = ['caravan', 'kameel', 'hond', 'boe', ]
  raw_queries = ['hoi kameel', 'betalen bank']
  queries = [['hoi','kameel'], ['betalen', 'bank']]
  
  senses ={}
  senses['hoi'] = {1:{'caravan': 0.03, 'kameel': 0.1, 'bank': 0.07, 'boe': 0.8} , 2: {'caravan': 0.2, 'kameel': 0.7, 'bank': 0.05, 'boe': 0.05}}
  senses['kameel'] = {1:{'caravan': 0.03, 'kameel': 0.1, 'bank': 0.8, 'boe': 0.07} , 2: {'caravan': 0.2, 'kameel': 0.6, 'bank': 0.15, 'boe': 0.05}}
  senses['betalen'] = {1:{'caravan': 0.1, 'kameel': 0.1, 'bank': 0.75, 'boe': 0.05} , 2: {'caravan': 0.2, 'kameel': 0.7, 'bank': 0.05, 'boe': 0.05}}
  senses['bank'] = {1:{'caravan': 0.05, 'kameel': 0.05, 'bank': 0.1, 'boe': 0.8} , 2: {'caravan': 0.1, 'kameel': 0.6, 'bank': 0.25, 'boe': 0.05}}
  
  doc_sense ={}
  doc_sense ['hoi'] = {'caravan': 0.03, 'kameel': 0.1, 'bank': 0.07, 'boe': 0.8} 
  doc_sense['kameel'] = {'caravan': 0.03, 'kameel': 0.1, 'bank': 0.8, 'boe': 0.07} 
  doc_sense['betalen'] = {'caravan': 0.1, 'kameel': 0.1, 'bank': 0.75, 'boe': 0.05} 
  doc_sense['bank'] = {'caravan': 0.05, 'kameel': 0.05, 'bank': 0.1, 'boe': 0.8}
   
  for i in range(6):
    for q in query_words:
      docs[i][q] = doc_sense[q]
    
  return (docs, query_words, c_words, raw_queries, senses, queries)

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
         
def test_similarity_calculation():
  (docs, query_words, c_words, raw_queries, senses, queries) = get_fake_data_sim()
  
  #senses_dict, doc_vectors, queries, context_words, raw_queries
  sim_w.write_similarities_to_CSV(senses, docs, queries, c_words, raw_queries)

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
  
  # print utilities.getDictString(resultPerQuery[queryWords[2]])
  
if __name__ == '__main__': #if this file is the argument to python
  #simple_test()
  # rl_test()
  test_similarity_calculation()
