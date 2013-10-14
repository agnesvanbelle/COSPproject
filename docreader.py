import os
import re
from collections import defaultdict
import nltk
from nltk.stem import PorterStemmer
#from nltk.stem.snowball import EnglishStemmer as SnowballStemmer

# represents a document
class Doc(object):

   def __init__(self,content, fieldValues=defaultdict(list)) :
     self.fieldContents = fieldValues
     self.mainContent = content


# preprocesses words
class Preprocessor():
  
  def __init__(self):
    self.stopwords = nltk.corpus.stopwords.words('english')
    self.stemmer = PorterStemmer() # works on words
     
  
  # returns a preprocessed word
  def preprocessWord(self, word):
    
    word = re.sub('[^A-Za-z0-9_-]+', '', word)
    
    if (word == ''): # word was only punctuation
      return ''
    
    word = word.lower()
      
    word = self.stemmer.stem(word)          
    
    if  word in self.stopwords:  
      return ''
    
    return word
  
  # returns preprocessed word list
  def preprocessWords(self, line):
    
    line = re.sub('<.*?>|(\\n)', '', line) # remove <></> tags and newline signs
    line = re.sub('[\.,]', ' ',line) # replace commans and dots by a space
    
    
    wordList =  line.split(' ')
    newWordList = []
    for w in wordList:
      newW = self.preprocessWord(w)
      if newW != '':
        newWordList.append(newW)
    return newWordList

# reads in documents one-by-one (see getNextDocFromFiles method)
class DocReader(object):

  startDoc = '<DOC>'
  endDoc = '</DOC>';

  startMain = '<TEXT>'
  endMain = '</TEXT>'
  
  fieldList = ['HEADLINE', 'BYLINE',  'SOURCE', 'FLAG', 'SECTION']


  def __init__(self, listOfFileNames):

    self.listOfFileNames = list(reversed(listOfFileNames))
    self.currentOpenFile = None
    self.currentOpenFileName = None
    self.docCounter = 0
    self.fileCounter = 0
    
    self.preprocessor = Preprocessor()

  # this is for processing the SOURCE, HEADLINE etc. fields
  # when we know we are at the start of a document
  def processField(self, docFile, line, fieldName):
    fieldValue = []

    while True:
      oldLine = line  
      
      if line != '':
        lineList = self.preprocessor.preprocessWords(line)     
        fieldValue.extend(lineList);
      
      if '</'+fieldName+'>' in oldLine:
        return fieldValue
        
      line = docFile.readline();

  # give the current file, process a document:
  # create a Doc object
  def processDoc(self, docFile) :

    fieldValues = defaultdict(list)
    contentWords =  []
    
    main = False
    
    while True:
      line = docFile.readline();

      if line.startswith(DocReader.endDoc):
        return Doc(contentWords, fieldValues)
        break;
      for fieldName in DocReader.fieldList:
        if line.startswith('<'+fieldName+'>'):
          fieldValue = self.processField(docFile, line, fieldName)
          fieldValues[fieldName] = fieldValue
      
      if line.startswith(DocReader.startMain):
        main = True
      elif line.startswith(DocReader.endMain):
        main = False
        
      if main:
        lineList = self.preprocessor.preprocessWords(line) 
        contentWords.extend(lineList);

  
  # get next document from the files, as a 
  # Doc object
  # returns None if the last file is empty
  def getNextDocFromFiles(self) :
    
    if self.currentOpenFile == None:
      if self.listOfFileNames == []:
        return None
      else:
        self.currentOpenFileName = self.listOfFileNames.pop()
        self.currentOpenFile = open(self.currentOpenFileName)
        print "Processing file nr. %d: %s " % (self.fileCounter, os.path.basename(self.currentOpenFileName))
        self.fileCounter += 1

    line = self.currentOpenFile.readline();

    if not line:
        self.currentOpenFile = None
        return self.getNextDocFromFiles()

    if line.startswith(DocReader.startDoc):
        print "Processing doc nr. %d from %s" % (self.docCounter, os.path.basename(self.currentOpenFileName))
        thisDoc = self.processDoc(self.currentOpenFile)
        self.docCounter += 1
        return thisDoc



def Clusterer(Object):
  
  def __init__(self):
    pass
    
  def clusterValidityScore(self):
    pass



def getFileNames(directory) :
  l = os.listdir(directory)
  l2 = []
  for name in l :
    if name[-4:] != ".dtd" and name != "README":
      if os.path.isdir(directory + "/" + name):
        print "%s is dir" % name
        l2.extend(getFileNames(directory + "/" + name + "/"))
      else :
        l2.append( directory + "/" + name)

  return l2

def getDictString(d) :
  s = ""
  if len(d) > 0:
    for k, v in d.iteritems():
      s += "\n\t%s --> %s " % (k, v)
  else:
    s =  "{}"
  return s

# returns variance, given values should be a list
def variance(avg, values, lengthList) :
  if lengthList <= 0:
    return 0
  else:
    return ( sum
                (map(lambda x : math.pow( x - avg, 2), values)) /
                float(lengthList)
            )





def run() :
  docFileNames  = getFileNames("/run/media/root/ss-ntfs/3.Documents/huiswerk_20132014/CS&P/project/data1/docs")

  dr = DocReader(docFileNames)

  d =  'meaningless init value'

  while d != None:
    d =  dr.getNextDocFromFiles()
    #print getDictString(d.fieldContents)
    #print d.mainContentnt


if __name__ == '__main__': #if this file is the argument to python
  run()
