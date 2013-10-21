import random
import math
from collections import defaultdict
import utilities

class SenseClustering(object):


  '''
  word instances = dictionary of the form {q_jk -> {w_i -> freq}} containing all occurences of a query word
  list_context_word = list of the used context words
  '''
  def __init__(self, word_instances, list_context_words):
    self.word_inst = word_instances
    self.con_words = list_context_words
    self.nr_instances = len(word_instances)

  def buckshot_clustering(self, list_of_k):
    # Get the random sample for hierarchical clustering
    sample_size = int( math.sqrt(self.nr_instances))
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
    print "list_of_k: %s" % list_of_k
    for k in list_of_k:
      if k in seeds:
        clusters[k] = self.k_means_defined_startpoints(seeds[k])
      else:
        print "Removing k=%d b/c of initialization fail" % k
        list_of_k.remove(k) # sorry you no play
        
    best_v = float("inf")
    best_k = -1
    # Find best cluster
    for k in list_of_k:
      (assignment, centroids) = clusters[k]
      print assignment
      print
      validation_score = self.calc_validation_index(assignment, centroids)
      if validation_score<best_v:
        best_v = validation_score
        best_k = k
      print validation_score, k
      print

    print 'best k value: %d' %best_k
    #print clusters[best_k][0]
    #print utilities.getDictString(clusters[best_k][1])
    return clusters[best_k][1]

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

  # TODO add something so it still works in there's only 1 vector
  def hierarchical_clustering_for_seeds(self, clusters, list_of_k):
    distances = self.calc_all_eucl_distances(clusters)
    current_nr_clusters = len(clusters)
    min_nr_clusters = min(list_of_k)
    cluster_id = len(clusters)
    centroids = {}

    while current_nr_clusters>=min_nr_clusters:
      self.print_clusters(clusters)
      print
      current_pair = None
      current_dist = float("inf")
      cluster_keys = clusters.keys()
      for i in range(len(clusters)):
        for j in range(i+1, len(clusters)):
          # Calculate cluster distance
          c1 = cluster_keys[i]
          c2 = cluster_keys[j]
          dist = self.calc_cluster_distance(clusters[c1]+clusters[c2], distances)
          if dist<current_dist:
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

  def print_clusters(self, clusters):
    for c in clusters:
      l = clusters[c]
      print(c),
      for i in range(len(l)):
        print(l[i]),
      print('\n'),

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

  def calc_cluster_distance(self, c, distances):
    factor = float(1)/ ( (math.pow(len(c),2)- len(c))/2 )
    dist = 0
    for i in range(len(c)):
      for j in range(i+1, len(c)):
        dist += distances[c[i]][c[j]]
    return dist * factor

