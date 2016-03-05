#!/usr/bin/python

from HTMLParser import HTMLParser
import requests
import json

base_url="http://audible.com"
new_url=base_url+"/newreleases"
page_url=new_url+"?page={}"

class ADBLParser(HTMLParser):

    def __init__(self, *args):
        HTMLParser.__init__(self, *args)

        self.state = "" # automata
        self.depth = 0  # recursive depth
        self.elem = {}  # temporary item
        self.meta = []
        self.res = []   # result item list

    def handle_starttag(self, tag, attrs):
        # Looking for result items
        if tag == 'li':
            if ('class','adbl-result-item') in attrs:
                self.elem = {}
                self.meta = []
                self.state = 'item'
            if self.state == 'item':
                self.depth += 1

        # Currently inside a result item
        elif self.state == 'item':
            # Found a thumbnail
            if tag == 'img' and ('class','adbl-prod-image') in attrs:
                for name, value in attrs:
                    if name == 'src':
                        self.elem['img'] = value
                        break
            # Found title div (for title and href)
            elif tag == 'div' and ('class','adbl-prod-title') in attrs:
                self.state = 'href'
            elif tag == 'div' and ('class','adbl-prod-meta') in attrs:
                self.state = 'meta'
        
        # Currently inside meta block
        elif self.state == 'meta':
            pass
            """
            if tag == 'a' and ('class','adbl-link'):
                if 'author' in self.elem:
                    print "catching narrator"
                    self.state = 'narrator'
                else:
                    print "catching author"
                    self.state == 'author'
            """

        # Currently inside title div
        elif self.state == 'href':
            # Found link
            if tag == 'a' and ('class','adbl-link') in attrs:
                self.state = 'title'
                for name, value in attrs:
                    if name == 'href':
                        self.elem['href'] = base_url+value
                        break

    def handle_data(self, data):
        # meta info
        if self.state == 'meta':
            d=data.strip()
            self.meta.append(d)


        if self.state == 'title':
            self.elem['title'] = data.strip()
            self.state = 'item'

        """
        if self.state: print self.state
        if self.state in ('author','narrator','length','date'):
            print "[REC DATA]",data.strip()
            self.elem[self.state] = data.strip()
            self.state = 'meta'

        # title info
        elif self.state == 'title':
            self.elem[self.state] = data.strip()
            self.state = 'item'

        if self.state == 'meta':
            if data.strip() == 'Length:':
                print 'found length'
                self.state = 'length'
            elif data.strip() == 'Release Date:':
                print 'found date'
                self.state = 'date'


        elif self.state == 'author':
            self.elem['author'] = data.strip()
            self.state = 'meta'
        elif self.state == 'narrator':
            self.elem['narrator'] = data.strip()
            self.state = 'meta'
        elif self.state == 'length':
            self.elem['length'] = data.strip()
            self.state = 'meta'
        elif self.state == 'date':
            self.elem['date'] = data.strip()
            self.state = 'meta'
        """



    def handle_endtag(self, tag):
        if tag == "li":
            if self.depth > 1:
                self.depth -= 1
            # Finished reading item result
            elif self.depth == 1:
                self.res.append(self.elem)
                print self.meta
                self.depth = 0
                self.state = ""

if __name__ == "__main__":
    parser = ADBLParser()
    parser.feed(requests.get(page_url.format(10)).text)
    print parser.res
    with open('adbl.data','w') as f:
        f.write(json.dumps(parser.res))
        """
        f.write(e['title']+'\n')
        f.write(e['href']+'\n')
        f.write(e['img']+'\n')
        f.write('\n')
        """

