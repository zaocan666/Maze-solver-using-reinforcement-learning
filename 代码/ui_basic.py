from PyQt5.QtWidgets import QLabel, QComboBox, QPushButton, QMessageBox, QWidget, QGroupBox, QGridLayout
from PyQt5.QtCore import QBasicTimer, QRect
from PyQt5.QtGui import QFont
import numpy as np
from maze_map import Mazes
from maze import Maze
from train_qtable import QTableModel
import time

from draw_ui import Draw_ui

class Ui_basic(QWidget):
    def __init__(self):
        super().__init__()
        self.model = None

    def initUI(self):
        self.resize(1200, 700)

        self.pic_list=['maze7_1', 'maze7_2', 'maze7_3', 'maze10_1', 'maze10_2', 'maze10_3' ]
        self.timer = QBasicTimer()
        widget1 = QWidget(parent=self)
        widget1.setGeometry(QRect(30, 50, 800, 500))
        table_area = QGroupBox(parent=widget1) #图形显示区域
        table_area.setGeometry(QRect(widget1.x(), widget1.y(), widget1.width(), widget1.height()))

        self.Plot = Draw_ui(width=3, height=3, dpi=100)
        gridlayout1 = QGridLayout(table_area)  # 继承容器groupBox
        gridlayout1.addWidget(self.Plot, 0, 1)

        pic_choose_label = QLabel(self)
        pic_choose_label.move(table_area.x()+table_area.width()+30, table_area.y()+20)
        pic_choose_label.setText("选择迷宫：")
        self.pic_choose_combo = QComboBox(self)
        self.pic_choose_combo.move(pic_choose_label.geometry().x()+pic_choose_label.geometry().width()+30, pic_choose_label.geometry().y())
        self.pic_choose_combo.resize(150,self.pic_choose_combo.geometry().height())
        self.pic_choose_combo.addItems(self.pic_list)
        self.pic_choose_combo.currentIndexChanged.connect(self.pic_change)
        self.pic_change()

        middle_x = (pic_choose_label.geometry().x() + self.pic_choose_combo.geometry().x() + self.pic_choose_combo.geometry().width()) / 2

        self.playing_index = -1
        self.problem_solving = False

        self.solve_problem_button = QPushButton(parent=self)
        self.solve_problem_button.setText("训练（可跳过训练）")
        self.solve_problem_button.move(middle_x - self.solve_problem_button.width() / 2, self.pic_choose_combo.y()+self.pic_choose_combo.height()+100)
        self.solve_problem_button.pressed.connect(self.solve_button_pressed)

        self.solve_test = QLabel(parent=self)  # 解答过程中的信息显示
        self.solve_test.setText("正在训练。。。")
        self.solve_test.resize(400, self.solve_test.height())
        self.solve_test.setFont(QFont("Fixed",7))
        self.solve_test.move(middle_x - self.solve_test.geometry().width() / 2,
                             self.solve_problem_button.geometry().y() + self.solve_problem_button.geometry().height() + 20)
        self.solve_test.setHidden(True)

        speed_choose_label = QLabel(self)
        speed_choose_label.move(self.solve_test.x()+20, self.solve_test.geometry().y() + 40)
        speed_choose_label.setText("播放速度：")
        self.play_speed_combo = QComboBox(self)
        self.play_speed_combo.move(speed_choose_label.geometry().x() + speed_choose_label.geometry().width() + 30,
                                   speed_choose_label.geometry().y())
        self.play_speed_combo.addItems(["高速", "中速", "慢速"])

        play_button = QPushButton(self)
        play_button.setText("播放走迷宫过程")
        play_button.move(middle_x - play_button.geometry().width() / 2,
                         self.play_speed_combo.geometry().y() + self.play_speed_combo.geometry().height() + 40)
        play_button.pressed.connect(self.play_button_pressed)

    def pic_change(self):
        self.timer.stop()
        current_text = self.pic_choose_combo.currentText()
        maze = Mazes[current_text]
        my_maze = Maze(maze_map=np.array(maze), period=2)
        self.model = QTableModel(my_maze)

        try:
            self.model.load_table('saved_qtable/'+current_text+'.npy')
        except:
            QMessageBox.information(self, "提示", "没找到Q表保存文件", QMessageBox.Ok | QMessageBox.Close,
                                    QMessageBox.Close)

        self.model.play_game((0, 0), 0)
        self.Plot.draw_root(self.model.my_maze, (0, 0), 1, 0, False)
        self.Plot.draw_qtable(qtable_model=self.model, time_=self.model.my_maze.period-1 if self.model.my_maze.period!=0 else 0, fire_flag=True)

    def play_button_pressed(self):
        if self.model == None:
            QMessageBox.information(self, "提示", "请先选择迷宫", QMessageBox.Ok | QMessageBox.Close,
                                    QMessageBox.Close)
            return

        self.model.play_game((0, 0), 0)
        speed_text = self.play_speed_combo.currentText()
        self.playing_index = 0
        if speed_text == "高速":
            self.timer.start(150, self)
        elif speed_text == "中速":
            self.timer.start(500, self)
        else:
            self.timer.start(1500, self)

    def timerEvent(self, event):
        if event.timerId() == self.timer.timerId():
            period = self.model.my_maze.period
            if period != 0 and (self.playing_index % period) >= period / 2:
                fire_flag = True
            else:
                fire_flag = False

            self.Plot.draw_qtable(self.model, self.playing_index % period if period != 0 else 0, fire_flag)
            self.Plot.draw_root(self.model.my_maze, (0,0), self.playing_index, period, fire_flag)

            self.playing_index = self.playing_index + 1

            if self.playing_index >= len(self.model.my_maze.visited) + 2:
                self.playing_index = 0
                # print("up",self.playing_index)
        else:
            super(Ui_basic, self).timerEvent(event)

    def solve_button_pressed(self):
        if self.problem_solving:
            return
        if type(self.model)==type(None):
            QMessageBox.information(self, "提示", "请先选择迷宫", QMessageBox.Ok | QMessageBox.Close, QMessageBox.Close)
            return

        self.problem_solving = True
        self.playing_index = -1
        self.solve_test.setHidden(False)
        self.timer.stop()
        self.repaint()

        start_time = time.time()
        #path = "tangrams\\" + self.parent().pic_choose_combo.currentText() + ".png"
        self.model.train(output_line = self.solve_test, main_ui=self)
        end_time = time.time()

        QMessageBox.information(self, "提示", "完成训练，用时：%.3f s" % (end_time - start_time),
                                QMessageBox.Ok | QMessageBox.Close, QMessageBox.Close)

        self.Plot.draw_qtable(qtable_model=self.model,
                              time_=self.model.my_maze.period - 1 if self.model.my_maze.period != 0 else 0,
                              fire_flag=True)
        self.problem_solving = False
        self.solve_test.setHidden(True)
