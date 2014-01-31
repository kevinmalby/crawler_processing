import sqlite3 as lite
import sys
import re

# The class for processing
class ProcessPages:

  # Constructor, sets up all the structures and opens the output file
  def __init__(self):
    self.total_pages = 0
    self.longest_page = 0
    self.longest_url = ''
    self.words = {}
    self.two_grams = {}
    self.subdomains = {}
    self.stop_words = ["a", "about", "above", "after", "again", "against", "all", "am", "an", "and", "any", "are", "aren't", "as", "at", "be", "because", "been", "before", "being", "below", "between", "both", "but", "by", "can't", "cannot", "could", "couldn't", "did", "didn't", "do", "does", "doesn't", "doing", "don't", "down", "during", "each", "few", "for", "from", "further", "had", "hadn't", "has", "hasn't", "have", "haven't", "having", "he", "he'd", "he'll", "he's", "her", "here", "here's", "hers", "herself", "him", "himself", "his", "how", "how's", "i", "i'd", "i'll", "i'm", "i've", "if", "in", "into", "is", "isn't", "it", "it's", "its", "itself", "let's", "me", "more", "most", "mustn't", "my", "myself", "no", "nor", "not", "of", "off", "on", "once", "only", "or", "other", "ought", "our", "ours ", "ourselves", "out", "over", "own", "same", "shan't", "she", "she'd", "she'll", "she's", "should", "shouldn't", "so", "some", "such", "than", "that", "that's", "the", "their", "theirs", "them", "themselves", "then", "there", "there's", "these", "they", "they'd", "they'll", "they're", "they've", "this", "those", "through", "to", "too", "under", "until", "up", "very", "was", "wasn't", "we", "we'd", "we'll", "we're", "we've", "were", "weren't", "what", "what's", "when", "when's", "where", "where's", "which", "while", "who", "who's", "whom", "why", "why's", "with", "won't", "would", "wouldn't", "you", "you'd", "you'll", "you're", "you've", "your", "yours", "yourself", "yourselves"]
    self.file = open('out.txt', 'w')
  
  # Keeps track of the longest page and updates the variable if necessary
  def UpdateLongestPage(self, url, word_count):
    if word_count > self.longest_page:
      self.longest_page = word_count
      self.longest_url = url

  # Just write to the output file the number of words in the
  # longest page and the url of the page
  def GetLongesPageCount(self):
    self.file.write('The longest page contained %d words\n' %(self.longest_page))
    self.file.write('The URL for the page is: %s\n' %(self.longest_url))

  # For each page, this method gets called in order to add the
  # the words from the current page into the words frequency dictionary
  def GenerateWordDict(self, word_list):
    for word in word_list:
      self.words.setdefault(word, 0)
      self.words[word] += 1

  # For each page, this method gets called in order to add the
  # the two grams from the current page into the two grams frequency dictionary
  def GenerateTwoGramDict(self, word_list):
    for i in range(len(word_list) - 1):
      tg = ' '.join(word_list[i:i+2])
      self.two_grams.setdefault(tg,0)
      self.two_grams[tg] += 1

  # For each subdomain, this method adds the subdomain to the
  # subdomain dictionary and records the number of pages in that subdomain
  def GenerateSubdomainDict(self, subdomain):
    if 'www.' in subdomain:
      subdomain = subdomain.replace('www.', '')
    subdomain = subdomain + '.uci.edu'
    self.subdomains.setdefault(subdomain, 0)
    self.subdomains[subdomain] += 1

  # This method gets called for every page and updates all of the
  # values of interest accordingly, i.e. words dict, two grams dict,
  # longest page.
  def ProcessPage(self, url, subdomain, page_text):
    word_list = re.sub("[^\w']", " ", page_text).lower().split()
    self.UpdateLongestPage(url, len(word_list))
    for stop in self.stop_words:
      word_list[:] = [x for x in word_list if x != stop]

    self.total_pages += 1

    self.GenerateSubdomainDict(subdomain)
    self.GenerateWordDict(word_list)
    self.GenerateTwoGramDict(word_list)

  # Writes the list of unique subdomains in alphabetical order
  # to the Subdomains.txt file
  def GetSubdomains(self):
    subs = open('Subdomains.txt', 'w')
    sorted_subs = sorted(self.subdomains.items())
    subs.write("Subdomains in Alphabetical Order\n\n")
    for ssub in sorted_subs:
      subs.write('%s: %d\n' %(ssub[0], ssub[1]))
    subs.close()
    
  # Sorts the words dictionary and writes the top 500 words and
  # their frequencies to the output file
  def GetTopFiveHundredWords(self):
    sorted_words = sorted(self.words.iteritems(), key=lambda x:-x[1])[:500]
    self.file.write("Top Five-Hundred Words\n\n")
    for sword in sorted_words:
      self.file.write('%s: %d\n' %(sword[0], sword[1]))

  # Sorts the two grams dictionary and writes the top 20 two grams and
  # their frequencies to the output file
  def GetTopTwentyTwoGrams(self):
    sorted_grams = sorted(self.two_grams.iteritems(), key=lambda x:-x[1])[:20]
    self.file.write("Top Twenty Two-Grams\n\n")
    for sgram in sorted_grams:
      self.file.write('%s: %d\n' %(sgram[0], sgram[1]))

  # Gets the total number of pages by looking at entries in table
  def GetTotalPages(self):
    self.file.write('There were %d unique pages in the domain\n' %(self.total_pages))

  # Creates a line to separate the different answers to questions
  def CreateSeparator(self, end):
    self.file.write('*****************************************************************************************************\n')
    if end == True:
      self.file.write('\n')

def main():

  # Initializes the ProcessPages object
  processor = ProcessPages()

  # Connects to the database, command line argument specifies db location
  conn = lite.connect(sys.argv[1])

  # Selects all of the entries in the database and stores them in the
  # rows variable. This is then iterated through, with each row being
  # processed by the ProcessPage method
  with conn:
    cur = conn.cursor()
    cur.execute("SELECT * FROM Pages")

    rows = cur.fetchall()

    for row in rows:
      processor.ProcessPage(row[1],row[2], row[3])

  # Write all of the necessary information to the output file
  processor.CreateSeparator(False)
  processor.GetTotalPages()
  processor.CreateSeparator(True)
  processor.CreateSeparator(False)
  processor.GetTopFiveHundredWords()
  processor.CreateSeparator(True)
  processor.CreateSeparator(False)
  processor.GetLongesPageCount()
  processor.CreateSeparator(True)
  processor.CreateSeparator(False)
  processor.GetTopTwentyTwoGrams()
  processor.CreateSeparator(True)

  processor.GetSubdomains()

  # Close the output file
  processor.file.close()

if __name__ == "__main__":
    main()
