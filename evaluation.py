from utilities import pairedTtest
import numpy

from collections import defaultdict

import sys

num_rel = [16,
          17,
          14,
          15,
          61,
          1,
          77,
          11,
          10,
          63,
          54,
          31,
          20,
          18,
          59,
          118,
          30,
          9,
          19,
          16,
          0,
          14,
          26,
          74,
          61 ]



def calcRecall(num_rel_ret):
  n_rel = numpy.array(num_rel)
  n_rel_ret = numpy.array(num_rel_ret)
  
  
  
  recall = list(n_rel_ret / n_rel)
  recall2 = [x if (x != float('Inf') and not numpy.isnan(x))  else 0 for x in recall]

  return recall2
  
def readFile(filename):
  
  f = open(filename, 'r')
  
  resultList = []
  
  for line in f:
    split = line.split()
    if split[1] != 'all':
      resultList.append(float(split[2]))
      
  f.close()

  return resultList



def getSupervised():
  
  P_10 = readFile('results/supervised/per_query_p_10.txt')
  
  Num_rel_ret = readFile('results/supervised/per_query_num_rel_ret.txt')
  Recall = calcRecall(Num_rel_ret)
  
  MAP = readFile('results/supervised/per_query_map.txt')
  
  Recip_rank = readFile('results/supervised/per_query_recip_rank.txt')
  
  
  
  return (P_10, Recall, MAP, Recip_rank)
  

def getQsGf2():
  
  P_10 = readFile('results/qs_gf2/per_query_p_10.txt')
  
  Num_rel_ret = readFile('results/qs_gf2/per_query_num_rel_ret.txt')
  Recall = calcRecall(Num_rel_ret)
  
  MAP = readFile('results/qs_gf2/per_query_map.txt')
  
  Recip_rank = readFile('results/qs_gf2/per_query_recip_rank.txt')
  
  return (P_10, Recall, MAP, Recip_rank)

def getQsGf():
  
  P_10 = readFile('results/qs_gf/per_query_p_10.txt')
  
  Num_rel_ret = readFile('results/qs_gf/per_query_num_rel_ret.txt')
  Recall = calcRecall(Num_rel_ret)
  
  MAP = readFile('results/qs_gf/per_query_map.txt')
  
  Recip_rank = readFile('results/qs_gf/per_query_recip_rank.txt')
  
  return (P_10, Recall, MAP, Recip_rank)
  

def getQsGc():
  
  P_10 = readFile('results/qs_gc/per_query_p_10.txt')
  
  Num_rel_ret = readFile('results/qs_gc/per_query_num_rel_ret.txt')
  Recall = calcRecall(Num_rel_ret)
  
  MAP = readFile('results/qs_gc/per_query_map.txt')
  
  Recip_rank = readFile('results/qs_gc/per_query_recip_rank.txt')
  
  return (P_10, Recall, MAP, Recip_rank)
  
def getQnGf():
  
  P_10 = readFile('results/qn_gf/per_query_p_10.txt')
  
  Num_rel_ret = readFile('results/qn_gf/per_query_num_rel_ret.txt')
  Recall = calcRecall(Num_rel_ret)
  
  MAP = readFile('results/qn_gf/per_query_map.txt')
  
  Recip_rank = readFile('results/qn_gf/per_query_recip_rank.txt')
  
  return (P_10, Recall, MAP, Recip_rank)
  

def getQnGc():
  
  P_10 = readFile('results/qn_gc/per_query_p_10.txt')
  
  Num_rel_ret = readFile('results/qn_gc/per_query_num_rel_ret.txt')
  Recall = calcRecall(Num_rel_ret)
  
  MAP = readFile('results/qn_gc/per_query_map.txt')
  
  Recip_rank = readFile('results/qn_gc/per_query_recip_rank.txt')
  
  return (P_10, Recall, MAP, Recip_rank)
  

def getBaselineResults():

  P_10 = readFile('results/baseline/baseline_p_10.txt')
  
  Num_rel_ret = readFile('results/baseline/baseline_num_rel_ret_per_query.txt')
  Recall = calcRecall(Num_rel_ret)
  
  MAP = readFile('results/baseline/baseline_MAP_per_query.txt')
  
  Recip_rank = readFile('results/baseline/baseline_RecipRank_per_query.txt')
  
  return (P_10, Recall, MAP, Recip_rank)

  

def compareWithBaseline():
  
  results = defaultdict(lambda:defaultdict(tuple))
  
  (P_10_baseline, Recall_baseline, MAP_baseline, Recip_rank_baseline) = getBaselineResults()

  (P_10_qn_gc, Recall_qn_gc, MAP_qn_gc, Recip_rank_qn_gc) = getQnGc()
  (P_10_qn_gf, Recall_qn_gf, MAP_qn_gf, Recip_rank_qn_gf) = getQnGf()
  (P_10_qs_gc, Recall_qs_gc, MAP_qs_gc, Recip_rank_qs_gc) = getQsGc()
  (P_10_qs_gf, Recall_qs_gf, MAP_qs_gf, Recip_rank_qs_gf) = getQsGf()
  (P_10_qs_gf2, Recall_qs_gf2, MAP_qs_gf2, Recip_rank_qs_gf2) = getQsGf2()
  (P_10_supervised, Recall_supervised, MAP_supervised, Recip_rank_supervised) = getSupervised()
  
  results['p_10']['qn_gc'] = pairedTtest(P_10_baseline, P_10_qn_gc)
  results['p_10']['qn_gf'] = pairedTtest(P_10_baseline, P_10_qn_gf)
  results['p_10']['qs_gc'] = pairedTtest(P_10_baseline, P_10_qs_gc)
  results['p_10']['qs_gf'] = pairedTtest(P_10_baseline, P_10_qs_gf)
  results['p_10']['qs_gf2'] = pairedTtest(P_10_baseline, P_10_qs_gf2)
  results['p_10']['supervised'] = pairedTtest(P_10_baseline, P_10_supervised)
  
  results['recall']['qn_gc'] = pairedTtest(Recall_baseline, Recall_qn_gc)
  results['recall']['qn_gf'] = pairedTtest(Recall_baseline, Recall_qn_gf)
  results['recall']['qs_gc'] = pairedTtest(Recall_baseline, Recall_qs_gc)
  results['recall']['qs_gf'] = pairedTtest(Recall_baseline, Recall_qs_gf)
  results['recall']['qs_gf2'] = pairedTtest(Recall_baseline, Recall_qs_gf2)
  results['recall']['supervised'] = pairedTtest(Recall_baseline, Recall_supervised)
  
  
  results['map']['qn_gc'] = pairedTtest(MAP_baseline, MAP_qn_gc)
  results['map']['qn_gf'] = pairedTtest(MAP_baseline, MAP_qn_gf)
  results['map']['qs_gc'] = pairedTtest(MAP_baseline, MAP_qs_gc)
  results['map']['qs_gf'] = pairedTtest(MAP_baseline, MAP_qs_gf)
  results['map']['qs_gf2'] = pairedTtest(MAP_baseline, MAP_qs_gf2)
  results['map']['supervised'] = pairedTtest(MAP_baseline, MAP_supervised)
  
  results['rr']['qn_gc'] = pairedTtest(Recip_rank_baseline, Recip_rank_qn_gc)
  results['rr']['qn_gf'] = pairedTtest(Recip_rank_baseline, Recip_rank_qn_gf)
  results['rr']['qs_gc'] = pairedTtest(Recip_rank_baseline, Recip_rank_qs_gc)
  results['rr']['qs_gf'] = pairedTtest(Recip_rank_baseline, Recip_rank_qs_gf)
  results['rr']['qs_gf2'] = pairedTtest(Recip_rank_baseline, Recip_rank_qs_gf2)
  results['rr']['supervised'] = pairedTtest(Recip_rank_baseline, Recip_rank_supervised)
  
  return results
  

def printResults(results):
  
  print "results as (t,p):"
  for metric in results:
    print "metric: %s" % metric
    for exp in results[metric]:
      print "exp: %s\t %s" % (exp, results[metric][exp])
      

def run():
  
  results =  compareWithBaseline()
  printResults(results)
  
if __name__ == '__main__':

  run()
