import os
import re
from collections import defaultdict


# represents a document
class Doc(object):

   def __init__(self,content, fieldValues=defaultdict(list)) :
     self.fieldContents = fieldValues
     self.mainContent = content




class DocReader(object):

  startDoc = '<DOC>'
  endDoc = '</DOC>';

  fieldList = ['HEADLINE', 'BYLINE',  'SOURCE', 'FLAG', 'SECTION']


  def __init__(self, listOfFileNames):

    self.listOfFileNames = list(reversed(listOfFileNames))
    self.currentOpenFile = None
    self.currentOpenFileName = None
    self.docCounter = 0
    self.fileCounter = 0

  # this is for processing the SOURCE, HEADLINE etc. fields
  # when we know we are at the start of a document
  def processField(self, docFile, line, fieldName):
    fieldValue = []

    #print fieldName

    while True:

      
      
      oldLine = line  
      line = re.sub('<.*?>|(\\n)', '', line)
      line = line.split(' ')
      fieldValue.extend(line);
      
      if '</'+fieldName+'>' in oldLine:
        return fieldValue
        
      line = docFile.readline();

  # give the current file, process a document:
  # create a Doc object
  def processDoc(self, docFile) :

    fieldValues = defaultdict(list)
    contentWords =  []

    while True:
      line = docFile.readline();

      if line.startswith(DocReader.endDoc):
        return Doc(contentWords, fieldValues)
        break;
      for fieldName in DocReader.fieldList:
        if line.startswith('<'+fieldName+'>'):
          fieldValue = self.processField(docFile, line, fieldName)
          fieldValues[fieldName] = fieldValue
      line = re.sub('<.*?>|(\\n)', '', line)
      line = line.split(' ')
      contentWords.extend(line);

  
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
        #print "Processing doc nr. %d from %s" % (self.counter, os.path.basename(self.currentOpenFileName))
        thisDoc = self.processDoc(self.currentOpenFile)
        self.docCounter += 1
        return thisDoc


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

def run() :
  docFileNames  = getFileNames("/run/media/root/ss-ntfs/3.Documents/huiswerk_20132014/CS&P/project/data1/docs")

  dr = DocReader(docFileNames)

  d =  dr.getNextDocFromFiles()

  while d != None:
    d =  dr.getNextDocFromFiles()
    #print d.mainContent
    print getDictString(d.fieldContents)


if __name__ == '__main__': #if this file is the argument to python
  run()
