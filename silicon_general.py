import subprocess as sub
import os
from PIL import Image
import shutil
import pprint
import time
import cv2
import matplotlib.pyplot as plt
import numpy as np
import sys


def move_file(files, from_path, to_path):
    for name in files:
        from_file = os.path.join(from_path, name)
        to_file = os.path.join(to_path, name)
        shutil.move(from_file, to_file)


def get_target_file(dir_path, target):
    return [path for path in os.listdir(dir_path) if target in path]


def get_ex_file(dir_paht, ex):
    return [path for path in os.listdir(dir_path) if path.endswith(ex)]


def make_or_cont(path):
    if os.path.exists(path) == False:
        os.makedirs(path)
    else:
        return


def trim_photo(path, X, Y):
    div = 70  # しきい値
    img = cv2.imread(path, 0)
    size = (X, Y)
    img_resize = cv2.resize(img, size)
    ret, thresh = cv2.threshold(img_resize, div, 255, 0)
    thresh = cv2.bitwise_not(thresh)  # 反転
    mask = np.zeros_like(img_resize)
    contours, hierarchy = cv2.findContours(
        thresh, cv2.RETR_CCOMP, cv2.CHAIN_APPROX_SIMPLE)
    out = np.zeros_like(img_resize)
    out[mask == 255] = img_resize[mask == 255]
    min_x, max_x, min_y, max_y = photo_range(img_resize, X, Y, contours)
    left_rate = 0.7
    right_rate = 0.7
    top_rate = 0.4
    under_rate = 0.4
    result = img_resize[min_y - int(min_y * top_rate):max_y + int(under_rate * (Y - max_y)),
                        min_x - int(min_x * left_rate):max_x + int(right_rate * (X - max_x))]
    return result


def photo_range(path, X, Y):
    div = 50  # しきい値
    # siliconを扱うなら50がいいしきい値化もしれない
    img = cv2.imread(path, 0)
    size = (X, Y)
    img_resize = cv2.resize(img, size)
    ret, thresh = cv2.threshold(img_resize, div, 255, 0)
    thresh = cv2.bitwise_not(thresh)  # 反転
    mask = np.zeros_like(img_resize)
    contours, hierarchy = cv2.findContours(
        thresh, cv2.RETR_CCOMP, cv2.CHAIN_APPROX_SIMPLE)
    min_x = X
    max_x = 0
    min_y = Y
    max_y = 0
    for i in range(0, len(contours)):
        x, y, w, h = cv2.boundingRect(contours[i])
        min_x = min(min_x, x)
        min_y = min(min_y, y)
        max_x = max(max_x, x)
        max_y = max(max_y, y)
    return min_x, max_x, min_y, max_y


#dirlist = sub.Popen(dir, shell=True)
print('プログラム実行')
print(' ')
back = '..'

args = sys.argv
dir_path = args[1]
extension = args[2]
phto_exe = '.png'  # 変換する画像の拡張子
remove_ex = '_remove.png'  # トリミングした後につける名前
files = get_ex_file(dir_path, extension)
print(files, '\n')
ne1 = 'code_photo'  # コードをシリコンで画像にした物を保存するフォルダ1
ne2 = 'original'  # シリコンで画像にした物を保存するフォルダ
ne3 = 'remove'  # トリミングした画像を保存するフォルダ
X = 1600  # リサイズの値
Y = 900  # リサイズの値
tmp = os.path.join(dir_path, ne1)  # コードを画像にして保存する入り口に指定
make_or_cont(tmp)

dir_path_2 = os.path.join(tmp, ne2)  # シリコンで画像にしたものを入れておくディレクトリ
make_or_cont(dir_path_2)

for name in files:
    os.chdir(dir_path)
    name_list = []
    if extension == '.ino':
        name_list.append(name)
        extension = extension.replace('.ino', '.cpp')
        # print(extension)
        dir_name = os.path.join(dir_path, name)
        name = name.replace('.ino', extension)
        # print(to_name)
        shutil.copy(dir_name, name)
    im = name.replace(extension, phto_exe)
    to_silicon = 'silicon ' + name + ' -o ' + im
    sub.Popen(to_silicon.split())  # 　シリコンを実行

sleep_time = 0.1 * len(files)  # ある程度待たないと全てのファイルを検出できない
time.sleep(sleep_time)
# 画像ファイルのリストを取得
image_list = get_ex_file(dir_path, phto_exe)
# print('image_list:', image_list)
move_file(image_list, dir_path, dir_path_2)
# print('os.curdir:', os.curdir)
# トリミング処理
dir_path_3 = os.path.join(tmp, ne3)
make_or_cont(dir_path_3)

for im in image_list:
    os.chdir(dir_path_2)
    # print('dir_path_2:', dir_path_2)
    # print('os.getcwd:', os.getcwd())

    left_rate = 0.7
    right_rate = 0.7
    top_rate = 0.7
    under_rate = 0.7

    img_n = os.path.join(dir_path_2, im)
    time.sleep(sleep_time)
    rex = 1600  # リサイズのxの値
    rey = 900  # リサイズのyの値
    x_mi, x_ma, y_mi, y_ma = photo_range(im, rex, rey)
    im_name = Image.open(im)
    im_resize = im_name.resize((rex, rey))
    x = [x_mi, x_ma]
    y = [y_mi, y_ma]
    left = x_mi * left_rate
    right = rex - x_mi * right_rate
    top = y_mi * top_rate
    under = rey - y_mi * under_rate
    im_crop = im_resize.crop((left, top,  right, under))
    # im_crop = trim_photo(img_n, rex, rey)
    # rows,cols,chs = im_crop.shape
    save_name = im.replace(phto_exe, remove_ex)
    im_crop.save(save_name, quality=95)
    # cv2.imwrite(save_name, im_crop)
removes = get_target_file(dir_path_2, remove_ex)
print(removes)
move_file(removes, dir_path_2, dir_path_3)
