#!/usr/bin/python

"""

AudioBrowse

Qt application for browsing audiobooks

author: Maxime Cogney

"""

import sys
import math
import random
import json
from PyQt4.QtGui import *
from PyQt4.QtCore import *

class ABMain(QMainWindow):

    def __init__(self, *args):
        QMainWindow.__init__(self, *args)

        exit_action = QAction(QIcon('exit.png'), '&Exit', self)
        exit_action.setShortcut('Ctrl+Q')
        exit_action.triggered.connect(qApp.quit)

        file_menu = self.menuBar().addMenu('&File')
        file_menu.addAction(exit_action)

        view_menu = self.menuBar().addMenu('&View')
        search_menu = self.menuBar().addMenu('&Search')
        option_menu = self.menuBar().addMenu('&Option')
        help_menu = self.menuBar().addMenu('&Help')
        
        table = ABTable(mystruct, self)
        self.setCentralWidget(table)
        table.show()

        self.setWindowTitle("AudioBrowse")
        self.resize(500,500)


class ABTable(QTableWidget):

    # Horizontal header labels
    labels=('Title','Link')

    def __init__(self, thestruct, *args):
        QTableWidget.__init__(self, *args)

        self.initUI()

    # UI Setup
    def initUI()

        # Setting up headers
        self.setColumnCount(len(self.labels))
        self.setHorizontalHeaderLabels(self.labels)
        self.horizontalHeader().setStretchLastSection(True)
        self.setColumnWidth(0,300)
        self.verticalHeader().setVisible(False)

        # Setting up selection/edition behavior
        self.setSelectionBehavior(QAbstractItemView.SelectRows)
        self.setSelectionMode(QAbstractItemView.NoSelection)
        self.setEditTriggers(QAbstractItemView.NoEditTriggers)

        # Load items
        jitems=json.loads(open('adbl.data').read())

        for jitem in jitems:
            self.addEntry(jitem)

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

        # Creating new row
        new_size = self.rowCount()
        self.insertRow(new_size)
        self.setItem(new_size,0,title)
        self.setItem(new_size,0,href)

def main():
    
    app = QApplication(sys.argv)
    main = ABMain()
    main.show()
    sys.exit(app.exec_())

if __name__ == '__main__':
    main()
