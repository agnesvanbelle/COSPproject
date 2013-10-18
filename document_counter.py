from collections import defaultdict
import threading
import time
import multiprocessing
import sys

import docreader
import utilities

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
            self.doc_representations[doc_id][word][w] +=1 # d_i -> q_j -> count
            
          occurrence_id = len(self.q_word_instances[w][word])
          for w in q_context:            
            self.q_word_instances[w][word][occurrence_id]+=1    # w_i -> q_j -> k -> count      
          
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
    nrDocs = 50
    docList = self.getSomeDocs(nrDocs)
    contextWordDictsList = []
    
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
      (contextWordsToQueries, docRepresentations) = t.get_representations()
      print "contextWordsToQueries len: %d" % len(contextWordsToQueries)
      print "docrepr. len: %s" % len(docRepresentations)
      #print "\nqwordinstances: %s" % utilities.getDictString(contextWordsToQueries)
      #print "\ndocrepr: %s" % utilities.getDictString(docRepresentations)
      contextWordDictsList.append(contextWordsToQueries)

    contextWordDict = self.mergeContextWordDicts(contextWordDictsList)
    print "contextWordDict len: %d " % len(contextWordDict)
    
    print contextWordDict['year']['world']
    print contextWordDict['year']['franc']
    
  def mergeContextWordDicts(self, listDicts):
    smallestLen = sys.maxint
    smallest = -1
    smallestDict = None
    
    for i in range(0, len(listDicts)):
      d = listDicts[i]
      l = len(d)
      if l > 0 and l < smallestLen:
        smallesLen = l
        smallest = i
    
    smallestDict = listDicts[smallest]
    listDicts.pop(smallest)
    
    # TODO: houd avg. bij voor variantie enz.
    newDict = defaultdict(lambda : defaultdict(lambda : defaultdict(int)))
    for wi, qj_k_count in smallestDict.iteritems():
      newDict[wi] = smallestDict[wi]
      for o in range(0, len(listDicts)):
        otherDict = listDicts[o]
        #print "otherDict: %s " % otherDict
        #qj_k_count_otherDict = otherDict[wi]
        for queryWord, occurrence_id_dict in otherDict[wi].iteritems():
          for occurrence_id, value in occurrence_id_dict.iteritems():
            
            start_new_occ = len(newDict[wi][queryWord])
            """
            #if value > 0 and wi == 'polic':
            if True:
              print "queryWord: %s" % queryWord
              print "newDict[wi][queryWord]: %s" % newDict[wi][queryWord]              
              print "start_new_occ: %d" % start_new_occ
              print "occurrence_id otherDict: %s"  % occurrence_id
              #print "otherDict[wi][queryWord]: %s " % otherDict[wi][queryWord]
            """
            newDict[wi][queryWord][start_new_occ] += value
          
        
    
    return newDict
    
#169 478 docs
def run() :
  docFileNames  = utilities.getFileNames("Data_dummy/collection")
  
  pp = docreader.Preprocessor("stopwords.txt")
  dr = docreader.DocReader(docFileNames , pp)
  
  
  queries = docreader.readQueries("Data_dummy/original_topics.txt")
  queryWords = docreader.queriesToTermList(queries)
  
  print queryWords
  
  

  dcm = DocCounterManager(dr, queryWords)
  dcm.getCounts()
  
if __name__ == '__main__': #if this file is the argument to python
  run()
