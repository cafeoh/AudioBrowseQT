#!/usr/bin/python

"""

AudioBrowse

Qt application for browsing audiobooks

author: Maxime Cogney

"""

import sys
import json
import time
import requests
from PyQt4.QtGui import *
from PyQt4.QtCore import *
from ADBLParser import *

class ABFeed(QThread):

    def __init__(self):
        QThread.__init__(self)

        self.urls=[]
        self.quitting = False
        self.parser = ADBLParser()

    def __del__(self):
        self.quitting = True
        self.wait()

    def addUrl(self,url):
        self.urls.append(url)

    def run(self):
        for url in self.urls:
            if(self.quitting):
                break
            self.feedUrl(url)

    def feedUrl(self,url):
        data = requests.get(url).text
        self.parser.feed(data)

        for item in self.parser.res:
            item=self.cacheImage(item)
            self.emit(SIGNAL('feed(PyQt_PyObject)'), item)
        self.parser.reset()

    def cacheImage(self,item):
        if 'img' not in item:
            return item

        url=item['img'] 
        filename=url.split('/')[-1]
        filelocation='img_cache/'+filename
        req=requests.get(url, stream=True)

        if req.status_code == 200:
            with open(filelocation,'wb') as f:
                for ch in req.iter_content(1024):
                    f.write(ch)
        else:
            print 'Bad requests ({})'.format(req.status_code)
            return item

        item['img']=filelocation
        return item



class ABMain(QMainWindow):

    def __init__(self, *args):
        QMainWindow.__init__(self, *args)

        self.initUI()

        # Setting up our worker to scrape the first 10 pages of new Audible releases
        self.feed = ABFeed()
        for x in range(10):
            self.feed.addUrl(page_url.format(x+1))
        self.connect(self.feed, SIGNAL('feed(PyQt_PyObject)'), self.table.addEntry)
        self.feed.start()

    def initUI(self):
        self.setWindowTitle("AudioBrowse")
        self.resize(800,600)

        # File menu
        exit_action = QAction('&Exit', self)
        exit_action.setShortcut('Ctrl+Q')
        exit_action.triggered.connect(qApp.quit)
        file_menu = self.menuBar().addMenu('&File')
        file_menu.addAction(exit_action)

        # Option menu
        switch_url_action = QAction('Hide &links', self)
        switch_url_action.setShortcut('Ctrl+L')
        switch_url_action.setCheckable(True)
        switch_url_action.triggered.connect(self.switchUrl)
        option_menu = self.menuBar().addMenu('&Option')
        option_menu.addAction(switch_url_action)
        
        # Main table
        self.table = ABTable(self)
        self.setCentralWidget(self.table)
        self.table.show()

    def switchUrl(self):
        if self.sender().isChecked():
            self.table.hideColumn(1)
        else:
            self.table.showColumn(1)
            self.table.setColumnWidth(0,self.table.columnWidth(0)-200)

class ABTable(QTableWidget):

    # Horizontal header labels
    labels=('Title','Link')

    def __init__(self, *args):
        QTableWidget.__init__(self, *args)

        self.initUI()

    # UI Setup
    def initUI(self):

        # Setting up headers
        self.setColumnCount(len(self.labels))
        self.setHorizontalHeaderLabels(self.labels)
        self.horizontalHeader().setStretchLastSection(True)
        self.setColumnWidth(0,600)
        self.verticalHeader().setVisible(False)

        # Setting up selection/edition behavior
        self.setSelectionBehavior(QAbstractItemView.SelectRows)
        self.setSelectionMode(QAbstractItemView.NoSelection)
        self.setEditTriggers(QAbstractItemView.NoEditTriggers)

        # Allow sorting
        self.setSortingEnabled(True)

    # Add entry (row) to table from a dictionnary
    def addEntry(self, data):

        # Verify item validity
        if any(x not in data for x in ('title','img','href')):
            print 'Invalid item'
            return

        # Setting up items
        title = QTableWidgetItem(data['title'])
        title.setData(Qt.DecorationRole,QPixmap('img_cache/'+data['img'].split('/')[-1]))
        href = QTableWidgetItem(data['href'])

        # Qt sorts at item insertion, which means we gotta hold auto sort calls until the
        # whole row is filled up if we don't want a mess or overwritten cells.
        self.setSortingEnabled(False)

        # Creating new row
        new_size = self.rowCount()
        self.insertRow(new_size)
        self.setItem(new_size,0,title)
        self.setItem(new_size,1,href)

        # Reenabling sorting
        self.setSortingEnabled(True)

def main():
    
    app = QApplication(sys.argv)
    main = ABMain()
    main.show()
    sys.exit(app.exec_())

if __name__ == '__main__':
    main()
