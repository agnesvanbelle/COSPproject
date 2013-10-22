from collections import defaultdict

def write_similarities_to_CSV(file_name, senses_dict, doc_vectors, queries, context_words, raw_queries):
  # Denk dat ik hier ook nog de raw queries nodig heb om als query key te gebruiken.
  similarities = calc_similarities(senses_dict, doc_vectors, queries, context_words, raw_queries)
  
  write_to_csv(similarities, file_name)
  
def calc_similarities(senses_dict, doc_vectors, queries, context_words, raw_queries):
  similarities = defaultdict(dict)
  for i in range(len(queries)):
    query = queries[i]
    raw_query = raw_queries[i]
    for doc, vector in doc_vectors.items():
      # calc_similarity hier invoegen!!
      sim = 0.0
      similarities[raw_query][doc] = sim
  
  return similarities
  
def write_to_csv(similarities, file_name):
  f = open(file_name, 'w')
  # Wat kan ik hier gebruiken dat ook in JAVA zit?  
  # Klopt doc id zo????
  for query in similarities:
    for doc, sim in similarities.items():
      line = query + ', ' + doc + ', ' + str(sim) + '\n'
      f.write(line)

  f.close()
 
