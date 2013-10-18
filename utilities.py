import os
import math

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

