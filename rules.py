import pygame,sys
import numpy
import os
import time

import content

# 绝杀标记
end = 0
# Alpha, Beta初始值
min_val = -10000
max_val = 10000
# 检索最大深度
max_depth = 4
# AI路径列表
way = []
way_before = []
# 初始化pygame
pygame.init()
# 设置窗口的大小，单位为像素
size = width, height = 1380,720
# 设置初始窗口相对屏幕的位置
os.environ['SDL_VIDEO_WINDOW_POS'] = "150,50"
screen = pygame.display.set_mode(size, pygame.RESIZABLE)
# 设置窗口的标题
pygame.display.set_caption('Chess Game')

# 定义颜色
WHITE = (255, 255, 255)
BLACK = ( 0, 0, 0)
RED = (255, 0, 0)
GREEN = ( 0, 255, 0)
BLUE = ( 0, 0, 255)

# 设置背景
# screen.fill(WHITE)

# 游戏背景图片
background_img = pygame.image.load("imgs/wallpaper/fgo.jpg")
# 游戏棋盘
chessboard_img = pygame.image.load("imgs/s1/bg.png")
# 棋子
chessboard_map = [
    ["b_c", "b_m", "b_x", "b_s", "b_j", "b_s", "b_x", "b_m", "b_c"],
    ["", "", "", "", "", "", "", "", ""],
    ["", "b_p", "", "", "", "", "", "b_p", ""],
    ["b_z", "", "b_z", "", "b_z", "", "b_z", "", "b_z"],
    ["", "", "", "", "", "", "", "", ""],
    ["", "", "", "", "", "", "", "", ""],
    ["r_z", "", "r_z", "", "r_z", "", "r_z", "", "r_z"],
    ["", "r_p", "", "", "", "", "", "r_p", ""],
    ["", "", "", "", "", "", "", "", ""],
    ["r_c", "r_m", "r_x", "r_s", "r_j", "r_s", "r_x", "r_m", "r_c"],
]
# 以点显示可移动路径数组
move_map = [[False for c in range(9)]for r in range(10)]

# 棋子周围方框显示
rect_before = [100000,100000]
rect = [100000,100000]

# 加载并播放一个特效音频文件
select = pygame.mixer.Sound('music/select.WAV')
eat = pygame.mixer.Sound('music/eat.ogg')
eat.set_volume(0.5)
# sound.play()

# 加载背景音乐文件
pygame.mixer.music.load('music/Old_people_and_sea.mp3')
# 设置音量
pygame.mixer.music.set_volume(0.2)
# 播放背景音乐，第一个参数为播放的次数（-1表示无限循环），第二个参数是设置播放的起点（单位为秒）
pygame.mixer.music.play(-1, 0.0)

def copy_map(map1):
    map_copy =  [["" for c in range(9)]for r in range(10)]
    i1 = 0
    while i1 < 10:
        y1 = 0
        while y1 < 9:
            map_copy[i1][y1] = map1[i1][y1]
            y1 += 1
        i1 += 1
    return map_copy

# 获取鼠标点击的棋子在棋盘中的相对位置 比如:(0,0)
def get_status(num):
    x = 91 # 120 - 29
    y = 44 # 73 - 29
    x_flag = 0
    y_flag = 0
    while x <= 604:
        x1 = x + 57
        if num[0] >= x and num[0] < x1:
            while y <= 614:
                y1 = y + 57
                if num[1] >= y and num[1] < y1:
                    return (y_flag,x_flag)
                y += 57
                y_flag += 1
        x += 57 
        x_flag += 1
    return (-1,-1)

# 棋子移动更新地图
def update_map(status_before,status_past):
    global chessboard_map
    chessboard_map[status_past[0]][status_past[1]] = chessboard_map[status_before[0]][status_before[1]]
    chessboard_map[status_before[0]][status_before[1]] = ""

# 判断棋子是红方还是黑方
def judge_red_black(status):
    global chessboard_map
    flag = chessboard_map[status[0]][status[1]]
    if flag == "b_c" or flag == "b_m" or flag == "b_x" or flag == "b_s" or flag == "b_j" or flag == "b_p" or flag == "b_z":
        return "black"
    elif flag == "r_c" or flag == "r_m" or flag == "r_x" or flag == "r_s" or flag == "r_j" or flag == "r_p" or flag == "r_z":
        return "red"
    else:
        return ""

# 判断棋子走之后(非将军棋子)是否会出现将军碰面的情况
def have_two_jiang(line_be, num_be, line_pa, num_pa):
    global chessboard_map
    chessboard = copy_map(chessboard_map)
    update_map((line_be, num_be), (line_pa, num_pa))
    line_y = 0
    while line_y < 3:
        if chessboard_map[line_y][num_pa] == "b_j":
            line_y1 = 7
            while line_y1 < 10:
                if chessboard_map[line_y1][num_pa] == "r_j":
                    flag_line = line_y + 1
                    while flag_line < line_y1:
                        if chessboard_map[flag_line][num_pa] != "":
                            chessboard_map = copy_map(chessboard)
                            return False
                        flag_line += 1
                    chessboard_map = copy_map(chessboard)
                    return True
                line_y1 += 1
            chessboard_map = copy_map(chessboard)
            return False
        elif chessboard_map[line_y][num_be] == "b_j":
            line_y1 = 7
            while line_y1 < 10:
                if chessboard_map[line_y1][num_be] == "r_j":
                    flag_line = line_y + 1
                    while flag_line < line_y1:
                        if chessboard_map[flag_line][num_be] != "":
                            chessboard_map = copy_map(chessboard)
                            return False
                        flag_line += 1
                    chessboard_map = copy_map(chessboard)
                    return True
                line_y1 += 1
            chessboard_map = copy_map(chessboard)
            return False
        line_y += 1
    chessboard_map = copy_map(chessboard)
    return False

# 判断棋子移动范围内是否有其他棋子，传入参数：（移动前的坐标，移动后的坐标，移动前的颜色，移动后的颜色）
def move_ok(status_be,status_pa,step):
    global chessboard_map
    global move_map
    # 返回错误
    if step % 2 == 0 and judge_red_black(status_be) == "red" or step % 2 == 1 and judge_red_black(status_be) == "black":
        return 0
    # 判断是否对将
    if status_be[1] >= 3 and status_be[1] <= 5:
        if have_two_jiang(status_be[0], status_be[1], status_pa[0], status_pa[1]):
            return 1
    # 判断是否被将军
    if move_map[status_pa[0]][status_pa[1]]:
        move_bak = copy_map(move_map)
        update_map(status_be, status_pa)
        i1 = 0
        while i1 < 10:
            y1 = 0
            while y1 < 9:
                if step % 2 == 0 and judge_red_black((i1,y1)) == "red" or step % 2 == 1 and judge_red_black((i1,y1)) == "black":
                    move_map = [[False for c in range(9)]for r in range(10)]
                    draw_point_map((i1,y1))
                    # 不能移动，否则被将
                    if is_jiang((i1,y1)):
                        move_map = copy_map(move_bak)
                        update_map(status_pa, status_be)
                        return 2
                    
                y1 += 1
            i1 += 1
        update_map(status_pa, status_be)
        move_map = copy_map(move_bak)
        return 3
    return 0

# 绘制显示可走路径
def draw_point_map(status):
    global chessboard_map
    global move_map
    type_piece = chessboard_map[status[0]][status[1]]
    line_s1 = status[0] - 1
    line_s2 = status[0] - 2
    line_x1 = status[0] + 1
    line_x2 = status[0] + 2
    row_z1  = status[1] - 1
    row_z2  = status[1] - 2
    row_y1  = status[1] + 1
    row_y2  = status[1] + 2
    # 车
    if type_piece == "b_c" or type_piece == "r_c":
        while line_x1 <= 9:
            if chessboard_map[line_x1][status[1]] == "":
                move_map[line_x1][status[1]] = True
            
            elif judge_red_black((line_x1,status[1])) != judge_red_black(status):
                move_map[line_x1][status[1]] = True
                break
            else :
                break
            line_x1 += 1
        while line_s1 >= 0:
            if chessboard_map[line_s1][status[1]] == "":
                move_map[line_s1][status[1]] = True
            elif judge_red_black((line_s1,status[1])) != judge_red_black(status):
                move_map[line_s1][status[1]] = True
                break
            else :
                break
            line_s1 -= 1
        while row_y1 <= 8:
            if chessboard_map[status[0]][row_y1] == "":
                move_map[status[0]][row_y1] = True
            elif judge_red_black((status[0],row_y1)) != judge_red_black(status):
                move_map[status[0]][row_y1] = True
                break
            else :
                break
            row_y1 += 1
        while row_z1 >= 0:
            if chessboard_map[status[0]][row_z1] == "":
                move_map[status[0]][row_z1] = True
            elif judge_red_black((status[0],row_z1)) != judge_red_black(status):
                move_map[status[0]][row_z1] = True
                break
            else :
                break
            row_z1 -= 1
    # 马
    if type_piece == "b_m" or type_piece == "r_m":
        # 上二左一
        if line_s2 >= 0 and row_z1 >= 0 and chessboard_map[line_s1][status[1]] == "" and judge_red_black((line_s2,row_z1)) != judge_red_black(status):
            move_map[line_s2][row_z1] = True
        # 上二右一
        if line_s2 >= 0 and row_y1 <= 8 and chessboard_map[line_s1][status[1]] == "" and judge_red_black((line_s2,row_y1)) != judge_red_black(status):
            move_map[line_s2][row_y1] = True
        # 上一左二
        if line_s1 >= 0 and row_z2 >= 0 and chessboard_map[status[0]][row_z1] == "" and judge_red_black((line_s1,row_z2)) != judge_red_black(status):
            move_map[line_s1][row_z2] = True
        # 上一右二
        if line_s1 >= 0 and row_y2 <= 8 and chessboard_map[status[0]][row_y1] == "" and judge_red_black((line_s1,row_y2)) != judge_red_black(status):
            move_map[line_s1][row_y2] = True
        # 下二左一
        if line_x2 <= 9 and row_z1 >= 0 and chessboard_map[line_x1][status[1]] == "" and judge_red_black((line_x2,row_z1)) != judge_red_black(status):
            move_map[line_x2][row_z1] = True
        # 下二右一
        if line_x2 <= 9 and row_y1 <= 8 and chessboard_map[line_x1][status[1]] == "" and judge_red_black((line_x2,row_y1)) != judge_red_black(status):
            move_map[line_x2][row_y1] = True
        # 下一左二
        if line_x1 <= 9 and row_z2 >= 0 and chessboard_map[status[0]][row_z1] == "" and judge_red_black((line_x1,row_z2)) != judge_red_black(status):
            move_map[line_x1][row_z2] = True
        # 下一右二
        if line_x1 <= 9 and row_y2 <= 8 and chessboard_map[status[0]][row_y1] == "" and judge_red_black((line_x1,row_y2)) != judge_red_black(status):
            move_map[line_x1][row_y2] = True
    # 象
    if type_piece == "b_x" or type_piece == "r_x":
        # 上二左二
        if line_s2 >= 0 and row_z2 >= 0 and chessboard_map[line_s1][row_z1] == "" and judge_red_black((line_s2,row_z2)) != judge_red_black(status):
            move_map[line_s2][row_z2] = True
        # 上二右二
        if line_s2 >= 0 and row_y2 <= 8 and chessboard_map[line_s1][row_y1] == "" and judge_red_black((line_s2,row_y2)) != judge_red_black(status):
            move_map[line_s2][row_y2] = True
        # 下二左二
        if line_x2 <= 9 and row_z2 >= 0 and chessboard_map[line_x1][row_z1] == "" and judge_red_black((line_x2,row_z2)) != judge_red_black(status):
            move_map[line_x2][row_z2] = True
        # 下二右二
        if line_x2 <= 9 and row_y2 <= 8 and chessboard_map[line_x1][row_y1] == "" and judge_red_black((line_x2,row_y2)) != judge_red_black(status):
            move_map[line_x2][row_y2] = True
        # 红黑判定
        if judge_red_black(status) == "black":
            if status[0] == 4:
                move_map[line_x2][row_z2] = False
                move_map[line_x2][row_y2] = False
        elif judge_red_black(status) == "red":
            if status[0] == 5:
                move_map[line_s2][row_z2] = False
                move_map[line_s2][row_y2] = False
    # 士
    if type_piece == "b_s" or type_piece == "r_s":
        # 红黑判定
        if judge_red_black(status) == "black":
            # 左上
            if line_s1 >= 0 and row_z1 >= 3 and judge_red_black((line_s1,row_z1)) != judge_red_black(status):
                move_map[line_s1][row_z1] = True
            # 右上
            if line_s1 >= 0 and row_y1 <= 5 and judge_red_black((line_s1,row_y1)) != judge_red_black(status):
                move_map[line_s1][row_y1] = True
            # 左下
            if line_x1 <= 2 and row_z1 >= 3 and judge_red_black((line_x1,row_z1)) != judge_red_black(status):
                move_map[line_x1][row_z1] = True
            # 右下
            if line_x1 <= 2 and row_y1 <= 5 and judge_red_black((line_x1,row_y1)) != judge_red_black(status):
                move_map[line_x1][row_y1] = True
        elif judge_red_black(status) == "red":
            # 左上
            if line_s1 >= 7 and row_z1 >= 3 and judge_red_black((line_s1,row_z1)) != judge_red_black(status):
                move_map[line_s1][row_z1] = True
            # 右上
            if line_s1 >= 7 and row_y1 <= 5 and judge_red_black((line_s1,row_y1)) != judge_red_black(status):
                move_map[line_s1][row_y1] = True
            # 左下
            if line_x1 <= 9 and row_z1 >= 3 and judge_red_black((line_x1,row_z1)) != judge_red_black(status):
                move_map[line_x1][row_z1] = True
            # 右下
            if line_x1 <= 9 and row_y1 <= 5 and judge_red_black((line_x1,row_y1)) != judge_red_black(status):
                move_map[line_x1][row_y1] = True
    # 将
    if type_piece == "b_j" or type_piece == "r_j":
        # 红黑判定
        if judge_red_black(status) == "black":
            # 上
            if line_s1 >= 0 and judge_red_black((line_s1,status[1])) != judge_red_black(status):
                move_map[line_s1][status[1]] = True
            # 下
            if line_x1 <= 2 and judge_red_black((line_x1,status[1])) != judge_red_black(status):
                move_map[line_x1][status[1]] = True
            # 左
            if row_z1 >= 3 and judge_red_black((status[0],row_z1)) != judge_red_black(status):
                move_map[status[0]][row_z1] = True
            # 右
            if row_y1 <= 5 and judge_red_black((status[0],row_y1)) != judge_red_black(status):
                move_map[status[0]][row_y1] = True
        elif judge_red_black(status) == "red":
            # 上
            if line_s1 >= 7 and judge_red_black((line_s1,status[1])) != judge_red_black(status):
                move_map[line_s1][status[1]] = True
            # 下
            if line_x1 <= 9 and judge_red_black((line_x1,status[1])) != judge_red_black(status):
                move_map[line_x1][status[1]] = True
            # 左
            if row_z1 >= 3 and judge_red_black((status[0],row_z1)) != judge_red_black(status):
                move_map[status[0]][row_z1] = True
            # 右
            if row_y1 <= 5 and judge_red_black((status[0],row_y1)) != judge_red_black(status):
                move_map[status[0]][row_y1] = True
    # 炮
    if type_piece == "b_p" or type_piece == "r_p":
        # 向下
        rap = 0
        while line_x1 <= 9:
            if rap == 0 and chessboard_map[line_x1][status[1]] == "":
                move_map[line_x1][status[1]] = True
            elif rap == 0:
                rap = 1
            elif rap == 1 and judge_red_black((line_x1,status[1])) != "" and judge_red_black((line_x1,status[1])) != judge_red_black(status):
                move_map[line_x1][status[1]] = True
                rap = 0
                break
            elif rap == 1 and judge_red_black((line_x1,status[1])) == judge_red_black(status):
                rap = 0
                break
            line_x1 += 1
        # 向上
        rap = 0
        while line_s1 >= 0:
            if rap == 0 and chessboard_map[line_s1][status[1]] == "":
                move_map[line_s1][status[1]] = True
            elif rap == 0:
                rap = 1
            elif rap == 1 and judge_red_black((line_s1,status[1])) != "" and judge_red_black((line_s1,status[1])) != judge_red_black(status):
                move_map[line_s1][status[1]] = True
                rap = 0
                break
            elif rap == 1 and judge_red_black((line_s1,status[1])) == judge_red_black(status):
                rap = 0
                break
            line_s1 -= 1
        # 向右
        rap = 0
        while row_y1 <= 8:
            if rap == 0 and chessboard_map[status[0]][row_y1] == "":
                move_map[status[0]][row_y1] = True
            elif rap == 0:
                rap = 1
            elif rap == 1 and judge_red_black((status[0],row_y1)) != "" and judge_red_black((status[0],row_y1)) != judge_red_black(status):
                move_map[status[0]][row_y1] = True
                rap = 0
                break
            elif rap == 1 and judge_red_black((status[0],row_y1)) == judge_red_black(status):
                rap = 0
                break
            row_y1 += 1
        # 向左
        rap = 0
        while row_z1 >= 0:
            if rap == 0 and chessboard_map[status[0]][row_z1] == "":
                move_map[status[0]][row_z1] = True
            elif rap == 0:
                rap = 1
            elif rap == 1 and judge_red_black((status[0],row_z1)) != "" and judge_red_black((status[0],row_z1)) != judge_red_black(status):
                move_map[status[0]][row_z1] = True
                rap = 0
                break
            elif rap == 1 and judge_red_black((status[0],row_z1)) == judge_red_black(status):
                rap = 0
                break
            row_z1 -= 1
    # 卒
    if type_piece == "b_z" or type_piece == "r_z":
        # 红黑判定
        if judge_red_black(status) == "black":
            if line_x1 == 4 or line_x1 == 5 and judge_red_black((line_x1,status[1])) != judge_red_black(status):
                move_map[line_x1][status[1]] = True
            else:
                # 下
                if line_x1 <= 9 and judge_red_black((line_x1,status[1])) != judge_red_black(status):
                    move_map[line_x1][status[1]] = True
                # 左
                if row_z1 >= 0 and judge_red_black((status[0],row_z1)) != judge_red_black(status):
                    move_map[status[0]][row_z1] = True
                # 右
                if row_y1 <= 8 and judge_red_black((status[0],row_y1)) != judge_red_black(status):
                    move_map[status[0]][row_y1] = True
        elif judge_red_black(status) == "red":
            if line_s1 == 4 or line_s1 == 5 and judge_red_black((line_s1,status[1])) != judge_red_black(status):
                move_map[line_s1][status[1]] = True
            else:
                # 上
                if line_s1 >= 0 and judge_red_black((line_s1,status[1])) != judge_red_black(status):
                    move_map[line_s1][status[1]] = True
                # 左
                if row_z1 >= 0 and judge_red_black((status[0],row_z1)) != judge_red_black(status):
                    move_map[status[0]][row_z1] = True
                # 右
                if row_y1 <= 8 and judge_red_black((status[0],row_y1)) != judge_red_black(status):
                    move_map[status[0]][row_y1] = True

# 判断对方的将是否在自己的攻击范围内
def is_jiang(status):
    global chessboard_map
    color = judge_red_black(status)
    i1 = 0
    while i1 < 10:
        y1 = 0
        while y1 < 9:
            if move_map[i1][y1]:
                if (color == "black" and chessboard_map[i1][y1] == "r_j" or color == "red" and chessboard_map[i1][y1] == "b_j"):
                    return True
            y1 += 1
        i1 += 1
    return False

# 绝杀判断
def kill(step1):
    list_r = []
    if step1 % 2 == 1:
        list_r = get_list("red",step1)
        if list_r == []:
            return True
    return False

# 判断是否存在将军对方的可能,传入本棋子位置
def jiang_ni(status):
    global chessboard_map
    color = judge_red_black(status)
    global move_map
    global step
    move_bak = copy_map(move_map)
    i1 = 0
    while i1 < 10:
        y1 = 0
        while y1 < 9:
            if step % 2 == 1 and color == "black" or step % 2 == 0 and color == "red":
                move_map = [[False for c in range(9)]for r in range(10)]
                draw_point_map((i1,y1))
                if is_jiang((i1,y1)):
                    move_map = copy_map(move_bak)
                    return True
            y1 += 1
        i1 += 1
    move_map = copy_map(move_bak)
    return False

def get_list(str1,depth):
    global chessboard_map
    global move_map
    list_now = []
    i1 = 0
    while i1 < 10:
        y1 = 0
        while y1 < 9:
            if judge_red_black((i1,y1)) == str1:
                draw_point_map((i1,y1))
                i = 0
                while i < 10:
                    y = 0 
                    while y < 9:
                        ok_now = move_ok((i1,y1), (i,y), depth)
                        # 对将或者被将
                        if ok_now == 0 or ok_now == 1 or ok_now == 2:
                            y += 1
                            continue
                        elif ok_now == 3:
                            list_now.append([i1,y1,i,y])
                        y += 1
                    i += 1
                move_map = [[False for c in range(9)]for r in range(10)]
            y1 += 1
        i1 += 1
    return list_now

# 获取路径的最终分值，传入参数为最后一次移动的路径
def get_score(list_1):
    global chessboard_map
    update_map((list_1[0], list_1[1]), (list_1[2], list_1[3]))
    score_b = 0
    score_r = 0
    i1 = 0
    while i1 < 10:
        y1 = 0
        while y1 < 9:
            if chessboard_map[i1][y1] == "b_c":
                score_b += content.pos_val[1][i1 * 9 + y1] * 8 + content.chessValue[4]
            elif chessboard_map[i1][y1] == "b_m":
                score_b += content.pos_val[2][i1 * 9 + y1] * 8 + content.chessValue[3]
            elif chessboard_map[i1][y1] == "b_x":
                score_b += content.chessValue[2]
            elif chessboard_map[i1][y1] == "b_s":
                score_b += content.chessValue[1]
            elif chessboard_map[i1][y1] == "b_j":
                score_b += content.chessValue[0]
            elif chessboard_map[i1][y1] == "b_p":
                score_b += content.pos_val[3][i1 * 9 + y1] * 8 + content.chessValue[5]
            elif chessboard_map[i1][y1] == "b_z":
                score_b += content.pos_val[0][i1 * 9 + y1] * 8 + content.chessValue[6]
            elif chessboard_map[i1][y1] == "r_c":
                score_r += content.pos_val[1][i1 * 9 + y1] * 8 + content.chessValue[4]
            elif chessboard_map[i1][y1] == "r_m":
                score_r += content.pos_val[2][i1 * 9 + y1] * 8 + content.chessValue[3]
            elif chessboard_map[i1][y1] == "r_x":
                score_r += content.chessValue[2]
            elif chessboard_map[i1][y1] == "r_s":
                score_r += content.chessValue[1]
            elif chessboard_map[i1][y1] == "r_j":
                score_r += content.chessValue[0]
            elif chessboard_map[i1][y1] == "r_p":
                score_r += content.pos_val[3][i1 * 9 + y1] * 8 + content.chessValue[5]
            elif chessboard_map[i1][y1] == "r_z":
                score_r += content.pos_val[0][i1 * 9 + y1] * 8 + content.chessValue[6]
            y1 += 1
        i1 += 1
    update_map((list_1[2], list_1[3]), (list_1[0], list_1[1]))
    return score_b - score_r

jian = -1
map_bak_2 = []
map_bak_3 = []
# 递归计算Alpha, Beta值
def AlphaBeta(depth, Alpha, Beta, list, num):
    global jian
    global map_bak_2
    global map_bak_3
    global max_depth
    global chessboard_map
    if depth <= 1:
        map_bak = copy_map(chessboard_map)
    elif depth == 2:
        map_bak_2 = copy_map(chessboard_map)
    elif depth == 3:
        map_bak_3 = copy_map(chessboard_map)
    
    if depth != 0:
        update_map((list[num][0], list[num][1]), (list[num][2], list[num][3]))
        
    if depth % 2 == 0:
        list_1 = get_list("black",depth)
    else :
        list_1 = get_list("red",depth)
    # 判断是否为根节点
    if depth == max_depth - 1:
        i = 0
        while i < len(list_1):
            score = get_score(list_1[i])
            if Beta > score:
                Beta = score
            if Alpha >= Beta:
                break
            i += 1
        return [Alpha, Beta]
    num = 0
    while num < len(list_1):
        # 返回一个列表内容为alpha, beta值
        depth += 1
        result = AlphaBeta(depth, Alpha, Beta, list_1, num)
        depth -= 1
        if depth % 2 == 0:
            if depth == 0 and Alpha < max(result):
                way.clear()
                way.append(list_1[num])
            Alpha = max(Alpha, max(result))
            if Alpha >= Beta:
                num = len(list_1)
                if depth == 2:
                    jian = 2
        else:
            Beta = min(Beta, min(result))
            if Alpha >= Beta:
                num = len(list_1)
                if depth == 1:
                    jian = 1
        num += 1
        if depth == 0 or jian == 1:
            chessboard_map = copy_map(map_bak)
        elif depth == 1 or jian == 2:
            chessboard_map = copy_map(map_bak_2)
        elif depth == 2:
            chessboard_map = copy_map(map_bak_3)
        jian = -1
    return [Alpha, Beta]

def computer_go():
    start_time = time.time()
    AlphaBeta(0, min_val, max_val, [], 0)
    end_time = time.time()
    print("时间：")
    print(end_time-start_time)
    # 电脑已输
    if way == way_before:
        end = 1
    else:
        # 绘制电脑路径
        rect_before[0] = way[0][0]
        rect_before[1] = way[0][1]
        rect[0] = way[0][2]
        rect[1] = way[0][3]
        end = 0
        if chessboard_map[way[0][2]][way[0][3]] != "":
            eat.play()
        update_map((way[0][0],way[0][1]), (way[0][2],way[0][3]))
        step += 1
        way_before = [way[0][0], way[0][1], way[0][2], way[0][3]]

# 程序主循环
ok_flag = 3
# 用来标识棋子是否被点击
monitor = 0
# 用来记录所走步数,同为1则红色方先走，同为0则黑色方先走
step = 1
step_before = 1
# 判断两次点击颜色是否相同
tong = 0
# 将军标志位
jiangjun = False
# 对将标志位
duijiang = False
while True:
    # 事件检测（例如点击了键盘、鼠标等）
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            pygame.quit()
            sys.exit()  # 退出程序
        elif event.type == pygame.VIDEORESIZE:
            size = width, height = event.size[0], event.size[1]  # 获取新的size
            screen = pygame.display.set_mode(size, pygame.RESIZABLE)
        # 获得鼠标按下的位置
        if event.type == pygame.MOUSEBUTTONDOWN:
            if end != 0 or event.pos[0] <= 100 or event.pos[0] >= 596 or event.pos[1] <= 53 or event.pos[1] >= 606:
                break
            # 返回鼠标点击的位置
            status = get_status(event.pos)
            # 返回黑色或者红色或者空
            judge = judge_red_black(status)
            # 选中棋子
            if judge != "":
                if monitor == 1:
                    # 判断棋子是否可走
                    if step % 2 == 0 and judge_before == "black" or step % 2 == 1 and judge_before == "red":
                        ok_flag = move_ok(status_before, status, step)
                        # 正常
                        if ok_flag == 3:
                            if chessboard_map[status[0]][status[1]] != "":
                                eat.play()
                            update_map(status_before,status)
                            monitor = 0
                            step_before = step
                            step += 1
                        # 对将或者被将
                        elif ok_flag == 2 or ok_flag == 1:
                            move_map = [[False for c in range(9)]for r in range(10)]
                            status_before = status
                            judge_before = judge
                            monitor = 1
                        # 两次点击的颜色相同
                        elif judge_before == judge:
                            status_before = status
                            judge_before = judge
                            monitor = 1
                            tong = 1
                        else:
                            break
                else:
                    status_before = status
                    judge_before = judge
                    monitor = 1
            # 没选中棋子
            elif monitor == 1:
                # 判断棋子是否可走
                if step % 2 == 0 and judge_before == "black" or step % 2 == 1 and judge_before == "red":
                    ok_flag = move_ok(status_before, status, step)
                    if ok_flag == 3:
                        if chessboard_map[status[0]][status[1]] != "":
                            eat.play()
                        update_map(status_before,status)
                        monitor = 0
                        step_before = step
                        step += 1
                    else:
                        break
            status_before = status
            # 设置棋子周围边框数据
            if step % 2 == 0 and judge_before == "black" or step % 2 == 1 and judge_before == "red" or step_before != step:
                if chessboard_map[status[0]][status[1]] != "":
                    select.play()
                    rect[0] = status[0]
                    rect[1] = status[1]
                step_before = step
            
            if monitor == 0 or tong == 1:
                # 检测是否将军了对方
                if monitor == 0:
                    if jiang_ni(status):
                        jiangjun = True
                    else :
                        jiangjun = False
                move_map = [[False for c in range(9)]for r in range(10)]
                tong = 0
            # 判断是否需要更新模板
            if monitor == 1:
                if step % 2 == 0 and judge == "black" or step % 2 == 1 and judge == "red":
                    draw_point_map(status)
                else :
                    monitor = 0
            
    
    # 显示游戏背景
    screen.blit(pygame.transform.smoothscale(background_img, size), (0, 0))
    # 显示棋盘
    screen.blit(chessboard_img, (100, 50))
    # 显示字体
    myfont=pygame.font.Font('fonts/SimHei.ttf',30)
    if step % 2 == 0:
        text = myfont.render("黑色方请下棋", True, RED, None)
    else :
        text = myfont.render("红色方请下棋", True, RED, None)
    screen.blit(text, (650, 50))
    # 被困不能移动
    if ok_flag == 2:
        text2 = myfont.render("不能移动，不然你会输", True, RED, None)
        screen.blit(text2, (650, 90))
    # 将军警告
    if jiangjun:
        text1 = myfont.render("将军", True, RED, None)
        screen.blit(text1, (650, 130))
    # 两将相对
    if ok_flag == 1:
        text3 = myfont.render("不能对将", True, RED, None)
        screen.blit(text3, (650, 170))
    # 结束
    if end == 1:
        txt = myfont.render("黑方输", True, RED, None)
        screen.blit(txt, (650, 210))
    elif end == 2:
        txt = myfont.render("红方输", True, RED, None)
        screen.blit(txt, (650, 210))
    # 显示棋子
    x = 0
    for line in chessboard_map:
        y = 0
        for chess_name in line:
            if chess_name != "":
                img_board = pygame.image.load("imgs/s1/" + chess_name + ".png")
                screen.blit(img_board, (100 + y * 57, 50 + x * 57))
            y += 1
        x += 1
    # 显示可移动路径
    x = 0
    for line in move_map:
        y = 0
        for chess_name in line:
            if move_map[x][y]:
                pygame.draw.circle(screen,GREEN,(121 + y * 57, 74 + x * 57),5,5)
            y += 1
        x += 1
    # 绘制棋子周围方框
    pygame.draw.line(screen, BLUE, (100 + rect[1] * 57, 50 + rect[0] * 57), (110 + rect[1] * 57, 50 + rect[0] * 57), 3)
    pygame.draw.line(screen, BLUE, (140 + rect[1] * 57, 50 + rect[0] * 57), (150 + rect[1] * 57, 50 + rect[0] * 57), 3)
    pygame.draw.line(screen, BLUE, (100 + rect[1] * 57, 50 + rect[0] * 57), (100 + rect[1] * 57, 60 + rect[0] * 57), 3)
    pygame.draw.line(screen, BLUE, (100 + rect[1] * 57, 90 + rect[0] * 57), (100 + rect[1] * 57, 100 + rect[0] * 57), 3)
    pygame.draw.line(screen, BLUE, (100 + rect[1] * 57, 100 + rect[0] * 57), (110 + rect[1] * 57, 100 + rect[0] * 57), 3)
    pygame.draw.line(screen, BLUE, (140 + rect[1] * 57, 100 + rect[0] * 57), (150 + rect[1] * 57, 100 + rect[0] * 57), 3)
    pygame.draw.line(screen, BLUE, (150 + rect[1] * 57, 50 + rect[0] * 57), (150 + rect[1] * 57, 60 + rect[0] * 57), 3)
    pygame.draw.line(screen, BLUE, (150 + rect[1] * 57, 90 + rect[0] * 57), (150 + rect[1] * 57, 100 + rect[0] * 57), 3)

    pygame.draw.line(screen, BLUE, (100 + rect_before[1] * 57, 50 + rect_before[0] * 57), (110 + rect_before[1] * 57, 50 + rect_before[0] * 57), 3)
    pygame.draw.line(screen, BLUE, (140 + rect_before[1] * 57, 50 + rect_before[0] * 57), (150 + rect_before[1] * 57, 50 + rect_before[0] * 57), 3)
    pygame.draw.line(screen, BLUE, (100 + rect_before[1] * 57, 50 + rect_before[0] * 57), (100 + rect_before[1] * 57, 60 + rect_before[0] * 57), 3)
    pygame.draw.line(screen, BLUE, (100 + rect_before[1] * 57, 90 + rect_before[0] * 57), (100 + rect_before[1] * 57, 100 + rect_before[0] * 57), 3)
    pygame.draw.line(screen, BLUE, (100 + rect_before[1] * 57, 100 + rect_before[0] * 57), (110 + rect_before[1] * 57, 100 + rect_before[0] * 57), 3)
    pygame.draw.line(screen, BLUE, (140 + rect_before[1] * 57, 100 + rect_before[0] * 57), (150 + rect_before[1] * 57, 100 + rect_before[0] * 57), 3)
    pygame.draw.line(screen, BLUE, (150 + rect_before[1] * 57, 50 + rect_before[0] * 57), (150 + rect_before[1] * 57, 60 + rect_before[0] * 57), 3)
    pygame.draw.line(screen, BLUE, (150 + rect_before[1] * 57, 90 + rect_before[0] * 57), (150 + rect_before[1] * 57, 100 + rect_before[0] * 57), 3)

    if monitor == 1:
        rect_before[0] = rect[0]
        rect_before[1] = rect[1]
    # 绘制屏幕内容
    pygame.display.update()
    pygame.display.flip()

    if step % 2 == 0:
        computer_go()