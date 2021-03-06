
import os
import codecs
import sys
import simplenlp
import pickle

from csc_utils.batch import queryset_foreach
from conceptnet.models import Sentence, Assertion, RawAssertion
from multiprocessing import Process, JoinableQueue

"""
This script is used to pull the conceptnet4 data into a set of flat 
files.  This way it can be read through quicker when creating 
the conceptnet5 edges with the conceptnet4 data.
"""

class FlatFileWriter():
  def __init__(self):
      self.base_filename = "raw_data/conceptnet4_flat_"
      self.num_threads = 10
    
      self.queue = JoinableQueue()

  def start(self):
      print "begin writing flat files"
      processes = self.create_processes()
      self.add_lines_to_queue()
      self.queue.join()
      print "finished writing flat files"

  def add_lines_to_queue(self):
      raw_assertions = RawAssertion.objects.filter()
      for raw_assertion in raw_assertions:
          self.queue.put(raw_assertion)

  def pull_data(self,q,output):
      while 1:
          raw_assertion = q.get()
          self.handle_raw_assertion(raw_assertion,output)
          q.task_done()

  def handle_raw_assertion(self,raw_assertion,output):
      lang = unicode(raw_assertion.language_id)
      creator = unicode(raw_assertion.creator.username)
      frame_id = int(raw_assertion.frame_id)
      startText = unicode(raw_assertion.text1)
      endText = unicode(raw_assertion.text2)


      activity = unicode(raw_assertion.sentence.activity.name)
      relname = unicode(raw_assertion.frame.relation.name)
      polarity = float(raw_assertion.frame.frequency.value)
      goodness = float(raw_assertion.frame.goodness)
      frame_text = unicode(raw_assertion.frame.text)
      cnet4_id = int(raw_assertion.id)
      votes = list(raw_assertion.votes.all())

      
      line = []

      line.append("<assertion>")

      line.append("<lang>")
      line.append(lang)
      line.append("</lang>")

      line.append("<creator>")
      line.append(creator)
      line.append("</creator>")

      line.append("<frame_id>")
      line.append(str(frame_id))
      line.append("</frame_id>")

      line.append("<startText>")
      line.append(startText)
      line.append("</startText>")

      line.append("<endText>")
      line.append(endText)
      line.append("</endText>")

      line.append("<activity>")
      line.append(activity)
      line.append("</activity>")

      line.append("<relname>")
      line.append(relname)
      line.append("</relname>")

      line.append("<polarity>")
      line.append(str(polarity))
      line.append("</polarity>")

      line.append("<goodness>")
      line.append(str(goodness))
      line.append("</goodness>")

      line.append("<frame_text>")
      line.append(frame_text)
      line.append("</frame_text>")

      line.append("<cnet4_id>")
      line.append(str(cnet4_id))
      line.append("</cnet4_id>")

      line.append("<votes>")
      for vote in votes:
          line.append("<vote>")
          line.append(unicode(vote))
          line.append("</vote>")

      line.append("</votes>")

      line.append("</assertion>")
      line.append('\n')

      output.write("".join(line).encode('utf8'))
      
     


  def create_processes(self):
      processes = []
      for i in range(self.num_threads):
          flat_file = open(self.base_filename + str(i)+ ".txt",'w')
          p = Process(target = self.pull_data, args = (self.queue, flat_file))
          p.daemon=True
          p.start()
          processes.append(p)
      return processes


if __name__ == '__main__':

    if "--build_flat_files" in sys.argv:
        quickWriter = FlatFileWriter()
        quickWriter.start()

