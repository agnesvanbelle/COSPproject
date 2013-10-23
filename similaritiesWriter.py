from collections import defaultdict
import math
import copy
def write_similarities_to_CSV(file_name, senses_dict, doc_vectors, queries, context_words, raw_queries):
  # Denk dat ik hier ook nog de raw queries nodig heb om als query key te gebruiken.
  similarities = calc_similarities(senses_dict, doc_vectors, queries, context_words, raw_queries)
    
  write_to_csv(similarities, file_name)
  
def calc_similarities(senses_dict, doc_vectors, queries, context_words, raw_queries):
  similarities = defaultdict(dict)
  for i in range(len(queries)):
    query = queries[i]
    raw_query = raw_queries[i]
    sim = get_similarity(doc_vectors, senses_dict, query, context_words)
    similarities[raw_query] = sim
  
  return similarities
  
def write_to_csv(similarities, file_name):
  f = open(file_name, 'w')
  for query, terms in similarities.items():
    for term, docs in terms.items():
      for doc, sim in docs.items():
        line = query.lower() + ', ' + term + ', ' + str(doc) + ', ' + str(sim) + '\n'
        f.write(line)

  f.close()
 
def get_similarity(doc_vectors, senses_dict, query, context_words):
    # Get distribution over senses for the query terms
    query_term_dist = query_term_distance_distribution(senses_dict, query, context_words)
    # Get distribution over senses for the documents for each of the query terms
    doc_term_dist = doc_term_distance_distribution(doc_vectors, senses_dict, query, context_words)
    # Get similarities between distributions
    return calc_distribution_similarities(query_term_dist, doc_term_dist, query)

def eucl_distance(context, instance_i, instance_j):
    dist = 0
    for w in context:
      f1 = 0
      f2 = 0
      if w in instance_i:
        f1 = instance_i[w]
      if w in instance_j:
        f2 = instance_j[w]
      dist += math.pow(f1-f2, 2)
    dist = math.sqrt(float(dist))

    return dist
    
def calc_distribution_similarities(query_term_dist, doc_term_dist, query):
  # distr_similarities term->doc->similarity
  distr_similarities = defaultdict(dict)
  for q in query:
    for doc, d in doc_term_dist.items():      
      # print 'similarity for', doc, q
      if q in d:        
        distr_similarities[q][doc] = bhattacharyya_coeff(d[q], query_term_dist[q])
  
  return distr_similarities

def bhattacharyya_coeff(distribution_1, distribution_2):
  bhat_coeff = 0
  # print 'distribution doc: ', distribution_1
  # print 'distribution query: ', distribution_2
  for sense, value_1 in distribution_1.items():
    value_2 = distribution_2[sense]
    bhat_coeff += math.sqrt( value_1 * value_2 )  
  # print 'distance:', bhat_dist
  return bhat_coeff

def doc_term_distance_distribution(doc_vectors, senses_dict, query, context_words):
  
  distributions = defaultdict(dict)
  # For each document
  for doc, q_terms in doc_vectors.items():    
    #For each query term
    for q in query:
      # If term in document
      if q in q_terms:
        #Determine distribution over senses
        distributions[doc][q] = get_distribution(senses_dict[q], doc_vectors[doc][q], context_words)      
  # Return result
  return distributions
    
def query_term_distance_distribution(senses_dict, query, context_words):
  distributions = {}
  # For each query term
  for i in range(len(query)):
    term = query[i]
    # initialize context for query term
    context_list_q = copy.deepcopy(query)
    del context_list_q[i]
    context_q = defaultdict(int)
    for w in context_list_q:
      context_q[w] += 1
    # Calculate distribution  
    senses = senses_dict[term]    
    distributions[term] = get_distribution(senses, context_q, context_words)
  # return result  
  return distributions
    
def get_distribution(senses, item, context_words):
  item_sense_dist = {}
  total_dist = 0
  # Get distance from item to each sense
  for sense, vector in senses.items():
    dist = eucl_distance(context_words, item, vector)
    item_sense_dist[sense] = dist
    total_dist+=dist
  # Normalize distances  
  for sense in senses.keys():
    if total_dist != 0:
      item_sense_dist[sense] /= total_dist 
    else :
      item_sense_dist[sense] = 1
  # Return distribution
  return item_sense_dist
