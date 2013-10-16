import random

class SenseClustering(object):
    
        
    def __init__(self, word_instances, random):
        self.word_inst = word_instances
        self.nr_instances = len(word_instances)
        
        
    def buckshot_clustering(list_of_k):
        # Get the random sample for hierarchical clustering
        sample_size = math.sqrt(self.nr_instances)
        sample = []
        occurrences = self.word_inst.keys()
        for i in range(sample_size):
            index = random.randrange(len(occurrences))
            sample.append(occurrences[index])
            del occurrences[index]
                
        # Use hierarchical clustering to get the seeds for k-means
        seeds = hierarchical_clustering_for_seeds()
        
        # Do k-means clustering for each k using the aquired seeds
        
        # Find best cluster
    
    
    def hierarchical_clustering_for_seeds(instances, list_of_k):
    
    
    def k_means_defined_startpoints(instances, seeds):