import random
from collections import defaultdict

class SenseClustering(object):
    
    
    '''
    word instances = dictionary of the form {q_jk -> {w_i -> freq}} containing all occurences of a query word
    list_context_word = list of the used context words
    '''
    def __init__(self, word_instances, list_context_words):
        self.word_inst = word_instances
        self.con_words = list_context_words        
        self.nr_instances = len(word_instances)
        
    def buckshot_clustering(list_of_k):
        # Get the random sample for hierarchical clustering
        sample_size = math.sqrt(self.nr_instances)
        sample = []
        clusters_init = {}
        occurrences = self.word_inst.keys()
        for i in range(sample_size):
            index = random.randrange(len(occurrences))
            clusters_init[i] = [occurrences[index]]
            del occurrences[index]
                
        del occurrences        
        # Use hierarchical clustering to get the seeds for k-means
        seeds = hierarchical_clustering_for_seeds(sample,clusters_init list_of_k)
        
        # Do k-means clustering for each k using the aquired seeds
        
        # Find best cluster
    
    
    def hierarchical_clustering_for_seeds(clusters, list_of_k):
        distances = calc_eucl_distances(clusters)
        current_nr_clusters = len(clusters)
        min_nr_clusters = min(list_of_k)
        max_nr_clusters = max(list_of_k)
        cluster_id = len(clusters)
        centroids = {}
        
        while current_nr_clusters<min_nr_clusters:
            # cluster two closest clusters                      
            current_pair = None
            current_dist = float("inf")
            cluster_keys = clusters.keys()
            for i in range(len(clusters)):
                for j in range(i+1, len(clusters)):
                    # Calculate cluster distance
                        c1 = cluster_keys[i]
                        c2 = cluster_keys[j]
                        dist = calc_cluster_distance(c1+c2, distances)
                    
                    if dist<current_dist:
                        current_dist = dist
                        current_pair = (c1,c2)
            
            clusters[cluster_id] = clusters[current_pair[0]]+clusters[current_pair[1]]
            del clusters[current_pair[0]]
            del clusters[current_pair[1]]
            
            current_nr_clusters -= 1
            cluster_id += 1
            
            # If now one of the desired number of clusters is achieved
            if current_nr_clusters in list_of_k:
                # save the centroids of the clusters
                centroids[current_nr_clusters] = get_centroids(clusters)
                ######################
                
        return centroids
    
    def get_centroids(clusters):
        print 'undefined'
    
    def k_means_defined_startpoints(instances, seeds):
        print 'undefined'
    
    def calc_eucl_distances(instance_ids):
        distances = defaultdict(lambda : defaultdict(int))
        for ind_i in range(len(instance_ids)):
            for ind_j in range(ind_i+1, len(instance_ids)):
                i = instance_ids[ind_i][0]
                j = instance_ids[ind_j][0]
                # calc eucl_distance
                dist = 0
                for w in self.con_words:
                    f1 = 0
                    f2 = 0
                    if w in self.word_inst[i]:
                        f1 = self.word_inst[i][w]
                    if w in self.word_inst[j]:
                        f2 = self.word_inst[j][w]
                    dist += math.pow(f1-f2, 2)    
                dist = mat.sqrt(float(dist))
                distances[i][j] = dist
                distances[j][i] = dist
        return distances
        
    def calc_cluster_distance(c, distances):
        factor = float(1)/ ( (math.pow(len(c),2)- len(c))/2 )
        dist = 0
        for i in range(len(c)):
            for j in range(i+1, len(c)):
                dist += distances[c[i]][c[j]]
        dist = dist * factor
        