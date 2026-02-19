import json
import os
import time
import sys
import threading
import traceback
from datetime import datetime
import inspect
import ctypes
from ctypes import wintypes
import re
import math
from typing import Tuple
from itertools import product

from .ansi import  ansi, art

import subprocess

def terminal_size() -> tuple:
    """
    terminal size
    
    Returns:
        tuple: 0 - height. 1 - lines num
    """
    # X , Y 
    return (int(os.get_terminal_size().columns) , int(os.get_terminal_size().lines))

def color(text, color, style='standart', begraund='blak', end='\33[0m')->str:#text,color,stule,beggraubd
    r"""позволяет перекрашивать цвет работает на `ansi`

    Args:
        text (_str_): текст который будет перекрашен
        color (_srt_): цвет текста
        stule (str, optional): стиль. Defaults to 'standart'.
        begraund (str, optional): задний фон. Defaults to 'blak'.
        end (str, optional): конец строки. Defaults to '\33[0'.

    Returns:
        str: текст с `ansi` кодами
    """
    
    self=ansi()
    try:
        stule=self.style[style]
    except KeyError:
        raise KeyError(f'error Not correct parameters , parameters :{self.style.keys()} ')
    try:
        color=self.color[color]
    except KeyError:
        raise KeyError(f'error Not correct parameters , parameters :{self.style.keys()} ')
    try:
        begraund=self.beggraubd[begraund]
    except KeyError:
        raise KeyError(f'error Not correct parameters , parameters :{self.beggraubd.keys()} ')
    return f"\33[{stule};{color};{begraund}m{text}{end}"
    

def move_cursor(x:int, y:int):
    print(f"\033[{y};{x}H", end='')

#def print_over(s:int):
#    sys.stdout.write("\033[F")
#    sys.stdout.write("\033[K")
#    sys.stdout.flush()    
        
def clear():
    print('\033[0m') #очистка
    if os.name == 'nt': 
        os.system("cls")
    else:
        os.system("clear")

def frame(text, x=-1, y=-1, text_color="\33[0m", frame_color="\33[0m")->str:
    """создания рамки с текстом в нутри

    Args:
        text: текст в нитри рамки
        x (int, optional): X координата. Defaults to -1.
        y (int, optional): Y координата. Defaults to -1.
        text_color (str, optional): цвет текста в ansi формате. Defaults to "\33[0m".
        frame_color (str, optional): цвет рамки в ansi формате. Defaults to "\33[0m".

    Returns:
        str: рамка с текстом
    """
    text=str(text)
    split=text.split('\n')
    
    if x==-1 and y==-1:
        ots=' '*(int(round(terminal_size()[0]/2))-int(len(text)+2))
    else:
        ots=' '*x
    temp_string=f"{ots}{frame_color}╔{'═'*len(max(split, key=len))}╗\33[0m"
    for t in split:
        temp_string=temp_string+f"\n{ots}{frame_color}║\33[0m{text_color}{t}\33[0m{' '*(len(max(split, key=len))-len(t))}{frame_color}║\33[0m"
    temp_string=temp_string+f"\n{ots}{frame_color}╚{'═'*len(max(split, key=len))}╝\33[0m"
        
    return temp_string

class InputMany:
    def __init__(self):
        self.output = []
        self.inputs_list = []
        self.input_in = 0
        self.lock = threading.Lock()

    def input_at(self, x: int, y: int, prompt: str):
        """Отобразить приглашение в позиции (x,y)."""
        self.inputs_list.append((x, y, prompt))

    def _reader(self, x: int, y: int, prompt: str, index:int):
        """
        Читает ввод и сохраняет в self.output в позиции index.
        index нужен, чтобы сохранить порядок ответов соответствующим переданным координатам.
        """
        move_cursor(x + len(prompt), y)
        user_input = sys.stdin.readline()
        with self.lock:
            self.output.append(user_input)

    def run_inputs(self) -> list:
        """
        coordinates: последовательность кортежей (x, y, prompt)
        Возвращает список ответов в том же порядке, в котором заданы coordinates.
        """
        threads = []

        # Сначала отрисуем все промпты
        for (x, y, prompt) in self.inputs_list:
            move_cursor(x, y)
            sys.stdout.write(prompt)
            sys.stdout.flush()
        
        ix=0
        for _i, (x, y, prompt) in enumerate(self.inputs_list):
            t = threading.Thread(target=self._reader, args=(x, y, prompt, ix))
            t.daemon = True
            threads.append(t)
            t.start()
            t.join()
            ix+=1

        #for t in threads:
        #    t.join()

        return self.output

# создано при моральной поддержке @KTkotiktapok

def rotation_calc(x:int, y:int, cx:float, cy:float, angle_deg:float) -> Tuple[int,int]:
    a = math.radians(angle_deg)
    src_aspect = 0.5

    y_norm = max(0, x - cy) # ХУЙНЯ!!!!!!!!
    x_n = max(0, y - cx)

    xr = x_n * math.cos(a) - y_norm * math.sin(a)
    yr = x_n * math.sin(a) + y_norm * math.cos(a)

    return round(xr * src_aspect)+x , round(yr / src_aspect)+y

class display():
    def __init__(self, size=(None,), begraund_symbol=' '):
        """
        Args:
            size (tuple, optional): задает размеры экрана. 1 элемент X координата, 2 элемент Y координата по умолчанию ипользует реальный размер терминала. Defaults to (None,).
        """
        templist=[]
        if size[0] is None:
            size=terminal_size()
        for _lens in range(size[1]): 
            temp={}
            for i in range(size[0]):
                temp[i] = begraund_symbol
            templist.append(temp)
        self.display=templist
        
    def box(self,px:int, py:int, x:int, y:int, symbol='█', filling=False, color=("\33[0m","\33[0m")):
        """### create box

        Args:
            px (int): length box
            py (int): height box
            x (int): X Corridate
            y (int): Y Corridate
            symbol (str, optional): symbol box. Defaults to '█'.
            filling (bool): заполнен ли квадрат.
            color (tuple): цвет синволов где 0 элемент это начало ANSI кода (перед символом), а 1 его конец (после символа).
        """
        
        if y>len(self.display)+py:
            raise TypeError(f"Y goes beyond (max {len(self.display)})")
        if x>len(self.display[0])+px:
            raise TypeError(f"X goes beyond (max {len(self.display[0])})")
        
        for xpos in range(x, x+px):
            self.display[y][xpos] = color[0] + symbol + color[1]
            
        if filling:
            for y in range(y,y+py):
                for xe in range(x,x+px):
                    self.display[y][xe] = color[0] + symbol + color[1]
        else:
            for y in range(y,y+py):
                self.display[y][x] = color[0] + symbol + color[1]
                self.display[y][x+px] = color[0] + symbol + color[1]
                 
        for xpos in range(x,x+px):
            self.display[y][xpos] = color[0] + symbol + color[1]
            
    def cursor(self, x : int, y : int, symbol='█', color=("\33[0m","\33[0m")):
        """рисует синвол по координатам

        Args:
            x (int): x координата курсора
            y (int): Y координата курсора
            symbol (str, optional): синвол который будет отрисован. Defaults to '█'.
            color (tuple, optional): цвет символов где 0 элемент это начало ANSI кода (перед символом), а 1 его конец (после символа). Defaults to ("\33[0m","\33[0m").
        """
        try:
            self.display[y]
        except KeyError:
            raise KeyError(f'no the lines end lines {len(self.display)}')
        try:
            self.display[y][x] = color[0] + symbol + color[1]
        except KeyError:
            raise KeyError(f'There is no such symbol')
    
    def line(self, point1:tuple[int,int], point2:tuple[int,int], symbol='█', color:tuple=("\33[0m","\33[0m")):
        """
        Рисует линию между point1 и point2.
        Args:
            point1 (tuple): координаты 1 точки формат: `(X, Y)`
            point2 (tuple): координаты 2 точки формат: `(X, Y)`
            color (tuple): цвет синволов где 0 элемент это начало ANSI кода (перед символом), а 1 его конец (после символа).
            symbol (str): синвол из которого сотоит линия.
        """
        x0, y0 = point1
        
        x1, y1 = point2
        
        if y0 < 0 or y1 < 0 or y0 >= len(self.display) or y1 >= len(self.display):
            raise TypeError(f"Y goes beyond (max {len(self.display)-1})")

        dx = abs(x1 - x0)
        sx = 1 if x0 < x1 else -1
        dy = -abs(y1 - y0)
        sy = 1 if y0 < y1 else -1
        err = dx + dy

        x, y = x0, y0
        while True:
            # проверяем, что строка существует (по Y) - уже гарантировано; по X используем запись в словарь
            self.display[y][x] = color[0] + symbol + color[1]
            if x == x1 and y == y1:
                break
            e2 = 2 * err
            if e2 >= dy:
                err += dy
                x += sx
            if e2 <= dx:
                err += dx
                y += sy

    def multi_line(self, points:list[tuple[int, int]], symbol='█', color:tuple=("\33[0m","\33[0m")):
        """
        соеденяет точки указанные в списке

        Args:
            points(list): список соеденяемых точек где кажный элемент это кортеж с координатой X и Y
            color (tuple): цвет синволов где 0 элемент это начало ANSI кода (перед символом), а 1 его конец (после символа).
            symbol (str): синвол из которого сотоит линия.
        """
        t_size=terminal_size()

        def line(x1,y1, x2,y2):
            step = abs(x1-x2)<abs(y1-y2)

            if step:
                x1,y1 = y1,x1
                x2,y2 = y2,x2
                
            if x1>x2:
                x1,x2 = x2,x1
                y1,y2 = y2,y1

            x=x1
            while x<=x2:
                t = (x-x1) / float(x2-x1)
                y = round(y1 + (y2-y1)*t)
                if step:
                    self.cursor(y, x, symbol=symbol, color=color)
                else:
                    self.cursor(x, y, symbol=symbol, color=color)
                x+=1

        x1,y1,x2,y2=0,0,0,0
        for pt in range(0,len(points)):

            if pt % 2 == 0:
                x2 = points[pt][0]
                y2 = points[pt][1]
            else:
                x1 = points[pt][0]
                y1 = points[pt][1]
            
            if pt == 0:
                x1, y1 = points[0][0], points[0][1]
                x2, y2 = points[1][0], points[1][1]
            
            if x1 > t_size[0] or x2 > t_size[0] or y1  > t_size[1] or y2 > t_size[0]:
                raise ValueError(f"pint {points[pt]} goes beyond")

            if pt == len(points):
                if len(points) >=3:
                    x2, y2 = points[0][0], points[0][1]
                else:
                    return
                
            if x1+y1 == x2+y2:
                continue

            line(x1, y1, x2, y2)
        
    def circle(self, cx: int, cy: int, radius: int, symbol='█', color:tuple=("\33[0m","\33[0m")):
        '''### функция рисующая круг (**не работает !**)

        Args: 
            x (int): X координата 
            y (int): Y координата  
            radius (int): радиус круга
            symbol (str): синвол из которого сотоит круг.
            color (tuple): цвет синволов где 0 элемент это начало ANSI кода (перед символом), а 1 его конец (после символа).
        '''
        point1 = (cx, cy+radius)# верхняя точка
        point2 = (round(cx+radius + (radius/100*60)), cy)# левая
        point3 = (round(cx-radius - (radius/100*60)), cy)# правая
        point4 = (cx, cy-radius)# нижняя точа

        def pr(p:tuple):
            self.display[p[1]][p[0]] = color[0] + symbol + color[1]

        aspectx = round(radius/2 * 1.7)
        aspecty = round(radius/2)# воотношение синвола это 40/32

        p1,p2,p3,p4,p5,p6,p7,p8=(0,0),(0,0),(0,0),(0,0),(0,0),(0,0),(0,0),(0,0)

        for x, y in product(range(aspectx), range(aspecty)):
            pr((point1[0]+x, point1[1]))
            pr((point1[0]-x, point1[1]))

            pr((point2[0], point2[1]+y))
            pr((point2[0], point2[1]-y))

            pr((point3[0], point3[1]+y))
            pr((point3[0], point3[1]-y))

            pr((point4[0]+x, point4[1]))
            pr((point4[0]-x, point4[1]))

            if aspectx-1 == x and aspecty-1 == y:   
                p1 = (point1[0]+x, point1[1])
                p2 = (point1[0]-x, point1[1])
                p3 = (point2[0], point2[1]+y)
                p4 = (point2[0], point2[1]-y)
                p5 = (point3[0], point3[1]+y)
                p6 = (point3[0], point3[1]-y)
                p7 = (point4[0]+x, point4[1])
                p8 = (point4[0]-x, point4[1])

        
        self.line(p1, p3, symbol=symbol, color=color)
        self.line(p2, p5, symbol=symbol, color=color)

        self.line(p4, p7, symbol=symbol, color=color)
        self.line(p6, p8, symbol=symbol, color=color)       


    def clear_display(self):
        """### clear display"""
        
        self.display={}
        templist=[]
        size=terminal_size()
        for _ in range(size[1]): 
            temp={}
            for i in range(size[0]):
                temp[i]=' '
            templist.append(temp)
        self.display=templist
    
    def trigon(self, x:int, y:int, h:int, w:int, symbol='█', filling:bool=False, color=("\33[0m","\33[0m")):
        """рисует треугольник

        Args:
            x (int): X координата
            y (int): Y координата
            h (int): высота
            w (int): ширена
            symbol (str, optional): синвол из кторого будет состоять фигура. Defaults to '█'.
            color (tuple): цвет синволов где 0 элемент это начало ANSI кода (перед символом), а 1 его конец (после символа).
        """
        
        higft=0
        wight=0

        while h>=higft:
            if filling:
                self.line((x+wight, y+higft),(x-wight, y+higft), color=color)
            else:
                self.display[y+higft][x+wight] =color[0] + symbol + color[1]
                self.display[y+higft][x-wight] =color[0] + symbol + color[1]
            if wight<=w:
                wight+=1
            higft+=1

        for line in range(x-wight+1, x+wight-1):
            self.display[y+higft-1][line] = color[0] + symbol + color[1]
    
    def Former(self, point1:tuple[int, int], point2:tuple[int, int], point3:tuple[int, int], symbol='█', color=("\33[0m","\33[0m")):
        """триугольник с произвольнвм положением точек 

        Args:
            point1 (tuple[int, int]): точка 1, элемент 0 - X координата, 1 - Y координата 
            point2 (tuple[int, int]): точка 2, элемент 0 - X координата, 1 - Y координата
            point3 (tuple[int, int]): точка 3, элемент 0 - X координата, 1 - Y координата
            symbol (str, optional): синвол из кторого будет состоять фигура. Defaults to '█'.
            color (tuple, optional):  цвет синволов где 0 элемент это начало ANSI кода (перед символом), а 1 его конец (после символа). Defaults to ("\33[0m","\33[0m").
        """
        self.multi_line([point1, point2, point3, point1], symbol, color)

    def rotation_box(self, x:int, y:int, w:int, h:int, angle:int, symbol:str='█', color:Tuple[str,str]=("\33[0m","\33[0m")):
        """квадрат/прямоугольник с возможнотью разворота с заданым градусом

        Args:
            x (int): X координата
            y (int): Y координата
            w (int): ширена
            h (int): высота
            angle (int): градус наклона
            symbol (str, optional): синвол из кторого будет состоять фигура. Defaults to '█'.
            color (Tuple[str,str], optional): цвет синволов где 0 элемент это начало ANSI кода (перед символом), а 1 его конец (после символа). Defaults to ("\33[0m","\33[0m").
        """
        cx = x + w / 2
        cy = y + h / 2
        p1 = rotation_calc(x, y, cx, cy, angle)
        p2 = rotation_calc(x + w, y, cx, cy, angle)
        p3 = rotation_calc(x + w, y + h, cx, cy, angle)
        p4 = rotation_calc(x, y + h, cx, cy, angle)

        self.multi_line([p1, p2, p3, p4, p1], symbol=symbol, color=color)

    def printf(self, x:int, y:int, text:str, color = ("\33[0m", "\33[0m")):
        """печатает текст где каждый синвол находится в собственной клетке

        Args:
            x (int): X координата 1 синвола
            y (int): Y координата 
            text (str): выводимый текст
            color (tuple, optional):  цвет синволов где 0 элемент это начало ANSI кода (перед символом), а 1 его конец (после символа). Defaults to ("\33[0m", "\33[0m").
        """
        t_size=terminal_size()
        if x > t_size[0]  or y  > t_size[0]:
            raise ValueError(f"text goes beyond")
        temp_x=x
        for symbol in text:
            self.cursor(temp_x, y, symbol, color=color)
            temp_x+=1
        
    def echo(self, end='\n', print_std:bool=True) -> str:
        """выводит буфер на экран

        Args:
            end (str, optional): аргумент end. Defaults to '\n'.
            print_std (bool): вудет ли вывод содержимого буфера в терминал. Defaults to `True`. 

        Returns:
            str: содержимое буфера
        """
        
        strings='' # НЕ СТРИНГИ А СТРОКИ
        for i in self.display:
            for st in list(dict(i).keys()):
                strings=strings+i[st]
            strings+='\n'
        if print_std:
            print(strings, end=end)
        
        return strings
        
        
def write_to_log_file(file, t ,path_save_log):
    if path_save_log:
        path=os.path.join(path_save_log, file)
    else:
        path=file
    with open(path, 'a', buffering=1) as f:
        f.write(t+'\n')        

class logse:
    def __init__(self, file:str='log.log', level:int=2, seve_log_file:bool=True, path_save_log:str|None=None):
        self.file=file
        self.level=level
        self.seve_log_file=seve_log_file
        self.patern=f"{datetime.now().strftime(r"%Y-%m-%d %H:%M:%S")} |{sys._getframe(1).f_locals['__file__']}| "
        self.path_save_log=path_save_log
        
        # color
        self.color_green='\33[32m'
        self.color_red='\33[31m'
        self.color_yelow='\33[33m'
    
    def info(self, text, info_patern=f"info: ", end='\033[0m'):
        if self.level>=0:
            print(self.patern+f"{self.color_green}line:{inspect.stack()[1][2]} |{info_patern}{str(text)}{end}")
        
            if self.seve_log_file:
                write_to_log_file(self.file, self.patern+f"line:{inspect.stack()[1][2]} |{info_patern}{str(text)}", self.path_save_log)    
                
    def warning(self, text, warning_patern=f"warning: ", end='\033[0m'):
        if self.level>=1:
            print(self.patern+f"{self.color_yelow}line:{inspect.stack()[1][2]} |{warning_patern}{str(text)}{end}")
            
            if self.seve_log_file:
                write_to_log_file(self.file, self.patern+f"line:{inspect.stack()[1][2]} |{warning_patern}{str(text)}", self.path_save_log)    
        
    def error(self, text, error_patern=f"ERROR: ", end='\033[0m'):
        if self.level>=2:
            print(self.patern+f"{self.color_red}line:{inspect.stack()[1][2]} |{error_patern}{str(text)}{end}")
            
            if self.seve_log_file:
                write_to_log_file(self.file, self.patern+f"line:{inspect.stack()[1][2]} |{error_patern}{str(text)}", self.path_save_log)
        
