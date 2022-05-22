print('请确保已经安装了PyAutoGUI模块，否则此功能将无法运行')
print('')
print('Make sure that you have installed the PyAutoGUI module, otherwise this feature will not work')
print('')
print('==========================================================================================')
print('')
print('按enter确认已经安装，可以正常运行，否则请先安装PyAutoGUI第三方库')
print('')
print('Press enter to confirm that it has been installed and can work normally, otherwise please install the PyAutoGUI '
      + '\n' + 'third-party library first')
input('')
print('==========================================================================================')

import time
import pyautogui as pg


def connecting_points():
    """
    from lzlzhn import connecting_points
    connecting_points.connecting_points()
    """
    print('请输入连点次数')
    print('Please enter the number of consecutive dots')
    times = input('')
    times = int(times)
    print('十秒后开始连点/Start in ten seconds')
    time.sleep(10)
    for x in range(times):
        pg.click()
