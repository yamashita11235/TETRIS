from os import system
from threading import Thread
from itertools import product

try:
  import PySimpleGUI as sg
except ModuleNotFoundError:
  system('py -m pip install PySimpleGUI')
  import PySimpleGUI as sg

from TETRIS import Tetris

sg.theme('DarkBlue')

class Tetris_gui(Tetris):
  SIDE_LEN = 30
  LINE_WIDTH = 2
  PAD_RATE = 0.2
  mini_canvas_pad = (-SIDE_LEN * PAD_RATE), (-SIDE_LEN * PAD_RATE)
  mini_canvas_size = SIDE_LEN * (4 + PAD_RATE), SIDE_LEN * (2 + PAD_RATE)
  canvas_size = SIDE_LEN * (Tetris.X_LEN - 2), SIDE_LEN * (Tetris.Y_LEN - 5 + PAD_RATE)
  num_color = {
    -1: ('gray45', 'gray30'),  # gameover
    1: ('cyan', 'cyan3'),  # I
    2: ('yellow', 'goldenrod1'),  # O
    3: ('green1', 'green3'),  # S
    4: ('red', 'red4'),  # Z
    5: ('blue3', 'blue4'),  # J
    6: ('DarkOrange', 'DarkOrange3'),  # L
    7: ('dark orchid', 'DarkOrchid4'),  # T
    0: ('black', 'black'),  # 空白
  }
  figures = dict()

  def __init__(self):
    super().__init__()
    self.can_record = True
    self.window = self.create_window()
    self.centerG_buf = [[-1 for _ in range(Tetris.X_LEN - 2)] for _ in range(Tetris.Y_LEN - 4)]
    self.leftG_buf = [[-1 for _ in range(4)] for _ in range(2)]
    self.rightG_buf = list()
    for _ in range(6):
      self.rightG_buf += [[[-1 for _ in range(4)] for _ in range(2)]]


  def create_window(self):
    left_frame = sg.Frame(
      title='',
      layout=[
        [sg.T('HOLD', expand_x=True, justification='center')],
        [sg.G(
          canvas_size=Tetris_gui.mini_canvas_size,
          graph_bottom_left=Tetris_gui.mini_canvas_pad,
          graph_top_right=Tetris_gui.mini_canvas_size,
          background_color='black',
          enable_events=True,
          k='LEFT_G'
        )],
        [sg.T('SCORE')],
        [sg.T(str(self.score), expand_x=True, justification='right', k='SCORE_T')],
        [sg.T('LEVEL')],
        [sg.T(str(self.level), expand_x=True, justification='right', k='LEVEL_T')],
        [sg.T('LINES')],
        [sg.T(str(self.lines), expand_x=True, justification='right', k='LINES_T')],
        [sg.B(
          'ranking', button_color=('white', 'cyan3'),
          k='RANKING_B', visible=False
        )]
      ],
      pad=(0, 0),
      border_width=0,
      expand_y=True
    )

    center_frame = sg.Frame(
      title='',
      layout=[[sg.G(
        canvas_size=Tetris_gui.canvas_size,
        graph_bottom_left=(0, 0),
        graph_top_right=Tetris_gui.canvas_size,
        background_color='gray5',
        pad=(0, 0),
        enable_events=True,
        k='CENTER_G'
      )]],
      pad=(0, 0),
      border_width=0
    )

    right_layout = [[sg.T('NEXT', expand_x=True, justification='center')]]
    for i in range(6):
      right_layout += [[sg.G(
        canvas_size=Tetris_gui.mini_canvas_size,
        graph_bottom_left=Tetris_gui.mini_canvas_pad,
        graph_top_right=Tetris_gui.mini_canvas_size,
        background_color='black',
        enable_events=True,
        k='RIGHT_G' + str(i + 1)
      )]]
    right_layout += [[sg.B(
      'continue', button_color=('white', 'DarkOrange3'),
      k='CONTINUE_B', visible=False
    )]]

    right_frame = sg.Frame(
      title='',
      layout=right_layout,
      pad=(0,0),
      border_width=0,
      expand_y=True
    )

    layout = [[left_frame, center_frame, right_frame]]

    with open('icon.dat', 'rb') as f:
      self.icon = f.read()

    return sg.Window('TETRIS', layout, font='メイリオ', icon=self.icon, use_default_focus=False, grab_anywhere=True)


  def create_ranking_window(self, values):
    name = '名無しのTETRISプレイヤー'

    left_frame = sg.Frame(
      title='',
      layout=[
        [sg.T('name:'), sg.T('', text_color='Red', k='CAUTION_T')],
        [sg.Input(default_text=name, size=(35, 1), k='NAME_IN')],
        [sg.T('score:')],
        [sg.T(str(self.score))]
      ],
      pad=(0, 0),
      border_width=0
    )

    right_frame = sg.Frame(
      title='',
      layout=[
        [sg.B(
          'record',
          button_color=('white', 'cyan3'),
          disabled=not self.can_record,
          k='RECORD_B'
         ),
         sg.B(
           'close',
           button_color=('white', 'gray30'),
           k='CLOSE_B'
         )]
      ],
      pad=(0, 0),
      border_width=0
    )

    layout = [
      [sg.Table(
        values=values,
        headings=['No.', 'name', 'score'],
        justification='center',
        vertical_scroll_only=True,
        pad=(0, 0),
        k='RANKING_T',
        expand_x=True,
        expand_y=True
      )],
      [left_frame, right_frame]]

    return sg.Window('ranking', layout, font='メイリオ', icon=self.icon, modal=True, grab_anywhere=True)


  def init_window(self):
    keys = ['LEFT_G', 'CENTER_G']
    for index in range(6):
      keys += ['RIGHT_G' + str(index + 1)]

    for key in keys:
      if key == 'CENTER_G':
        y, x = Tetris.Y_LEN - 4, Tetris.X_LEN - 2
      else:
        y, x = 2, 4
      Tetris_gui.figures[key] = [[dict() for _ in range (x)] for _ in range(y)]

      for i, j in product(range(y), range(x)):
        for color_key in Tetris_gui.num_color:
          color, line_color = Tetris_gui.num_color[color_key]
          figure_id = self.window[key].draw_rectangle(
            (0 + (Tetris_gui.SIDE_LEN * j) + Tetris_gui.LINE_WIDTH,
            Tetris_gui.SIDE_LEN + (Tetris_gui.SIDE_LEN * i) - Tetris_gui.LINE_WIDTH),
            (Tetris_gui.SIDE_LEN + (Tetris_gui.SIDE_LEN * j) - Tetris_gui.LINE_WIDTH,
            0 + (Tetris_gui.SIDE_LEN * i) + Tetris_gui.LINE_WIDTH),
            fill_color=color, line_color=line_color, line_width=Tetris_gui.LINE_WIDTH
          )
          Tetris_gui.figures[key][i][j][color_key] = figure_id


  def screen(self, map_array):
    def draw(key, i, j):
      if pixel < 0:
        figure_id = Tetris_gui.figures[key][i][j][pixel]
      else:
        figure_id = Tetris_gui.figures[key][i][j][pixel % 8]
      self.window[key].BringFigureToFront(figure_id)


    if self.hold in Tetris.mino:
      for i, line in enumerate(Tetris.mino[self.hold][::-1]):
        for j, pixel in enumerate(line):
          if self.leftG_buf[i][j] != pixel:
            self.leftG_buf[i][j] = pixel
            draw('LEFT_G', i, j)

    for i, line in enumerate(map_array[3:Tetris.Y_LEN - 1][::-1]):
      for j, pixel in enumerate(line[1:Tetris.X_LEN - 1]):
        if self.centerG_buf[i][j] != pixel:
          self.centerG_buf[i][j] = pixel
          draw('CENTER_G', i, j)

    for index in range(6):
      key = 'RIGHT_G' + str(index + 1)
      for  i, line in enumerate(Tetris.mino[self.next[index]][::-1]):
        for j, pixel in enumerate(line):
          if self.rightG_buf[index][i][j] != pixel:
            self.rightG_buf[index][i][j] = pixel
            draw(key, i, j)

    self.window['SCORE_T'].update(str(self.score))
    self.window['LEVEL_T'].update(str(self.level))
    self.window['LINES_T'].update(str(self.lines))


  def ranking(self):
    def attach_rank(scores):  # ランク付け
      ranking_scores = list()
      tmp = [None, None]
      for i, score in enumerate(scores):
        if tmp[1] == score[1]:
          i = score[0]
        else:
          tmp = scores
        ranking_scores += [[str(i + 1)] + [f'{score[0]:^15}', score[1]]]
      return ranking_scores


    with open('scores.dat', 'rb') as f:
      scores = f.read().decode()

    if not len(scores):  # バイナリファイルの初期化
      scores = 'TETRIS師範:50000\nTETRISさん:25000\nTETRISくん:10000\n'
      with open('scores.dat', 'wb') as f:
        f.write(scores.encode())

    scores = scores.splitlines()  # データの整形
    for i, score in enumerate(scores):
      scores[i] = score.split(':')
    scores.sort(key=lambda x:int(x[1]), reverse=True)

    ranking_scores = attach_rank(scores)

    ranking_window = self.create_ranking_window(ranking_scores)

    while True:
      event, value = ranking_window.read()
      if event in {sg.WIN_CLOSED, 'CLOSE_B'}:
        break

      elif event == 'RECORD_B':
        name = value['NAME_IN']
        if len(name) > 15 or len(name) < 1:
          ranking_window['CAUTION_T'].update('*0 < n <= 15')
        for ch in {':', '\\'}:
          if ch in name:
            ranking_window['CAUTION_T'].update(f'‘{ch}’ cannot be used')
            break
        else:
          ranking_window['CAUTION_T'].update('')

          with open('scores.dat', 'ab') as f:
            f.write(f'{name}:{self.score}\n'.encode())
          with open('scores.dat', 'rb') as f:
            scores = f.read().decode()

          scores = scores.splitlines()
          for i, score in enumerate(scores):
            scores[i] = score.split(':')
          scores.sort(key=lambda x:int(x[1]), reverse=True)

          ranking_scores = attach_rank(scores)

          ranking_window['RANKING_T'].update(
            values=ranking_scores
          )
          self.can_record = False
          ranking_window['RECORD_B'].update(
            disabled=not self.can_record
          )

    ranking_window.close()


  def end(self):
    self.window['CONTINUE_B'].update(visible=True)
    self.window['CONTINUE_B'].expand(expand_x=True)
    self.window['RANKING_B'].update(visible=True)
    self.window['RANKING_B'].expand(expand_x=True)


  def start(self):
    play_th = Thread(target=self.play, daemon=True)
    input_th = Thread(target=self.input_ky, daemon=True)
    play_th.start()
    input_th.start()


  def continue_tetris(self):
    window_copy = self.window
    self.__init__()
    self.window = window_copy
    self.window['CONTINUE_B'].update(visible=False)
    self.window['RANKING_B'].update(visible=False)
    self.start()


  def window_read(self):
    timeout = 0
    while True:
      event = self.window.read(timeout)[0]
      if event == sg.WIN_CLOSED:
        self.continue_play = False
        break
      elif event == 'RANKING_B':
        self.ranking()
      elif event == 'CONTINUE_B':
        self.continue_tetris()
      elif event == '__TIMEOUT__':
        self.init_window()
        self.start()
        timeout = None
    self.window.close()


def main():
  tetris = Tetris_gui()
  tetris.window_read()


if __name__ == '__main__':
  main()
