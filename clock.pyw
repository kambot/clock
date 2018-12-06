from time import strftime, sleep, time, mktime
from datetime import datetime
from calendar import monthrange

import sys, os
from PyQt5.QtWidgets import *
from PyQt5.QtGui import QKeyEvent, QPainter,QImage, QPen, QIcon, QPixmap, QColor, QBrush, QCursor, QFont, QPalette
from PyQt5.QtCore import Qt, QPoint, QPointF, QSize, QEvent, QTimer, QCoreApplication


class Clock(QMainWindow):

    def __init__(self):
        super().__init__()
        self.initUI()

    def initUI(self):

        self.pid = os.getpid()
   
        self.root = os.path.dirname(os.path.abspath(__file__))  + "\\"
        
        self.main_icon = QIcon(self.root + r"clock.png")
        self.setWindowIcon(self.main_icon)
        self.setWindowTitle("Clock")
        # self.setWindowOpacity(.5)

        self.setFont(QFont('Arial', 10))
        QToolTip.setFont(QFont('Arial', 8))

        self.tooltip = True
        self.gray_circles = True
        self.tray_app = False
        self.in_tray = False
        self.was_tray = False
        self.colors = [Qt.white, Qt.black, Qt.gray, Qt.darkGray, Qt.lightGray, Qt.red, Qt.darkRed, Qt.green, Qt.darkGreen, Qt.blue, Qt.darkBlue, Qt.cyan, Qt.darkCyan, Qt.magenta, Qt.darkMagenta, Qt.yellow, Qt.darkYellow]
        self.color0_ind = self.colors.index(Qt.black)
        self.color1_ind = self.colors.index(Qt.gray)
        self.dim = 0
        self.m_prior = "0"
        self.diy = 0
        self.Y_prior = "0"

        # self.colors = []
        # for i in range(256):
        #     for ii in range(256):
        #         for iii in range(256):
        #             self.colors.append((i,ii,iii))
        
        self.sih = 60*60
        self.sid = self.sih*24

        self.circles = 6

        # default window size and heights
        self.w = 300
        self.h = 300
        self.w_def = self.w * 1
        self.h_def = self.h * 1
        self.pad = 10

        self.reduce_ws = [.98,.94,.96,.97,.99,.99]
        self.p_ws_def = [3,5,7,9,11,13]
        self.p_ws = [x for x in self.p_ws_def]

        self.r_w_def = (self.w - max(self.p_ws) - self.pad)/(self.circles*2)
        self.r_h_def = (self.h - max(self.p_ws) - self.pad)/(self.circles*2)
        self.r_ws = [self.r_w_def * x for x in range(1,self.circles+1)]
        self.r_hs = [self.r_h_def * x for x in range(1,self.circles+1)]
        self.midx = self.r_w_def * self.circles + max(self.p_ws)/2 + self.pad/2
        self.midy = self.r_h_def * self.circles + max(self.p_ws)/2 + self.pad/2

        self.update_times()
        
        self.widget = QWidget()
        # self.circle_area = QWidget()
        # self.grid = QGridLayout()
        # self.grid.setSpacing(0)
        # self.grid.setHorizontalSpacing(0)
        # self.grid.setVerticalSpacing(0)
        # # self.grid.addWidget(self.circle_area,0,0)
        # self.widget.setLayout(self.grid)
        self.setCentralWidget(self.widget)

        self.setGeometry(300, 300, self.w, self.h)
        self.center()

        self.timer = QTimer()
        self.timer.timeout.connect(self.updater)
        self.timer.start(50)

        self.installEventFilter(self)

        self.def_bg_color = self.widget.palette().color(QPalette.Background)
        self.colors.append(self.def_bg_color)
        self.color2_ind = self.colors.index(self.def_bg_color)



    def paintEvent(self, event):
        if self.in_tray:
            return

        # cumulative seconds
        self.cum_seconds = 0
        percents = []
        start_angle = -270

        # percent through a second
        percents.append(int(self.MS)/1000000)
        self.cum_seconds += int(self.MS)/1000000
    
        # percent through a minute
        self.cum_seconds += int(self.S)
        percents.append((self.cum_seconds)/60) # / number of seconds in a minute

        # percent through an hour
        self.cum_seconds += int(self.M)*60
        percents.append((self.cum_seconds)/(self.sih)) # / number of seconds in an hour

        # percent through a day
        self.cum_seconds += int(self.H)*60*60
        percents.append((self.cum_seconds)/(self.sid)) # / number of seconds in a day

        # percent through a month
        self.cum_seconds += int(self.d)*60*60*24
        percents.append((self.cum_seconds)/(self.sid*self.dim)) # / number of seconds in the current month

        # percent through a year
        percents.append((float(self.ts) - self.ts_boy)/(self.ts_eoy - self.ts_boy)) # / number of seconds in this year

        pformats = []
        for p in percents:
            pformats.append(str(int(p*10000)/100))
        
        if self.tooltip:
            tooltip = []
            for i in range(self.circles):
                tooltip.append(self.time_names[i] + ": " + str(self.times[i]) + " - " + pformats[i] + "%")
            self.widget.setToolTip("\n".join(tooltip))
        else:
            self.widget.setToolTip("")


        painter = QPainter(self)
        painter.eraseRect(0,0,self.w,self.h)
        # input()
        painter.setRenderHint(QPainter.Antialiasing,True)

        def draw_arc(ind):
            pen = QPen()
            pen.setWidth(self.p_ws[ind])

            if self.gray_circles:
                # pen.setColor(Qt.gray)
                pw = self.p_ws[ind] * self.reduce_ws[ind]
                pen.setWidth(pw)
                pen.setColor(self.colors[self.color1_ind])
                painter.setPen(pen)
                # painter.drawArc(self.midx-self.r_ws[ind], self.midy-self.r_hs[ind], self.r_ws[ind]*2, self.r_hs[ind]*2, start_angle*16,-360*16)
                # painter.drawArc(self.midx-self.r_ws[ind], self.midy-self.r_hs[ind], self.r_ws[ind]*2, self.r_hs[ind]*2, start_angle*16 + percents[ind]*-360*16 - pw/self.r_ws[ind]*.5*3.14/180*16, (1-percents[ind])*-360*16 +  pw/self.r_ws[ind]*.5*3.14/180*16)
                painter.drawArc(self.midx-self.r_ws[ind], self.midy-self.r_hs[ind], self.r_ws[ind]*2, self.r_hs[ind]*2, start_angle*16 + percents[ind]*-360*16, (1-percents[ind])*-360*16)

            pen.setWidth(self.p_ws[ind])
            pen.setColor(self.colors[self.color0_ind])
            painter.setPen(pen)
            painter.drawArc(self.midx-self.r_ws[ind], self.midy-self.r_hs[ind], self.r_ws[ind]*2, self.r_hs[ind]*2, start_angle*16, percents[ind]*-360*16)

        for i in range(self.circles):
            draw_arc(i)



       

    def update_times(self):
        self.ts = str(time())
        self.date = strftime("%Y-%m-%d")
        self.time = strftime("%H:%M:%S")
        self.H = self.time.split(":")[0]
        self.M = self.time.split(":")[1]
        self.S = self.time.split(":")[2]
        self.MS = datetime.now().strftime("%f")#strftime("%f")
        self.Y = strftime("%Y")
        self.m = strftime("%m")
        self.d = strftime("%d")
        self.times = [self.MS,self.S,self.M,self.H,self.d,self.m]
        self.time_names = ["milliseconds","seconds","minutes","hours","day","month"]

        if self.m != self.m_prior or self.dim == 0:
            self.dim = monthrange(int(self.Y), int(self.m))[1]
        self.m_prior = self.m + ""
        
        # if self.Y != self.Y_prior or self.diy == 0:
        #     self.diy = 0
        #     for m in range(1,12+1):
        #         self.diy += monthrange(int(self.Y), m)[1]
        #     # print(self.diy)
        # self.Y_prior = self.Y + ""

        if self.Y != self.Y_prior:
            self.ts_boy = mktime(datetime.strptime(self.Y + ".01.01.00.00:00","%Y.%m.%d.%H.%M:%S").timetuple())
            self.ts_eoy = mktime(datetime.strptime(self.Y + ".12.31.23.59:59","%Y.%m.%d.%H.%M:%S").timetuple())

            
    def updater(self):
        self.update_times()
        self.repaint()

    def to_tray(self):

        self.in_tray = True
        
        self.hide()
        menu = QMenu()

        settingAction = menu.addAction("Show Window")
        settingAction.triggered.connect(self.show_window)

        exitAction = menu.addAction("Exit")
        exitAction.triggered.connect(self.custom_close)

        self.tray = QSystemTrayIcon()
        self.tray.setIcon(self.main_icon)
        self.tray.setContextMenu(menu)
        self.tray.show()
        self.was_tray = True


    def resizeEvent(self, event):
        qr = self.geometry()
        self.w = qr.width()
        self.h = qr.height()

        self.w_scale = self.w / self.w_def
        self.h_scale = self.h / self.h_def

        if self.w_scale < 1 or self.h_scale < 1:
            scale = min(self.w_scale,self.h_scale)
            self.p_ws = [scale * x for x in self.p_ws_def]
        else:
            scale = min(self.w_scale,self.h_scale,20)
            self.p_ws = [scale * x for x in self.p_ws_def]

        self.r_w = (self.w - max(self.p_ws) - self.pad)/(self.circles*2)
        self.r_h = (self.h - max(self.p_ws) - self.pad)/(self.circles*2)

        self.r_ws = [self.r_w * x for x in range(1,self.circles+1)]
        self.r_hs = [self.r_h * x for x in range(1,self.circles+1)]
        self.midx = self.r_w * self.circles + max(self.p_ws)/2 + self.pad/2
        self.midy = self.r_h * self.circles + max(self.p_ws)/2 + self.pad/2

        # print(self.w,self.h)
        # print(self.w_scale,self.h_scale)
        # print(self.r_w,self.r_h)
        # print(self.midx,self.midy)
        # print("-"*20)


    def center(self):
        qr = self.frameGeometry()
        cp = QDesktopWidget().availableGeometry().center()
        qr.moveCenter(cp)
        self.move(qr.topLeft())


    def show_window(self):
        self.show()
        self.in_tray = False
        self.tray.hide()
    
    def custom_close(self):
        try:
            self.tray.hide()
        except:
            pass
        QCoreApplication.instance().quit()

    def eventFilter(self,source,event):

        if event.type() == QEvent.KeyPress:
            modifiers = QApplication.keyboardModifiers()
            if modifiers == Qt.ControlModifier and event.key() == Qt.Key_C:
                self.custom_close()
            if modifiers == Qt.ControlModifier and event.key() == Qt.Key_Q:
                self.custom_close()
            if event.key() == Qt.Key_Escape:
                self.custom_close()
            
            if event.key() == Qt.Key_Right:
                self.color0_ind += 1
                if self.color0_ind >= len(self.colors):
                    self.color0_ind = 0
            elif event.key() == Qt.Key_Left:
                self.color0_ind += -1
                if self.color0_ind < 0:
                    self.color0_ind = len(self.colors)-1

            if event.key() == Qt.Key_Up:
                if self.gray_circles:
                    self.color1_ind += 1
                    if self.color1_ind >= len(self.colors):
                        self.color1_ind = 0
            elif event.key() == Qt.Key_Down:
                if self.gray_circles:
                    self.color1_ind += -1
                    if self.color1_ind < 0:
                        self.color1_ind = len(self.colors)-1

            if event.key() == Qt.Key_Plus:
                self.color2_ind += 1
                if self.color2_ind >= len(self.colors):
                    self.color2_ind = 0
                p = self.palette()
                p.setColor(self.backgroundRole(), self.colors[self.color2_ind])
                self.setPalette(p)
            if event.key() == Qt.Key_Minus:
                self.color2_ind += -1
                if self.color2_ind < 0:
                    self.color2_ind = len(self.colors)-1
                p = self.palette()
                p.setColor(self.backgroundRole(), self.colors[self.color2_ind])
                self.setPalette(p)


        if event.type() == QEvent.ContextMenu:
            menu = QMenu()
            ex = menu.addAction('Exit')
            sq = menu.addAction('Square Window')
            tc = menu.addAction('Inner Circles')
            ttp = menu.addAction('Toggle Tooltip')
            co = menu.addAction('Default Colors')
            action = menu.exec_(event.globalPos())

            if action == tc:
                self.gray_circles = not self.gray_circles

            elif action == ttp:
                self.tooltip = not self.tooltip

            elif action == sq:
                m = min(self.w,self.h)
                self.resize(m,m)
            
            elif action == co:
                self.color0_ind = self.colors.index(Qt.black)
                self.color1_ind = self.colors.index(Qt.gray)

            elif action == ex:
                self.custom_close()

        return 0

    def closeEvent(self, event):

        if self.tray_app:
            self.to_tray()
            event.ignore()
        else:
            self.custom_close()


            
if __name__ == '__main__':

    import ctypes
    ctypes.windll.shell32.SetCurrentProcessExplicitAppUserModelID("clock_gui_ctypes_thing")

    app = QApplication(sys.argv)
    QApplication.setQuitOnLastWindowClosed(False)
    gui = Clock()
    gui.tray_app = True
    # gui.build_menu()
    gui.show()
    app.exec_()

