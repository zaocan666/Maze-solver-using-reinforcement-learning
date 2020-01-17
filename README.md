# 强化学习求解迷宫问题
## 核心代码
- maze.py: 迷宫类的实现，迷宫信息用一个二维数组表示，数组中的每个数代表一个方格，数字值代表方格类型（如0表示墙, 2表示陷阱, 3表示火）。
- train_qtable.py: Q表类的实现，Q表类有Q值的存储，决策的进行，Q表的学习等功能函数，进行预测和学习时会与迷宫（“环境”）进行交互，对其输入动作，得到反馈。
- train_network.py: 监督学习模型的学习，预测等实现。
- git.py: 监督学习用到的批量式学习仓库。
- maze_map.py: 存储6个事先定义好的迷宫
- draw.py: Q表的可视化以及完整走迷宫过程的呈现。

## UI代码
- ui.py: 顶层窗口，有两个标签页
- ui_basic.py: “已有迷宫”标签页的实现，用户可以从我们定义好的几个迷宫中选择一个，进行训练并查看完整的走迷宫过程。
- ui_userDefine.py：“用户自定义”标签页的实现，用户可以输入任意大小的迷宫，自定义火焰周期，训练次数上限。之后进行训练，并以三种不同的速度查看完整的走迷宫结果。
- draw_ui.py: 在ui界面绘制Q表和走迷宫过程。

## 运行方法
- 打开“可执行文件/ui.exe”
- 运行“代码/ui.py”
- 运行“代码/train_qtable.py”，对maze_map中定义的迷宫进行训练，训练结束后显示Q表和完整走迷宫过程。

## 编译运行环境
python 3.6, pyqt 5.13.1, matplotlib 3.0.2, numpy 1.15.2, Pyinstaller 3.5

## Reference
https://zhuanlan.zhihu.com/p/39617577
https://github.com/erikdelange/Reinforcement-Learning-Maze
