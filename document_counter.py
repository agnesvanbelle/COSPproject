from collections import defaultdict
import threading
import time
import multiprocessing


import docreader

class DocCounter(threading.Thread):
  
  docCount = 0
  
  def __init__(self, documents, query_words, document_window_size=10, dsm_window_size=10):  
    
    threading.Thread.__init__(self)
    
    self.documents = documents
    self.q_words = query_words
    self.d_window = document_window_size
    self.q_window = dsm_window_size    
    self.q_word_instances = defaultdict(lambda : defaultdict(lambda : defaultdict(int)))
    self.doc_representations = defaultdict(lambda : defaultdict(lambda : defaultdict(int)))
    
  def run(self):
    self.make_representations()

  def make_representations(self):
    
    for doc in self.documents:
      content = doc.mainContent
      doc_id = doc.ID
      d_length = len(content)
      for i in range(d_length):
        word = content[i]
        # If a query word is encountered
        if word in self.q_words:
          # Process context 
          #print "word: %s" % word
          d_context = content[max(0, i-self.d_window):i] + content[i+1: min(i+1+self.d_window, d_length+1)]
          #print "d_context: %s" % d_context
          q_context = content[max(0, i-self.q_window):i] + content[i+1: min(i+1+self.q_window, d_length+1)]
          #print "q_context: %s " % q_context
          for w in d_context:        
            self.doc_representations[doc_id][word][w] +=1
            
          occurrence_id = len(self.q_word_instances[w][word])
          for w in q_context:            
            self.q_word_instances[w][word][occurrence_id]+=1          
          
      DocCounter.docCount += 1
      if DocCounter.docCount % 1000 == 0:
        print "%d docs  processed." % (DocCounter.docCount + 1)
        
  def get_representations(self):
    return (self.q_word_instances, self.doc_representations)
    
    
class DocCounterManager(object):
  
  def __init__(self, docReader, queryWords):
    self.nrProcessors = multiprocessing.cpu_count()   
    self.threads = [None]*self.nrProcessors
    self.docReader = docReader
    self.queryWords = queryWords
  
   
  def getSomeDocs(self, number = 10) :    
    d =  'meaningless init value'
    docList = []
    while d != None and number > 0:
      d =  self.docReader.getNextDocFromFiles()
      number -= 1
      #print getDictString(d.fieldContents)
      #print d.mainContentnt
      #print d.ID
      docList.append(d)
    print "docReader.docCounter: %d" % self.docReader.docCounter
    return docList
  
  def getCounts(self):
    nrDocs = 10
    docList = self.getSomeDocs(nrDocs)
    
    start = 0
    interval = nrDocs / self.nrProcessors
    end = start + interval    
    
    for i in range(0, self.nrProcessors) :
      if (i == (self.nrProcessors-1)):
        end = nrDocs
    
      docsSubset = docList[start:end]
      print "start: %d, end: %d" % (start,end)
      
      self.threads[i] = DocCounter( docsSubset, self.queryWords)    
            
      start = end + 1
      end = end + interval

    for t in self.threads:
        t.start()
        
    for t in self.threads:
      t.join()
      
    print "Done preprocessing."
    
    for t in self.threads:
      (qWordInstances, docRepresentations) = t.get_representations()
      print "qwordinstances len: %d" % len(qWordInstances)
      print "docrepr. len: %s" % len(docRepresentations)
      

#169 478 docs
def run() :
  docFileNames  = docreader.getFileNames("/run/media/root/ss-ntfs/3.Documents/huiswerk_20132014/CS&P/project/data1/docs")
  
  pp = docreader.Preprocessor("stopwords.txt")
  dr = docreader.DocReader(docFileNames , pp)
  
  
  queries = docreader.readQueries("/run/media/root/ss-ntfs/3.Documents/huiswerk_20132014/CS&P/project/data1/original_topics.txt")
  queryWords = docreader.queriesToTermList(queries)
  
  print queryWords
  
  

  dcm = DocCounterManager(dr, queryWords)
  dcm.getCounts()
  
if __name__ == '__main__': #if this file is the argument to python
  run()
