import os, sys
from dynamic_Ui import Ui_MainWindow
from PyQt5.QtWidgets import QApplication, QMainWindow, QFileDialog, QMessageBox
from PyQt5.QtCore import QObject, pyqtSignal, Qt
from PyQt5.QtGui import QTextCursor
from extract import data_extract
import numpy as np
from dynamic_interger_plan import DynamicIntergerPlan
import pulp as lp

class NewMainWindow(QMainWindow):
    def closeEvent(self, event):
        """Shuts down application on close."""
        # Return stdout to defaults.
        sys.stdout = sys.__stdout__
        super().closeEvent(event)


app = QApplication(sys.argv)
MainWindow = NewMainWindow()


class Stream(QObject):
    newText = pyqtSignal(str)

    def write(self, text):
        self.newText.emit(str(text))
        QApplication.processEvents()


class MyMainWindow(Ui_MainWindow):
    def __init__(self):
        super().__init__()
        self.setupUi(MainWindow)
        sys.stdout = Stream(newText=self.onUpdateEdit)
        self.data = None

    def onUpdateEdit(self, text):
        cursor = self.textEdit.textCursor()
        cursor.movePosition(QTextCursor.End)
        cursor.insertText(text)
        self.textEdit.setTextCursor(cursor)
        self.textEdit.ensureCursorVisible()

    def fit(self):
        self.pushButton.clicked.connect(self.choose_file)
        self.pushButton_3.clicked.connect(self.run)
        self.pushButton_3.setFocus()
        self.pushButton_3.setShortcut(Qt.Key_Enter)
        self.pushButton_3.setDefault(True)
        self.lineEdit_2.setText('6000')
        self.lineEdit_3.setText('50')
        self.lineEdit_4.setText('100')
        self.lineEdit_5.setText('2')
        self.pushButton_4.clicked.connect(self.save_data)
    def choose_file(self):
        file, type = QFileDialog.getOpenFileName(MainWindow, "选取文件", os.getcwd())
        if file:
            self.lineEdit.setText(file)

        else:
            print('Error: 选择错误,请重新选择文件')

    def save_data(self):
        dir, type = QFileDialog.getSaveFileName(MainWindow, '保存数据至', './results.txt', "All Files (*);;Text Files (*.txt)")
        if dir:
            with open(dir, 'w+') as f:
                if self.data:
                    f.write('管路下料尺寸分布为: ')
                    for i in self.data[2]:
                        f.write(str(i))
                    f.write('\n每根管材利用率为: \n' + str(['{:.2f}%'.format(i * 100) for i in self.data[0]]))
                    f.write('\n管材平均利用率为:\n {:.2f}%'.format(np.mean(self.data[0]) * 100))
                    print('计算结果写入' + dir + '文件中')
                else:
                    QMessageBox.warning(MainWindow, 'warning', '请先计算结果', QMessageBox.Ok)


    def distribute(self, weights, init):
        big = []
        for result in init:
            dt = dict(zip(weights, result))
            ls = []
            for i in weights:
                if dt.get(i):
                    ls.extend([i]*int(dt.get(i)))
            big.append(ls)
        return big

    def run(self):
        filename = self.lineEdit.text()
        if filename:
            self.weights, self.nums = data_extract(filename)
        else:
            QMessageBox.warning(MainWindow, 'warning', '请先选择数据文件', QMessageBox.Ok)
            return
        try:
            L = eval(self.lineEdit_2.text())
            m1 = eval(self.lineEdit_3.text())
            m2 = eval(self.lineEdit_4.text())
            N = eval(self.lineEdit_5.text())
        except:
            QMessageBox.warning(MainWindow, 'warning', 'L,m1,m2,N只能是整数')
            return
        if not (isinstance(L, int) and isinstance(m1, int) and isinstance(m2, int) and isinstance(N, int)):
            QMessageBox.warning(MainWindow, 'warning', 'L,m1,m2,N只能是整数')
            return
        dp = DynamicIntergerPlan(self.weights, self.nums, L, m1, m2, N)
        init = dp.fit()
        pro = np.sum(init * self.weights, axis=1, dtype=int)
        for i, j in enumerate(pro):
            pro[i] += m1 + m2 + np.sum(init[i]) * N
        ratios = pro / L
        print('-'*20)
        print('管路下料尺寸分布为: ')
        dis = self.distribute(self.weights, init)
        self.data =[ratios, init, dis]
        for i in dis:
            print(i, end='\n')
        print('\n')
        print('管路下料所需管材数目为: {}根'.format(len(init)), end='\n\n')
        print('每根管材利用率为: \n' + str(['{:.2f}%'.format(i*100) for i in ratios]), end='\n\n')
        print('管材平均利用率为: {:.2f}%'.format(np.mean(ratios)*100), end='\n------\n计算成功!')



myui = MyMainWindow()
myui.fit()
MainWindow.show()
sys.exit(app.exec_())