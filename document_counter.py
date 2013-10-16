from collections import defaultdict

class DocCounter(object):
    
    def __init__(self, documents, query_words, document_window_size, dsm_window_size):    
  
        self.documents = documents
        self.q_words = query_words
        self.d_window = document_window_size
        self.q_window = dsm_window_size        
        self.q_word_instances = defaultdict(lambda : defaultdict(lambda : defaultdict(int)))
        self.doc_representations = defaultdict(lambda : defaultdict(lambda : defaultdict(int)))
        

    def get_representations(self):
        doc_id = 0
        for doc in self.documents:
            content = doc.mainContent
            d_length = len(content)
            for i in range(d_length):
                word = content[i]
                # If a query word is encountered
                if word in self.q_words:
                    # Process context 
                    print i
                    d_context = content[max(0, i-self.d_window):i] + content[i+1: min(i+1+self.d_window, d_length+1)]
                    print d_context
                    q_context = content[max(0, i-self.q_window):i] + content[i+1: min(i+1+self.q_window, d_length+1)]
                    print q_context
                    for w in d_context:
                        # !!!!!!!!!!!!!!!!!!!!!!!!!!!
                        # IK HEB GEEN DOCUMENT ID!!!!                        
                        self.doc_representations[doc_id][word][w] +=1
                        
                    occurrence_id = len(q_word_instances[w][word])
                    for w in q_context:                        
                        self.q_word_instances[w][word][occurrence_id]+=1
                    
            doc_id+=1        
        return (self.q_word_instances, self.doc_representations)