print('请确保已经安装了pygame模块，否则此功能将无法运行')
print('')
print('Make sure that you have installed the pygame module, otherwise this feature will not work')
print('')
print('==========================================================================================')
print('按enter确认已经安装，可以正常运行，否则请先安装pygame第三方库')
print('')
print('Press enter to confirm that it has been installed and can work normally, otherwise please install the pygame '
      + '\n' + 'third-party library first')
input('')
print('==========================================================================================')

import pygame
from pygame.locals import *
from pygame.color import THECOLORS


def connecting_points_test():
    """
    from lzlzhn import connecting_points_test
    connecting_points_test.connecting_points_test()
    """
    pygame.init()
    canvas = pygame.display.set_mode((600, 600))
    canvas.fill((255, 255, 255))
    pygame.display.set_caption('TEST')

    # 鼠标点击次数
    mouBut = 0
    # 空格键按下次数
    keyDow = 0

    def handle():
        global mouBut, keyDow
        for event in pygame.event.get():
            if event.type == QUIT:
                pygame.quit()
                exit()
            # 当按下鼠标
            if event.type == MOUSEBUTTONDOWN:
                x, y = event.pos
                # 且在黑色矩形内
                if 200 <= x <= 400 and 200 <= y <= 400:
                    mouBut += 1
            # 当按下键盘
            if event.type == KEYDOWN:
                # 且为空格键
                if event.key == K_SPACE:
                    keyDow += 1

    while True:
        # 每次重绘背景
        canvas.fill((255, 255, 255))
        # 鼠标测试，绘制矩形
        pygame.draw.rect(canvas, (0, 0, 0), (200, 200, 200, 200), 0)
        # 绘制文字
        font1 = pygame.font.SysFont('Consolas', 30)
        font2 = font3 = font4 = font5 = font6 = font1
        canvas.blit(font1.render('MouseButtonDown:%d' % mouBut, True, (0, 0, 0)), (10, 10))
        canvas.blit(font2.render('KeyDown:%d' % keyDow, True, (0, 0, 0)), (10, 50))
        canvas.blit(font3.render('CLICK ME!', True, (255, 255, 255)), (225, 275))
        canvas.blit(font4.render('Click the black rectangle or press', True, (255, 0, 0)), (10, 100))
        canvas.blit(font5.render('the spacebar!', True, (255, 0, 0)), (10, 150))
        canvas.blit(font6.render('By Zhuolong Li', True, (0, 0, 255)), (200, 500))
        handle()
        pygame.display.update()
