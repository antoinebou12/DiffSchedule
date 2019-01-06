import os
import sys
from calendar import day_name
from datetime import date, datetime, timedelta
import numpy as np
import tempfile
import pickle

import PyQt5
from PyQt5.QtWidgets import QMainWindow, qApp, QApplication, QWidget, QDialog, QDesktopWidget, \
                            QFileDialog, QLabel, QPushButton, QTextEdit, QScrollArea, QLineEdit, QRadioButton,  \
                            QVBoxLayout, QHBoxLayout, QGridLayout, QGroupBox, QSizePolicy, \
                            QUndoStack, QUndoCommand,\
                            QMenu, QAction, \
                            QComboBox, QFormLayout, QDialogButtonBox

from PyQt5.QtGui import QIcon, QPixmap, QFont, QKeySequence
from PyQt5.QtCore import Qt, QEvent, QRect

import qdarkstyle

from base import WeekSpace, DAY_IN_WEEK
from formats import ImportFile, ExportFile


class MainGUI(QMainWindow):
    def __init__(self, parent=None):
        super(MainGUI, self).__init__(parent)

        self.parent = parent

        self.screen_size = QDesktopWidget().screenGeometry(-1)
        self.window_size = (self.screen_size.width(), self.screen_size.height())

        self.menu_bar = self.menuBar()

        # Edit File
        self.fileMenu = None

        self.saveAct = None
        self.openAct = None

        # Recent sub menu
        self.recentMenu = None

        self.compareAct = None

        # Import sub menu
        self.importMenu = None

        self.importAct = None
        self.import_csvAct = None

        #  Export sub menu
        self.exportMenu = None
        self.exportAct = None
        self.export_csvAct = None

        self.exitAct = None

        # Edit Menu
        self.editMenu = None

        self.undoAct = None
        self.redoAct = None
        self.clearAct = None

        # ViewMenu
        self.viewMenu = None

        self.timelabelAct = None
        self.daylabelAct = None
        self.fullscrenAct = None

        # Theme Menu
        self.styleMenu = None

        self.dark_styleAct = None
        self.white_styleAct = None

        # Theme
        self._style = "Dark"
        self.setStyleSheet(qdarkstyle.load_stylesheet_pyqt5())

        # Save
        self._save_week_list = []
        self._num_save = 0

        # Undo framework
        self.undoStack = QUndoStack()

        # Main grid
        self.grid = None

        self.initUI()

    def initMenuBar(self):

        # saveAct = QAction(QIcon('save.png'), '&Save', self)
        self.saveAct = QAction('&Save', self)
        self.saveAct.setShortcut('Ctrl+S')
        self.saveAct.setStatusTip('Save the grid')
        self.saveAct.triggered.connect(self.save)

        # openAct = QAction(QIcon('open.png'), '&Open', self)
        self.openAct = QAction('&Open', self)
        self.openAct.setShortcut('Ctrl+O')
        self.openAct.setStatusTip('Open file')
        self.openAct.triggered.connect(self.open)

        # self.importMenu = QAction(QIcon('recent.png'), '&Open Recent', self)
        self.recentMenu = QMenu('&Open Recent', self)

        # compareAct = QAction(QIcon('compare.png'), '&Compare', self)
        self.compareAct = QAction('&Compare', self)
        self.compareAct.setShortcut('Ctrl+B')
        self.compareAct.setStatusTip('Compare two grid')
        self.compareAct.triggered.connect(self.compare)

        self.importMenu = QMenu('&Import', self)
        self.importMenu.setStatusTip('Import file')

        # self.importAct = QAction(QIcon('import.png'), '&Import', self)
        self.importAct = QAction('&Import', self)
        self.importAct.setShortcut('Ctrl+I')
        self.importAct.setStatusTip('Import file')

        # self.import_csvAct = QAction(QIcon('import.png'), '&csv', self)
        self.import_csvAct = QAction('&csv', self)
        self.import_csvAct.setStatusTip('Import csv')

        # self.exportMenu = QAction(QIcon('csv.png'), '&Exit', self)
        self.exportMenu = QMenu('&Export', self)
        self.exportMenu.setStatusTip('Export file')

        # self.exportAct = QAction(QIcon('import.png'), '&Export', self)
        self.exportAct = QAction('&Export', self)
        self.exportAct.setShortcut('Ctrl+E')
        self.importAct.setStatusTip('Import file')

        # self.import_csvAct = QAction(QIcon('csv.png'), '&csv', self)
        self.export_csvAct = QAction('&csv', self)
        self.export_csvAct.setStatusTip('Import csv')
        self.export_csvAct.triggered.connect(self.export_csv)

        # exitAct = QAction(QIcon('exit.png'), '&Exit', self)
        self.exitAct = QAction('&Exit', self)
        self.exitAct.setShortcut('Ctrl+Q')
        self.exitAct.setStatusTip('Exit application')
        self.exitAct.triggered.connect(qApp.quit)

        # self.undoAct = QAction(QIcon("icons/undo.png"),"Undo last action",self)
        self.undoAct = QAction('&Undo', self)
        self.undoAct.setStatusTip("Undo last action")
        self.undoAct.setShortcut("Ctrl+Z")
        self.undoAct.triggered.connect(self.undo)

        # self.redoAct = QtWidgets.QAction(QtGui.QIcon("icons/redo.png"),"Redo last undone thing",self)
        self.redoAct = QAction('&Redo', self)
        self.redoAct.setStatusTip("Redo last undone thing")
        self.redoAct.setShortcut("Ctrl+Y")
        self.redoAct.triggered.connect(self.redo)

        # self.clearAct = QAction(QIcon('clear.png'), '&Exit', self)
        self.clearAct = QAction('&Clear', self)
        self.clearAct.setShortcut('Ctrl+D')
        self.clearAct.setStatusTip('Clear calender')
        self.clearAct.triggered.connect(self.clear)

        # self.daylabelAct = QAction(QIcon('daylabel.png'), '&Toggle day Label', self)
        self.daylabelAct = QAction('&Toggle Day Label', self)
        self.daylabelAct.setCheckable(True)
        self.daylabelAct.setChecked(True)
        self.daylabelAct.setShortcut('Ctrl+G')
        self.daylabelAct.setStatusTip('View the day label')
        self.daylabelAct.triggered[bool].connect(self.daylabel)

        # self.timelabelAct = QAction(QIcon('timelabel.png'), '&Toggle Time Label', self)
        self.timelabelAct = QAction('&Toggle Time Label', self)
        self.timelabelAct.setCheckable(True)
        self.timelabelAct.setChecked(False)
        self.timelabelAct.setShortcut('Ctrl+T')
        self.timelabelAct.setStatusTip('View the time label')
        self.timelabelAct.triggered[bool].connect(self.timelabel)

        # self.fullscreenAct = QAction(QIcon('fullscreen.png'), '&FullScreen', self)
        self.fullscreenAct = QAction('&Fullscreen', self)
        self.fullscreenAct.setCheckable(True)
        self.fullscreenAct.setShortcut('F11')
        self.fullscreenAct.setStatusTip('Fullscreen')
        self.fullscreenAct.triggered.connect(self.fullscreen)

        # self.styleMenu = QAction(QIcon('theme.png'), '&Theme', self)
        self.styleMenu = QMenu('&Theme', self)

        # self.dark_styleAct = QAction(QIcon('darktheme.png'), '&Dark', self)
        self.dark_styleAct = QAction('&Dark ', self)
        self.dark_styleAct.setStatusTip('Dark')
        self.dark_styleAct.triggered.connect(self.dark_mode)

        # self.white_styleAct = QAction(QIcon('whitetheme.png'), '&White', self)
        self.white_styleAct = QAction('&White ', self)
        self.white_styleAct.setStatusTip('White theme')
        self.white_styleAct.triggered.connect(self.white_mode)

    def save(self):
        save = SaveCommand('save%s' % self._num_save, self.grid.week, self._num_save)
        new_file, filename = tempfile.mkstemp()
        outfile = open(filename, 'wb')
        serial = pickle.dump(self.grid.week, outfile)

        self.tmp_filename = filename

        saveAct = QAction(save.nickname, self)
        saveAct.triggered.connect(self.open_recent)
        self.recentMenu.addAction(saveAct)
        self._save_week_list.append(save)
        self._num_save = self._num_save + 1

    def open(self):
        filename = QFileDialog.getOpenFileName(self, 'Open File', ".", "(*.writer)")[0]

        if filename:
            with open(self.filename, "rt") as file:
                pass

    def open_recent(self):
        week = pickle.load(open(self.tmp_filename, 'rb'))
        self.grid.week = week

    def compare(self):
        cmp_dialog = CompareDialog(parent=self)

    def clear(self):
        clear_week = ClearCommand(grid=self.grid)
        self.undoStack.push(clear_week)

    def import_csv(self):
        ImportFile(self.grid.week, 'FreeTime.csv').csv()

    def export_csv(self):
        ExportFile(self.grid.week, 'FreeTime.csv').csv()

    def undo(self):
        self.undoStack.undo()

    def redo(self):
        self.undoStack.redo()

    def daylabel(self, state):
        if state:
            self.grid.grid_date.visibility_day = True
        else:
            self.grid.grid_date.visibility_day = False

    def timelabel(self, state):
        if state:
            self.grid.grid_date.visibility_time = True
        else:
            self.grid.grid_date.visibility_time = False

    def fullscreen(self):
        if self.isFullScreen():
            self.showNormal()
        else:
            self.showFullScreen()

    def dark_mode(self):
        self.setStyleSheet(qdarkstyle.load_stylesheet_pyqt5())
        self._style = "Dark"
        self.grid.grid_date.update_theme()

    def white_mode(self):
        self.setStyleSheet("")
        self._style = "White"
        self.grid.grid_date.update_theme()

    def initToolbar(self):

        self.fileMenu = self.menu_bar.addMenu('&File')
        self.fileMenu.addAction(self.openAct)
        self.fileMenu.addMenu(self.recentMenu)
        self.fileMenu.addAction(self.saveAct)
        self.fileMenu.addAction(self.compareAct)

        self.fileMenu.addSeparator()

        self.fileMenu.addMenu(self.importMenu)
        self.importMenu.addAction(self.import_csvAct)
        self.fileMenu.addMenu(self.exportMenu)
        self.exportMenu.addAction(self.export_csvAct)

        self.fileMenu.addSeparator()

        self.fileMenu.addAction(self.exitAct)

        self.editMenu = self.menu_bar.addMenu('&Edit')
        self.editMenu.addAction(self.undoAct)
        self.editMenu.addAction(self.redoAct)

        self.editMenu.addSeparator()

        self.editMenu.addAction(self.clearAct)

        self.viewMenu = self.menu_bar.addMenu('&View')

        self.viewMenu.addMenu(self.styleMenu)
        self.styleMenu.addAction(self.dark_styleAct)
        self.styleMenu.addAction(self.white_styleAct)

        self.viewMenu.addSeparator()

        self.viewMenu.addAction(self.fullscreenAct)

        self.viewMenu.addSeparator()

        self.viewMenu.addAction(self.daylabelAct)
        self.viewMenu.addAction(self.timelabelAct)

    @property
    def style(self):
        return self._style

    def initUI(self):

        undoAction = self.undoStack.createUndoAction(self, self.tr("&Undo"))
        undoAction.setShortcuts(QKeySequence.Undo)
        redoAction = self.undoStack.createRedoAction(self, self.tr("&Redo"))
        redoAction.setShortcuts(QKeySequence.Redo)

        # Windows properties
        self.setWindowTitle('FreeTime')

        # self.setWindowIcon(QIcon('image\icon.png'))
        self.resize(self.window_size[0], self.window_size[1])
        self.move(0,  0)

        # Menu
        self.statusBar()
        self.initMenuBar()
        self.initToolbar()

        # GridLayout
        self.grid = MainGrid(parent=self)
        self.setCentralWidget(self.grid)

        self.show()


class CompareDialog(QDialog):

    def __init__(self, parent=None):
        super(CompareDialog, self).__init__(parent)

        self.parent = parent

        self.title = 'Compare'
        self.text1 = "Current Space"
        self.text2 = "Empty Space"

        self.initUI()

    def initUI(self):

        self.setWindowTitle(self.title)

        buttonBox = QDialogButtonBox(QDialogButtonBox.Ok | QDialogButtonBox.Cancel)
        buttonBox.accepted.connect(self.accept_btn)
        buttonBox.rejected.connect(self.reject_btn)

        layout = QFormLayout(self)

        label1 = QLabel("Space 1: ")
        label2 = QLabel("Space 2: ")
        comboBox1 = QComboBox(self)

        comboBox1.addItem("Current Space")
        comboBox1.addItem("Empty Space")
        comboBox1.addItem("Recent Save")
        comboBox1.addItem("Extern Space")

        comboBox2 = QComboBox(self)

        comboBox2.addItem("Empty Space")
        comboBox2.addItem("Current Space")
        comboBox2.addItem("Recent Save")
        comboBox2.addItem("Extern Space")

        comboBox1.activated[str].connect(self.selectionchange1)
        comboBox2.activated[str].connect(self.selectionchange2)

        layout.addRow(label1, comboBox1)
        layout.addRow(label2, comboBox2)
        layout.addWidget(buttonBox)

        self.setLayout(layout)

        self.show()

    def selectionchange1(self, txt):
        self.text1 = txt

    def selectionchange2(self, txt):
        self.text2 = txt

    def accept_btn(self):

        if self.text1 == "Current Space":
            week1 = self.parent.grid.week
        elif self.text1 == "Empty Space":
            week1 = WeekSpace(0, 0)
        elif self.text1 == "Recent Save":
            week1 = self.parent._save_week_list.get(0)

        if self.text2 == "Empty Space":
            week2 = WeekSpace(0, 0)
        elif self.text2 == "Current Space":
            week2 = self.parent.grid.week
        elif self.text2 == "Recent Save":
            week2 = self.parent._save_week_list.get(0)

        cmp_matrix = week1.cmp_week(week2)
        for row_index, row in enumerate(cmp_matrix):
            for col_index, item in enumerate(row):
                if cmp_matrix[row_index][col_index]:
                    week2.get_space(row_index, col_index).state = True

        cmp_week = CompareCommand(self.parent.grid, week2)
        self.parent.undoStack.push(cmp_week)

        self.accept()

    def reject_btn(self):
        self.reject()


class CompareCommand(QUndoCommand):
    def __init__(self, grid, cmp_week):
        super(CompareCommand, self).__init__()

        self._grid = grid
        self._cmp_week = cmp_week

        self._week_backup = self._grid.week

    def undo(self):
        self._grid.week = self._week_backup

    def redo(self):
        self._grid.set_cmp_week(self._cmp_week)


class ClearCommand(QUndoCommand):
    def __init__(self, grid):
        super(ClearCommand, self).__init__()

        self._grid = grid

        self._week_backup = self._grid.week
        self._week = self._grid.week

    def undo(self):
        self._week = self._week_backup
        self._grid.week = self._week_backup

    def redo(self):
        self._week = WeekSpace(0, 0)
        self._grid.week = WeekSpace(0, 0)


class SaveCommand(object):
    def __init__(self, name, week, num):

        self._nickname = name
        self._week = week
        self._num = num

    @property
    def nickname(self):
        return self._nickname

    @nickname.setter
    def set_name(self, name):
        self._nickname = name

    @property
    def week(self):
        return self._week

    @property
    def num(self):
        return self._num


class MainGrid(QWidget):
        def __init__(self, parent=None):
            super(MainGrid, self).__init__(parent)

            self.parent = parent

            self._week = WeekSpace(0, 0)
            self._week.get_space(0, 0).state = True
            self._week.get_space(0, 1).state = True
            self._week.get_space(1, 0).state = True
            self._week.get_space(6, 47).state = True
            self.fill_bool = False

            self.grid_layout_main = QGridLayout(self)

            self.scroll_area = ScrollGrid(self)
            self._grid_date = self.scroll_area.date_grid
            # self.clear_btn = QPushButton('Clear')
            # self.save_btn = QPushButton('Save')
            # self.fill_btn = QPushButton('Fill')

            # self.fill_btn.toggle()
            # self.fill_btn.setCheckable(True)

            # self.save_btn.clicked.connect(self.saveClicked)
            # self.fill_btn.clicked.connect(self.fillClicked)

            self.initUI()

        @property
        def grid_date(self):
            return self._grid_date

        @property
        def week(self):
            return self._week

        @week.setter
        def week(self, w):
            self._week = w
            self.grid_date.week = w
            self.grid_date.update_state()

        def set_cmp_week(self, w):
            self._week = w
            self.grid_date.week = w
            self.grid_date.update_state(True)

        def initUI(self):
            self.grid_layout_main.addWidget(self.scroll_area, 1, 1, 1, 8)
            # self.grid_layout_main.addWidget(self.save_btn, 2, 4, 1, 1)
            # self.grid_layout_main.addWidget(self.clear_btn, 2, 5, 1, 1)
            # self.grid_layout_main.addWidget(self.fill_btn, 2, 6, 1, 1)

        # def saveClicked(self, pressed):
        #     pass
        #
        # def fillClicked(self, pressed):
        #     if self.fill_btn.isChecked():
        #         self.fill_bool = True
        #     else:
        #         self.fill_bool = False


class ScrollGrid(QScrollArea):
    def __init__(self, parent=None):
        super(ScrollGrid, self).__init__(parent)

        self.parent = parent

        self._date_grid = None

        self.initUI()

    @property
    def date_grid(self):
        return self._date_grid

    def initUI(self):

        sizePolicy = QSizePolicy(QSizePolicy.Expanding, QSizePolicy.Preferred)
        sizePolicy.setHorizontalStretch(0)
        sizePolicy.setVerticalStretch(0)
        self.setSizePolicy(sizePolicy)

        self.setStyleSheet("border: none;")

        self.setVerticalScrollBarPolicy(Qt.ScrollBarAlwaysOn)
        self.setHorizontalScrollBarPolicy(Qt.ScrollBarAlwaysOff)
        self.setWidgetResizable(True)
        # self.setFixedHeight(950)
        # self.setFixedWidth(1900)

        self._date_grid = DateGrid(self.parent.week, self)
        self.setWidget(self._date_grid)


class DateGrid(QWidget):
    def __init__(self, week, parent=None):
        super(DateGrid, self).__init__(parent)

        self.parent = parent

        self._week = week

        self.b1 = None
        self.b2 = None

        self._num_col = DAY_IN_WEEK
        self._num_row = self._week.get_day(0).num_space

        # Label
        self.daylabel = None
        self._visibility_day = True

        self.timelabel = None
        self._visibility_time = False

        self.base_style = "background-color:#333333; border: 2px solid #222222;border-radius: 5px;"
        self.pressed_style = "%sbackground-color:red;" % self.base_style
        self.freetime_style = "%sbackground-color:green;" % self.base_style
        self.default_style = "QPushButton{%s}" \
                             "QPushButton:pressed{%s}" \
                             "QPushButton:hover{background-color:#3c3c3c;}" \
                             % (self.base_style, self.pressed_style)

        self.grid_layout_main = QGridLayout(self)
        self.setLayout(self.grid_layout_main)
        self.grid_layout_main.setSpacing(0)
        self.grid_layout_main.setContentsMargins(0, 0, 0, 0)

        self.grid_layout_date = QGridLayout(self)
        self.grid_layout_date.setSpacing(1)

        self.initUI()

    @property
    def week(self):
        return self._week

    @week.setter
    def week(self, w):
        self._week = w
        
    @property
    def visibility_day(self):
        return self._visibility_day
    
    @visibility_day.setter 
    def visibility_day(self, v):
        self._visibility_day = v

        if v:
            self.daylabel.setVisible(True)
            self.daylabel.show()
        else:
            self.daylabel.setVisible(False)

    @property
    def visibility_time(self):
        return self._visibility_time

    @visibility_time.setter
    def visibility_time(self, v):
        self._visibility_time = v

        if v:
            self.timelabel.setVisible(True)
            self.timelabel.show()
        else:
            self.timelabel.setVisible(False)

    def update_theme(self):

        if self.parent.parent.parent.style == "Dark":

            self.base_style = "background-color:#333333; border: 2px solid #222222;border-radius: 5px;"
            self.pressed_style = "%sbackground-color:red;" % self.base_style
            self.freetime_style = "%sbackground-color:green;" % self.base_style
            self.default_style = "QPushButton{%s}" \
                                 "QPushButton:pressed{%s}" \
                                 "QPushButton:hover{background-color:#3c3c3c;}" \
                                 % (self.base_style, self.pressed_style)

        elif self.parent.parent.parent.style == "White":

            self.base_style = "border: 2px solid #222222;border-radius: 5px;"
            self.pressed_style = "%sbackground-color:red;" % self.base_style
            self.freetime_style = "%sbackground-color:green;" % self.base_style
            self.default_style = ""

        self.update_state()

    def initUI(self):

        self.daylabel = DayLabelDateGrid(self)
        self.daylabel.setVisible(self._visibility_day)
        self.timelabel = TimeLabelDateGrid(self)
        self.timelabel.setVisible(self._visibility_time)

        self.grid_layout_main.addWidget(self.timelabel, 1, 0, self.timelabel.w_size[0], self.timelabel.w_size[1])
        self.grid_layout_main.addWidget(self.daylabel, 0, 1, self.daylabel.w_size[0], self.daylabel.w_size[1])

        self.grid_layout_main.addLayout(self.grid_layout_date, 1, 1, self.timelabel.w_size[0], self.daylabel.w_size[1])

        # Grid button
        self.time_btn()

        self.update_state()

    def time_btn(self):
        # Generate the button grid
        for d in range(self._num_col):
            for t in range(self._num_row):

                time_btn = QPushButton("%s\n" %
                                       (self._week.get_space(d, t).num + 1,
                                        # self.week_space.get_space(d, t).title,
                                        # self.week_space.get_space(d, t).start,
                                        # self.week_space.get_space(d, t).end
                                        ))
                time_btn.setToolTip("%s\n%s\n%s" % (self._week.get_space(d, t).title,
                                                    self._week.get_space(d, t).description,
                                                    self._week.get_space(d, t).str()))

                self.grid_layout_date.addWidget(time_btn, t, d)

                time_btn.setStyleSheet(self.default_style)
                time_btn.setCheckable(True)
                time_btn.clicked[bool].connect(self.timebtnClicked)

    def timebtnClicked(self, pressed):

        sender = self.sender()

        index = self.grid_layout_date.indexOf(sender)

        # 1D index to 2D index
        if index >= 0:
            day, time = np.unravel_index(index, (self._num_col, self._num_row))

        # Click modifier
        modifiers = QApplication.keyboardModifiers()
        if modifiers == Qt.ControlModifier:
            self.edit_info(day, time)
        else:
            if self._week.get_space(day, time).state is False:

                sender.setStyleSheet(self.pressed_style)
                self._week.get_space(day, time).state = True

                # TODO
                # Fill
                if self.parent.parent.fill_bool:
                    if self.b1 is None:
                        self.b1 = (day, time)
                    else:
                        self.b2 = (day, time)
                    if self.b1[0] == self.b2[0]:
                        self._week.get_day(self.b1[0]).fill_gap(self.b1[1], self.b2[1])
                        self.update_state()
                # if self.week_space.get_space(day, time-1).state:
                # pass
                #
                # if self.week_space.get_space(day, time+1).state:
                #     pass

            elif self._week.get_space(day, time).state:
                sender.setStyleSheet(self.default_style)
                self._week.get_space(day, time).state = False

    def edit_info(self, d, t):
        edit_dialog = SpaceEditDialog(d, t, parent=self)

    def update_state(self, compare=False):
        iteration = 0
        items = (self.grid_layout_date.itemAt(i)
                 for i in range(self.grid_layout_date.count()))
        for w in items:
            d, t = np.unravel_index(iteration, (self._num_col, self._num_row))
            if self._week.get_space(d, t).state:
                if compare:
                    w.widget().setStyleSheet(self.freetime_style)
                else:
                    w.widget().setStyleSheet(self.pressed_style)
            elif self._week.get_space(d, t).state is False:
                w.widget().setStyleSheet(self.default_style)
            iteration = iteration + 1


class SpaceEditDialog(QDialog):
    def __init__(self, d, t, parent=None):
        super(SpaceEditDialog, self).__init__(parent)

        self.parent = parent
        self._day = d
        self._time = t

        self._space = self.parent.week.get_space(self._day, self._time)

        self.title_text = QLineEdit(self)
        self.description_text = QLineEdit(self)
        self.state_btn = QRadioButton("State")

        self.initUI()

    def initUI(self):
        self.setWindowTitle("Edit Info")

        buttonBox = QDialogButtonBox(QDialogButtonBox.Ok | QDialogButtonBox.Cancel)
        buttonBox.accepted.connect(self.accept_btn)
        buttonBox.rejected.connect(self.reject_btn)

        layout = QFormLayout(self)

        title_label = QLabel("Title")
        description_label = QLabel("Description")
        lapse_label = QLabel(self._space.str())

        self.title_text.setText(self._space.title)
        self.description_text.setText(self._space.description)
        self.state_btn.setChecked(self._space.state)

        layout.addRow(title_label, self.title_text)
        layout.addRow(description_label, self.description_text)
        layout.addWidget(self.state_btn)
        layout.addWidget(lapse_label)
        layout.addWidget(buttonBox)

        self.setLayout(layout)

        self.show()

    def accept_btn(self):
        self._space.title = self.title_text.text()
        self._space.description = self.description_text.text()
        self._space.state = self.state_btn.isChecked()
        self.accept()

    def reject_btn(self):
        self.reject()


class DayLabelDateGrid(QWidget):
    def __init__(self, parent=None):
        super(DayLabelDateGrid, self).__init__(parent)

        self.parent = parent

        self.grid_layout_day = None

        self._num_col = 7
        self._num_row = 1

        self.initUI()

    @property
    def w_size(self):
        return self._num_row, self._num_col

    def initUI(self):

        self.grid_layout_day = QGridLayout(self)
        self.grid_layout_day.setSpacing(0)
        self.grid_layout_day.setContentsMargins(0, 0, 0, 5)

        for num, name in enumerate(day_name):
            day_label = QLabel(self, text=name)
            self.grid_layout_day.addWidget(day_label, 0, num+1, 1, 1)

        self.show()


class TimeLabelDateGrid(QWidget):
    def __init__(self, parent=None):
        super(TimeLabelDateGrid, self).__init__(parent)

        self.parent = parent

        self._num_col = 1
        self._num_row = self.parent.week.get_day(0).num_space

        self.grid_layout_time = None
        self.blank_label = QLabel(self, text="")

        self.initUI()

    @property
    def w_size(self):
        return self._num_row, self._num_col

    def initUI(self):

        self.grid_layout_time = QGridLayout(self)
        self.grid_layout_time.setSpacing(0)
        self.grid_layout_time.setContentsMargins(0, 0, 5, 0)

        for i in range(self.parent.week.get_day(0).num_space):
            hours_start = self.parent.week.get_space(0, i).hours_start
            timespace_label = QLabel(self, text=hours_start)
            self.grid_layout_time.addWidget(timespace_label, i, 0, 1, 1)


def main():
    app = QApplication([])
    ex = MainGUI()
    ex.show()
    sys.exit(app.exec_())


if __name__ == '__main__':
    main()
