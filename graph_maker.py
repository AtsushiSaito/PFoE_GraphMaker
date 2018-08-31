#!/usr/bin/env python

from PyQt5.QtWidgets import *
from matplotlib.backends.backend_qt5agg import FigureCanvasQTAgg as FigureCanvas
from raspimouse_gamepad_teach_and_replay.msg import *
import matplotlib.pyplot as plt
import numpy as np
import sys, rospy, rosbag, collections, os

class MainWindow(QWidget):
    def __init__(self):
        super(MainWindow, self).__init__()
        self.bag_opened = False
        self.resize(800,400)
        self.setWindowTitle("PFoE Graph Maker")
        self.openButton = QPushButton('Open BagFile')
        self.openButton.clicked.connect(self.choiceBagFile)
        self.SavePNGButton = QPushButton("Save PNG")
        self.SavePNGButton.clicked.connect(self.SavePNG)
        self.SaveEPSButton = QPushButton("Save EPS")
        self.SaveEPSButton.clicked.connect(self.SaveEPS)

        # matplotlib
        self.figure = plt.figure()
        self.canvas = FigureCanvas(self.figure)

        # set the layout
        vbox = QVBoxLayout()
        vbox.addWidget(self.canvas)

        hbox = QHBoxLayout()
        hbox.addWidget(self.openButton)
        hbox.addWidget(self.SaveEPSButton)
        hbox.addWidget(self.SavePNGButton)
        vbox.addLayout(hbox)

        self.setLayout(vbox)
        self.show()

    def choiceBagFile(self):
        fname = QFileDialog.getOpenFileName(self, "Open repaly bagfile", os.path.expanduser('~'))
        self.bagname = fname[0]
        print(self.bagname)
        if self.checkBagfile():
            self.openBagfile()
            self.readBagfile()
            self.draw()

    def SavePNG(self):
        if(self.bag_opened):
            dir_path = QFileDialog.getExistingDirectory(self, 'Save Directory', os.path.expanduser('~') )
            root_ext_pair = os.path.splitext(self.bagname)
            bag_basename = os.path.basename(root_ext_pair[0])
            plt.savefig(dir_path + "/" + bag_basename + ".png")
        else:
            QMessageBox.warning(self, "Message", u"not open bagfile")

    def SaveEPS(self):
        if(self.bag_opened):
            dir_path = QFileDialog.getExistingDirectory(self, 'Save Directory', os.path.expanduser('~') )
            root_ext_pair = os.path.splitext(self.bagname)
            bag_basename = os.path.basename(root_ext_pair[0])
            plt.savefig(dir_path + "/" + bag_basename + ".eps")
        else:
            QMessageBox.warning(self, "Message", u"not open bagfile")

    def draw(self):
        x = np.arange(0, len(self.most_particles),1)
        self.ax = self.figure.add_subplot(111)
        self.ax.scatter(x, self.most_particles, s=30, marker='+')
        self.ax.grid()
        self.canvas.draw()

    def checkBagfile(self):
        if self.bag_opened:
            self.bag.close()
            self.bag_opened = False
            return False
        return True

    def openBagfile(self):
        self.bag = rosbag.Bag(self.bagname)
        print ("-----------------------------------------------")
        print ("current_bag_file: [ %s ]" % self.bagname)
        self.bag_opened = True

    def readBagfile(self):
        self.right_forward = []
        self.right_side = []
        self.left_side = []
        self.left_forward = []
        self.linear_x = []
        self.angular_z = []
        self.paticle_pos = []
        self.eta = []
        self.particles_pos = [[]]
        self.most_particles = []

        for topic, msg, t in self.bag.read_messages(topics=['/pfoe_out']):
            self.right_forward.append(float(msg.right_forward))
            self.right_side.append(float(msg.right_side))
            self.left_side.append(float(msg.left_side))
            self.left_forward.append(float(msg.left_forward))
            self.linear_x.append(msg.linear_x)
            self.angular_z.append(msg.angular_z)
            self.eta.append(msg.eta)
            self.paticle_pos.append(msg.particles_pos)
        for e in self.paticle_pos:
            self.most_particles.append(collections.Counter(e).most_common()[0][0])


if __name__ == '__main__':
    app = QApplication(sys.argv)
    main = MainWindow()
    sys.exit(app.exec_())
