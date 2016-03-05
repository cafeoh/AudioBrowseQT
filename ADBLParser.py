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
        self.reset()

    def reset(self):
        HTMLParser.reset(self)
        self.state = "" # automata
        self.depth = 0  # recursive depth
        self.elem = {}  # temporary item
        self.res = []   # result item list

    def handle_starttag(self, tag, attrs):
        # Looking for result items
        if tag == 'li':
            if ('class','adbl-result-item') in attrs:
                self.elem = {}
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

        if self.state == 'title':
            self.elem['title'] = data.strip()
            self.state = 'item'

    def handle_endtag(self, tag):
        if tag == "li":
            if self.depth > 1:
                self.depth -= 1
            # Finished reading item result
            elif self.depth == 1:
                self.res.append(self.elem)
                self.depth = 0
                self.state = ""

if __name__ == "__main__":
    parser = ADBLParser()
    parser.feed(requests.get(page_url.format(10)).text)
    """
    with open('adbl.data','w') as f:
        f.write(json.dumps(parser.res))
    """
