import ctypes
from os import system
from time import time, sleep
from threading import Thread

try:
  import numpy as np
except ModuleNotFoundError:
  system('py -m pip install numpy')
  import numpy as np
# todo:音
class Tetris:
  DEBUG = False
  WIN10 = False
  T_SPIN = False
  SPF = 1 / 60  # 1 / FPS
  X_LEN = 10 + 2  # 横の長さ + 左右の番兵
  Y_LEN = 20 + 4 + 1  # 縦の長さ + 上部のゆとり + 下端の番兵
  mino = {
    'I': [[0, 0, 0, 0],
          [1, 1, 1, 1]],
    'O': [[0, 2, 2, 0],
          [0, 2, 2, 0]],
    'S': [[0, 3, 3, 0],
          [3, 3, 0, 0]],
    'Z': [[4, 4, 0, 0],
          [0, 4, 4, 0]],
    'J': [[5, 0, 0, 0],
          [5, 5, 5, 0]],
    'L': [[0, 0, 6, 0],
          [6, 6, 6, 0]],
    'T': [[0, 7, 0, 0],
          [7, 7, 7, 0]]
  }
  mino_num = {
    'I': 1,
    'O': 2,
    'S': 3,
    'Z': 4,
    'J': 5,
    'L': 6,
    'T': 7
  }

  def __init__(self):
    # mapの初期化
    self.map = np.full((Tetris.Y_LEN, Tetris.X_LEN), -1, int)
    self.map[:Tetris.Y_LEN - 1, 1:Tetris.X_LEN - 1] = 0
    self.original = np.array([])
    if Tetris.T_SPIN:
      if Tetris.T_SPIN == 1:  # single mini
        self.map[Tetris.Y_LEN - 3:Tetris.Y_LEN - 1, 4:Tetris.X_LEN - 1] = 9
        self.map[Tetris.Y_LEN - 3][3] = 9
      elif Tetris.T_SPIN == 2:  # double
        self.map[Tetris.Y_LEN - 4:Tetris.Y_LEN - 1, 3:Tetris.X_LEN - 1] = 9
        self.map[Tetris.Y_LEN - 2][1] = 9
        self.map[Tetris.Y_LEN - 3][3] = 0
      elif Tetris.T_SPIN == 3:  # triple
        self.map[Tetris.Y_LEN - 6:Tetris.Y_LEN - 1, 1:Tetris.X_LEN - 1] = 9
        self.map[Tetris.Y_LEN - 6:Tetris.Y_LEN - 4, 1:3] = 0
        self.map[Tetris.Y_LEN - 5:Tetris.Y_LEN - 1, 3] = 0
        self.map[Tetris.Y_LEN - 3][2] = 0

    # HOLDとNEXT
    self.hold = str()
    self.next = list()
    if Tetris.T_SPIN:
      self.next += ['T']
      self.next += ['T']

    # 動いているミノの属性
    self.moving_mino = str()
    self.angle = 0

    # 共有のフラグ
    self.continue_play = True
    self.lock = False
    self.can_move = False
    self.can_hold = True
    self.keep_left_right = False
    self.keep_down = False
    self.lower_move_times = 0

    # 表示する値
    self.score = 0
    self.level = 0
    self.lines = 0

    # 変動する時間
    self.sleep_time = 0.8
    self.space_time = 0.5


  def screen(self, map_array):
    system('cls')
    if Tetris.WIN10:
      for i, line in enumerate(map_array[4:]):
        if i == 0:
          print('┌ ─ HOLD─ ┐ ', end='')
        elif i in {1, 2}:
          print('│ ', end='')
          if self.hold in Tetris.mino:
            for pixel in Tetris.mino[self.hold][i - 1]:
              print('□' if pixel else '  ', end='')
          else:
            print(' ' * 8, end='')
          print('│ ', end='')
        elif i == 3:
          print('└ ─ ─ ─ ─ ┘ ', end='')
        elif i == 4:
          print(f'SCORE:{self.score:>6}', end='')
        elif i == 5:
          print(f'LEVEL:{self.level:>6}', end='')
        elif i == 6:
          print(f'LINES:{self.lines:>6}', end='')
        else:
          print(' ' * 12, end='')

        for pixel in line:
          if pixel < 0: print('■', end='')
          elif pixel > 0: print('□', end='')
          else: print('  ', end='')

        if i > 18:
          print()
        elif i == 0:
          print('┌ ─ NEXT─ ┐ ')
        elif i % 3:
          print('│ ', end='')
          for pixel in Tetris.mino[self.next[:][i // 3]][(i + 1) % 2]:
            print('□' if pixel else '  ', end='')
          print('│ ')
        elif i < 18:
          print('├ ─ ─ ─ ─ ┤ ')
        else:
          print('└ ─ ─ ─ ─ ┘ ')
    else:
      for i, line in enumerate(map_array[4:]):
        if i == 0:
          print('┌─HOLD─┐', end='')
        elif i in {1, 2}:
          print('│', end='')
          if self.hold in Tetris.mino:
            for pixel in Tetris.mino[self.hold][i - 1]:
              print('□' if pixel else '  ', end='')
          else:
            print(' ' * 8, end='')
          print('│', end='')
        elif i == 3:
          print('└────┘', end='')
        elif i == 4:
          print(f'SCORE:{self.score:>6}', end='')
        elif i == 5:
          print(f'LEVEL:{self.level:>6}', end='')
        elif i == 6:
          print(f'LINES:{self.lines:>6}', end='')
        else:
          print(' ' * 12, end='')

        for pixel in line:
          if pixel < 0: print('■', end='')
          elif pixel > 0: print('□', end='')
          else: print('  ', end='')

        if i > 18:
          print()
        elif i == 0:
          print('┌─NEXT─┐')
        elif i % 3:
          print('│', end='')
          for pixel in Tetris.mino[self.next[:][i // 3]][(i + 1) % 2]:
            print('□' if pixel else '  ', end='')
          print('│')
        elif i < 18:
          print('├────┤')
        else:
          print('└────┘')


  def display(self, delete=False):
    func = print if Tetris.DEBUG else self.screen
    if delete:
      for i in range(3):  # 消去時のチカチカ
        if i % 2: func(self.original)
        else: func(self.map)
        sleep(0.15)
    else:
      func(self.map)


  def judge_move(self, direction=1):
    dir_move = [0, 1, 0, -1]
    now_map = self.map.copy()
    mino_pos_list = np.array(list(zip(
      *np.where(now_map == Tetris.mino_num[self.moving_mino])
    )))

    for mino_pos in mino_pos_list:
      moved_y, moved_x = mino_pos + dir_move[direction:direction + 2]
      if self.map[moved_y][moved_x] != 0 and\
         self.map[moved_y][moved_x] != Tetris.mino_num[self.moving_mino]:
        return False, now_map
      else:
        now_map[moved_y][moved_x] = 16

    now_map = np.where(
      now_map == Tetris.mino_num[self.moving_mino],
      0, now_map
    )
    now_map = np.where(
      now_map == 16,
      Tetris.mino_num[self.moving_mino], now_map
    )
    return True, now_map


  def judge_lower_end(self):
    lower_end = not(self.judge_move()[0])
    return lower_end


  def srs(self, i, times, rotated_angle):
    if self.moving_mino == 'I':
      if i == 1:
        if rotated_angle == 0:
          self.srs_x = -times * 2
        elif rotated_angle == 2:
          self.srs_x = -times
        else:
          if self.angle + rotated_angle == 3:
            self.srs_x = 1
          else:
            self.srs_x = 2
          if self.angle == 0:
            self.srs_x *= -1
        self.srs1 = self.srs_y, self.srs_x

      elif i == 2:
        if rotated_angle == 0:
          self.srs_x = times
        elif rotated_angle == 2:
          self.srs_x = times * 2
        elif self.angle == 0:
          self.srs_x += 3
        else:
          self.srs_x -= 3
        self.srs2 = self.srs_y, self.srs_x

      elif i == 3:
        if times + 1:  # 右回転
          move_times = 1
        else:
          move_times = 2
        if rotated_angle == 1:
          self.srs_y, self.srs_x = self.srs1
          self.srs_y -= move_times
        elif rotated_angle == 1:
          self.srs_y, self.srs_x = self.srs1
          self.srs_y += move_times
        elif self.angle == 1:
          self.srs_y, self.srs_x = self.srs1
          self.srs_y += move_times
        else:
          self.srs_y, self.srs_x = self.srs2
          self.srs_y -= move_times

      else:
        if times + 1:  # 右回転
          move_times = 2
        else:
          move_times = 1
        if rotated_angle == 1:
          self.srs_y, self.srs_x = self.srs2
          self.srs_y += move_times
        elif rotated_angle == 3 or self.angle == 3:
          self.srs_y, self.srs_x = self.srs2
          self.srs_y -= move_times
        elif self.angle == 1:
          self.srs_y, self.srs_x = self.srs1
          self.srs_y += move_times

    else:
      if i == 1:
        self.srs_y = 0
        if rotated_angle == 1:
          self.srs_x = -1
        elif rotated_angle == 3:
          self.srs_x = 1
        else:
          self.srs_x = -times

      elif i == 2:
        if rotated_angle % 2:
          self.srs_y += 1
        else:
          self.srs_y -= 1

      elif i == 3:
        self.srs_x = 0
        if rotated_angle % 2:
          self.srs_y = -2
        else:
          self.srs_y = 2

      else:
        if rotated_angle == 1:
          self.srs_x -= 1
        elif rotated_angle == 3:
          self.srs_x += 1
        else:
          self.srs_x -= times


  def do_hold(self):
    while self.lock: sleep(Tetris.SPF)
    if not self.can_hold: return
    self.lock = True

    self.map = np.where(
      self.map == Tetris.mino_num[self.moving_mino],
      0, self.map
    )
    if self.hold in Tetris.mino:
      self.hold, self.moving_mino = self.moving_mino, self.hold
      self.put_mino(False)
      self.can_hold = False
    else:
      self.hold = self.moving_mino
      self.put_mino()
      self.can_hold = False
      self.lock = False


  def rotate(self, times):
    while self.lock: sleep(Tetris.SPF)
    if not self.can_move: return
    if self.moving_mino == 'O': return
    self.lock = True
    self.original = self.map.copy()

    angle_move = np.array(
      [[0, 1],
       [-1, -1],
       [1, 0],
       [0, 0]]
    ) * times
    rotated_angle = (self.angle + times) % 4
    if times + 1:  # 右回転
      select_angle = self.angle
    else:  # 左回転
      select_angle = rotated_angle
    if self.moving_mino == 'I':
      if select_angle % 2:
        angle_move -= times
      else:
        angle_move += times

    mino_pos = np.array(list(zip(
      *np.where(self.map == Tetris.mino_num[self.moving_mino])
    )))
    min_y, min_x = mino_pos.min(axis=0)
    max_y, max_x = mino_pos.max(axis=0)
    y_size, x_size = max_y - min_y + 1, max_x - min_x + 1

    clip_mino = self.map[min_y:max_y + 1, min_x:max_x + 1]
    clip_mino = np.where(
      clip_mino == Tetris.mino_num[self.moving_mino],
      clip_mino, 0
    )
    clip_mino = np.rot90(clip_mino, -times)
    self.map = np.where(
      self.map == Tetris.mino_num[self.moving_mino],
      0, self.map
    )
    self.map = np.where(
      self.map == 0,
      0, -1
    )

    adjust_y, adjust_x = angle_move[select_angle]
    min_y -= adjust_y
    min_x += adjust_x

    for i in range(5):
      if i == 0:
        self.srs_y = self.srs_x = 0
      else:
        self.srs(i, times, rotated_angle)
      top = min_y - self.srs_y
      left = min_x + self.srs_x
      rotate_map = self.map[top:top + x_size, left:left + y_size]
      if rotate_map.size != clip_mino.size:
        continue
      if np.all(rotate_map * clip_mino == 0):
        self.map = self.original
        self.map = np.where(
          self.map == Tetris.mino_num[self.moving_mino],
          0, self.map
        )
        self.map[top:top + x_size, left:left + y_size] += clip_mino
        self.angle = rotated_angle
        self.lock = False
        self.display()
        return True
    else:
      self.map = self.original
      self.lock = False
      return False


  def move(self, direction=1, auto_proc=True):
    while self.lock: sleep(Tetris.SPF)
    if not self.can_move: return False
    self.lock = True
    self.original = self.map.copy()

    if direction == 3:
      result = False
      while True:
        can_move, self.map = self.judge_move()
        if can_move:
          self.original = self.map.copy()
          result = True
          self.score += 2
        else: break
      self.map = self.original
      self.lock = False
      self.can_move = False
      self.can_hold = False
      self.display()
      return result

    else:
      can_move, self.map = self.judge_move(direction)
      if can_move:
        if direction == 1:
          self.score += 1
        self.lock = False
        self.display()
      else:
        if direction == 1 and not(self.keep_down):  # 下端で下キー入力時遊び時間をスキップする処理
          self.can_move = False
          self.can_hold = False
          add_rate = 0
        self.map = self.original
        self.lock = False
      if auto_proc:
        start_time = time()
        add_rate = 1
        tmp = 0
        while self.judge_lower_end():
          sleep(Tetris.SPF)
          if self.keep_left_right: add_rate = 1.25
          if (time() - start_time) >= (self.space_time * add_rate):
            if self.judge_lower_end() and tmp == self.lower_move_times:
              self.can_move = False
              self.can_hold = False
              break
          if self.lower_move_times >= 15:
            if self.judge_lower_end():
              self.can_move = False
              self.can_hold = False
              break
          if tmp != self.lower_move_times:
            tmp = self.lower_move_times
            start_time = time()
      return can_move


  def put_mino(self, use_pop=True):
    while len(self.next[:]) < 7:
      self.next[:] += np.random.permutation(list(Tetris.mino)).tolist()

    if use_pop:
      self.moving_mino = self.next.pop(0)
    else:
      self.moving_mino = self.moving_mino
    self.angle = 0

    put_was_space = self.map[2:4, 4:8] + Tetris.mino[self.moving_mino]

    self.continue_play = np.all(put_was_space <= Tetris.mino_num[self.moving_mino])
    if self.continue_play:
      self.map[2:4, 4:8] = put_was_space
      self.display()
      self.lock = False
      self.can_move = True
      self.can_hold = True
      self.lower_move_times = 0
      sleep(self.sleep_time)
    else:
      self.next.insert(0, self.moving_mino)


  def delete_line(self):
    self.original = self.map.copy()
    self.map = np.where(
      self.map == Tetris.mino_num[self.moving_mino],
      Tetris.mino_num[self.moving_mino] + 8, self.map
    )
    del_list = np.array(list(zip(
      np.where(np.prod(self.map[:-1], axis=1) != 0)
    ))).ravel()

    if len(del_list):
      for index in del_list:
        self.map[index] = np.where(self.map[index] > 0, 0, self.map[index])
      self.display(delete=True)

      if len(del_list) == 4:
        self.score += 800 * (self.level + 1)
      elif len(del_list) == 3 and self.moving_mino == 'T':  # t-spin triple
        self.score += 1600 * (self.level + 1)
      else:
        self.score += (2 * len(del_list) - 1) * 100 * (self.level + 1)

      for del_index in del_list:
        self.lines += 1
        if self.lines % 10 == 0:
          self.level += 1
          if self.level < 9:
            self.sleep_time -= 1 / 12
          elif self.level == 9:
            self.sleep_time -= 1 / 30
          elif self.level in {10, 13, 16, 19, 29}:
            self.sleep_time -= 1 / 60
          self.space_time = self.sleep_time / 4 + 0.25

        for i, line in enumerate(self.map[:del_index][::-1]):
          self.map[del_index - i] = line

    moved_mino_pos = np.array(list(zip(
      *np.where(self.map == Tetris.mino_num[self.moving_mino])
    )))
    if len(moved_mino_pos):
      for y, _ in moved_mino_pos:
        if y > 3: break
      else: self.continue_play = False


  def gameover(self):
    for i, line in enumerate(self.map[::-1]):  # gameover時の演出
      sleep(0.05)
      self.map[Tetris.Y_LEN - i - 1] = np.where(line > 0, -1, line)
      self.display()
    self.end()


  def end(self):
    print('game over!')
    sleep(3)


  def play(self):
    while self.continue_play:
      self.put_mino()
      while self.can_move:
        self.move()
        if self.can_move: sleep(self.sleep_time)
      self.delete_line()
    self.gameover()


  def input_ky(self):
    move_ky = {  # 移動(右, 下, 左, 即着地)
      68: 0, 83: 1, 65: 2, 87: 3,  # dsaw
      39: 0, 40: 1, 37: 2, 38: 3,  # 矢印キー(MPKH)
      32: 3,  # space
    }
    left_right_set = {  # 左右移動
      68, 65, 39, 37,
    }
    down_set = {  # 下移動
      83, 40,
    }
    rotate_ky = {  # 回転(左, 右)
      74: -1, 75: 1,  # j, k
      90: -1, 88: 1,  # z, x
      81: -1, 69: 1,  # q, e
    }
    hold_ky = {  # ホールド
      70, 72, 67,  # f, h, c
    }
    key_list = list(move_ky.keys() | rotate_ky.keys() | hold_ky)
    push_dic = dict()
    keep_dic = dict()
    push = False
    for key in move_ky.keys() | rotate_ky.keys():
      push_dic[key] = keep_dic[key] = False
    input_sleep = 0

    while self.continue_play:
      key_list.reverse()
      sleep(input_sleep)
      for key in key_list:
        if not(ctypes.windll.user32.GetAsyncKeyState(key) in {1, 0}):
          if key in move_ky:
            push_dic[key] = True
            if key in left_right_set:  # 左右入力
              moved = self.move(move_ky[key], False)
              if moved and self.judge_lower_end():
                self.lower_move_times += 1
              if keep_dic[key]:
                input_sleep = 0.05
              else:
                input_sleep = 0.3
                keep_dic[key] = True
                self.keep_left_right = True
            elif move_ky[key] == 1:  # 下入力
              self.move(move_ky[key], False)
              self.keep_down = True
              input_sleep = self.sleep_time / 20
            else:  # 上入力
              if not keep_dic[key]:
                self.move(move_ky[key], False)
                keep_dic[key] = True

          elif key in rotate_ky:
            push_dic[key] = True
            if not keep_dic[key]:
              rotated = self.rotate(rotate_ky[key])
              if rotated and self.judge_lower_end():
                self.lower_move_times += 1
              input_sleep = 0
              keep_dic[key] = True

          elif key in hold_ky:
            self.do_hold()

      for key in down_set:
        if push_dic[key]: break
      else: self.keep_down = False

      for key in left_right_set:
        if push_dic[key]: break
      else: self.keep_left_right = False

      if not self.judge_lower_end():
        self.lower_move_times = 0

      for key in push_dic:
        if push_dic[key]:
          push = True
          push_dic[key] = False
        else:
          keep_dic[key] = False

      if push: push = False
      else: input_sleep = 0


  def start(self):
    play_th = Thread(target=self.play, daemon=False)
    input_th = Thread(target=self.input_ky, daemon=True)
    play_th.start()
    input_th.start()
    play_th.join()


def main():
  tetris = Tetris()
  tetris.start()


if __name__ == '__main__':
  while True:
    main()
