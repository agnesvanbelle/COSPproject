import random
import math
from collections import defaultdict
import utilities
import threading
import time
import multiprocessing
import sys

'''
Class that manages the clustering process using different threads.
Each thread handles the clustering process for one or more queries
'''
class SenseClusterManager(object):
  
  def __init__(self, queryTerms, queryVectorDict, contextWords, k_values, variancePerTerm):
    
    self.queryTerms = queryTerms
    self.queryVectorDict = queryVectorDict
    self.contextWords = contextWords
    self.variancePerTerm = variancePerTerm
    self.k_values = k_values
    
    self.finalDict = {}
    
  def cluster(self):
    
    self.nrProcessors = multiprocessing.cpu_count()
    nrTerms = len(self.queryTerms)
    
    self.nrThreads  = min(self.nrProcessors, nrTerms)
    self.threads = [None]*self.nrThreads
    
    
    start = 0
    interval = nrTerms / self.nrThreads
    end = start + interval

    print "Start clustering. Using %d threads." % self.nrThreads
    
    for i in range(0, self.nrThreads) :
      if (i == (self.nrThreads-1)):
        end = nrTerms

      termSubset = self.queryTerms[start:end+1]
      queryDictSubset = {}
      for q in termSubset:
        queryDictSubset[q] = self.queryVectorDict[q]
        
      print "start:%d, end:%d, query term subset: %s " % (start, end, termSubset)
      
    
      self.threads[i] = SenseClustering( termSubset , queryDictSubset, self.k_values, self.contextWords, self.variancePerTerm)

      start = end + 1
      end = end + interval 

    for t in self.threads:
      t.start()

    for t in self.threads:
      t.join()

    print "Done clustering."

    for t in self.threads:
      
      result = t.getResultPerQuery()
      
      
      for q in result:
        self.finalDict[q] = result[q]
  
  
  def getResult(self):
    return self.finalDict
  
'''
This class clusters the occurrences of one query term such that the centroids of those (= word senses) can be determined.
'''
class SenseClustering(threading.Thread):


  '''
  queries = list of queries which are a list of query terms
  word_instances_per_query = dictionary of the form q_j -> {q_jk -> {w_i -> freq}} containing all occurences of a query word
  list_context_words = list of the used context words
  list_of_k = list of different values of k for which you wish to do k-means clustering
  variancePerTerm = parameter stating the type of variance you wish to use (seperate per query term or not)
  '''
  def __init__(self, queries, word_instances_per_query, list_of_k,  list_context_words, variancePerTerm):
    
    threading.Thread.__init__(self)
    
    self.queries = queries
    self.word_instances_per_query = word_instances_per_query
    
    self.list_context_words = list_context_words
    
    self.list_of_k = list_of_k
    
    self.variancePerTerm = variancePerTerm
    
    self.resultPerQuery = {}
    
  
  '''
  Manages the clustering for one query term by running buckshot clustering 
  for each term if there is a sufficient amount of occurrences.
  '''
  def run(self):    
    
    # For each query term
    for q in self.queries:
      self.word_inst = self.word_instances_per_query[q]
      self.nr_instances = len(self.word_inst)
      
      # Get the context words
      if self.variancePerTerm:
        self.con_words = self.list_context_words[q]
      else:
        self.con_words = self.list_context_words
      
      # If there are sufficient instances of a query term
      if self.nr_instances > max(self.list_of_k):
        # Run buckshot clustering
        self.resultPerQuery[q] = self.buckshot_clustering(self.list_of_k) # 'bla'
      else:
        # Assume a single word sense
        single_cluster = defaultdict(list)
        for inst in self.word_inst:
          single_cluster[0].append(inst)
        self.resultPerQuery[q] = self.get_centroids(single_cluster)
     
  def getResultPerQuery(self):
    return self.resultPerQuery
      
  '''
  Implements buckshot clustering for one query term.
  Runs k-means for different values of k and returnes best
  clustering based on cluster validation index.
  list_of_k= list of values of k that the user would like to consider
  '''  
  def buckshot_clustering(self, list_of_k):
    # Get the random sample for hierarchical clustering
    sample_size = int( math.sqrt(self.nr_instances))+1
    clusters_init = {}
    occurrences = self.word_inst.keys()    
    
    for i in range(sample_size):
      index = random.randrange(len(occurrences))
      clusters_init[i] = [occurrences[index]]
      del occurrences[index]

    del occurrences
    # Use hierarchical clustering to get the seeds for k-means
    seeds = self.hierarchical_clustering_for_seeds(clusters_init, list_of_k)

    # Do k-means clustering for each k using the aquired seeds
    clusters = {}
    for k in list_of_k:
      if k in seeds:
        clusters[k] = self.k_means_defined_startpoints(seeds[k])
        
    best_v = float("inf")
    best_k = -1
    # Find best cluster
    for k in list_of_k:
      if k in clusters:
        (assignment, centroids) = clusters[k]
        validation_score = self.calc_validation_index(assignment, centroids)
        if validation_score<best_v:
          best_v = validation_score
          best_k = k
    
    if best_k != -1:
      return clusters[best_k][1]
    else:
      single_cluster = defaultdict(list)
      for inst in self.word_inst:
        single_cluster[0].append(inst)
      return self.get_centroids(single_cluster)
  
  '''
  Calculate the validation index of a cluster
  '''
  def calc_validation_index(self, assignment, centroids):
    # calculate sum of differences between centroids and cluster members
    total_wc_distance = 0
    for cluster in assignment:
      for occurrence in assignment[cluster]:
        total_wc_distance += self.eucl_distance(centroids[cluster], self.word_inst[occurrence])

    # calculate sum of differences between cluster centroids
    # and determine minimum distance between cluster centroids
    min_dist = float('inf')
    total_bc_distance = 0
    cluster_ids = centroids.keys()
    c = len(cluster_ids)
    for i in range(c):
      for j in range(i+1, c):
        d  = self.eucl_distance(centroids[cluster_ids[i]], centroids[cluster_ids[j]])
        total_bc_distance += d
        if d< min_dist:
          min_dist = d

    factor = 1.0
    if c != 1:
      factor = factor/(c*(c-1))
    # calculate validation index
    return (total_wc_distance + factor * total_bc_distance) / (min_dist + (1.0 / c))

  '''
  Perform hierarchical clustering on a set of instances
  '''
  def hierarchical_clustering_for_seeds(self, clusters, list_of_k):    
    
    distances = self.calc_all_eucl_distances(clusters)
    current_nr_clusters = len(clusters)
    min_nr_clusters = min(list_of_k)
    cluster_id = len(clusters)
    centroids = {}
    
    # while you still need fewer clusters (with respect to list_of_k)
    while current_nr_clusters>=min_nr_clusters:
      current_pair = None
      current_dist = float("inf")
      cluster_keys = clusters.keys()      
      
      # For each combination of clusters
      for i in range(len(clusters)):
        for j in range(i+1, len(clusters)):          
          
          # Calculate cluster distance
          c1 = cluster_keys[i]
          c2 = cluster_keys[j]
          dist = self.calc_cluster_distance(clusters[c1]+clusters[c2], distances)
          
          # Evaluate if this distance is smaller than current smallest
          if dist < current_dist:
            current_dist = dist
            current_pair = (c1,c2)
      
      # cluster two closest clusters
      clusters[cluster_id] = clusters[current_pair[0]]+clusters[current_pair[1]]
      del clusters[current_pair[0]]
      del clusters[current_pair[1]]

      current_nr_clusters -= 1
      cluster_id += 1

      # If now one of the desired number of clusters is achieved
      if current_nr_clusters in list_of_k:
        # save the centroids of the clusters
        centroids[current_nr_clusters] = self.get_centroids(clusters)

    return centroids
  
  '''
  Prints clusters in a readable way
  '''
  def print_clusters(self, clusters):
    for c in clusters:
      l = clusters[c]
      print(c),
      for i in range(len(l)):
        print(l[i]),
      print('\n'),

  '''
  Calculates centroids for a given set of clusters
  '''  
  def get_centroids(self, clusters):
    centroids = {}
    for c in clusters:
      centroid = defaultdict(float)
      nr_inst = float(len(clusters[c]))
      for j in clusters[c]:
        for w in self.con_words:
          f = 0
          if w in self.word_inst[j]:
            f = self.word_inst[j][w]
          centroid[w] += f/nr_inst
      centroids[c] = centroid
    return centroids

  '''
  Performs k-means clustering with pre defined initial centroids
  centroids: initial centroids
  '''
  def k_means_defined_startpoints(self, centroids):
    converged = False
    old_assignment = {}
    assignment = defaultdict(list)
    for c in centroids:
      old_assignment[c] = []
    change = False
    max_iterations = 1000
    nr_iterations = 0

    while not converged:
      nr_iterations+=1
      # For each instance find the closest centroid and assign
      for occ in self.word_inst.keys():
        min_dist = float("inf")
        best_c = -1
        for c in centroids:
          centr = centroids[c]
          dist = self.eucl_distance(centr, self.word_inst[occ])
          if dist<min_dist:
            min_dist = dist
            best_c = c

        # Assign occurance to closest centroid
        assignment[best_c].append(occ)
        # Record if the assignment of occurances changed
        change = occ not in old_assignment[best_c]


      centroids = self.get_centroids(assignment)
      old_assignment = assignment
      assignment = defaultdict(list)

      # Check if k-means has converged
      converge = (not change) or (nr_iterations >= max_iterations)
      change = False

      return(old_assignment, centroids)

  '''
  Calculates euclidean distance between all instances
  '''
  def calc_all_eucl_distances(self, instance_ids):
    distances = defaultdict(lambda : defaultdict(int))
    for ind_i in range(len(instance_ids)):
      for ind_j in range(ind_i+1, len(instance_ids)):
        i = instance_ids[ind_i][0]
        j = instance_ids[ind_j][0]
        # calc eucl_distance
        dist = self.eucl_distance(self.word_inst[i],self.word_inst[j])
        distances[i][j] = dist
        distances[j][i] = dist
    return distances

  '''
  Calculates the euclidean distance between two instances
  '''
  def eucl_distance(self, instance_i, instance_j):
    dist = 0
    for w in self.con_words:
      f1 = 0
      f2 = 0
      if w in instance_i:
        f1 = instance_i[w]
      if w in instance_j:
        f2 = instance_j[w]
      dist += math.pow(f1-f2, 2)
    dist = math.sqrt(float(dist))

    return dist
  
  '''
  Calculates average cluster distance
  '''
  def calc_cluster_distance(self, c, distances):
    factor = float(1)/ ( (math.pow(len(c),2)- len(c))/2 )
    dist = 0
    for i in range(len(c)):
      for j in range(i+1, len(c)):
        dist += distances[c[i]][c[j]]
    return dist * factor

