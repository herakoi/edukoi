import argparse

import numpy as np
import re

import cv2
import mediapipe as mp

import tkinter
import tkinter.filedialog as filedialog

from pynput import keyboard
from pynput.keyboard import Key

import time
import sys
import os

from mingus.midi import fluidsynth
from mingus.midi import pyfluidsynth
fluidsynth.init('{0}/support/edukoi.sf2'.format(os.path.dirname(__file__)))

vlims_ = (40,127) 
flims_ = (63, 63, 63) # C2-B5

root = tkinter.Tk()
scrw = root.winfo_screenwidth()
scrh = root.winfo_screenheight()
root.withdraw()

global pressed; pressed = None

# Convert BGR image into HSV
# -------------------------------------
class gethsv:
  def __init__(self,inp):
    self.bgr = cv2.imread(inp)

    for i in range(3):
      self.bgr[...,i][self.bgr[...,i]>200] = 255
      self.bgr[...,i][self.bgr[...,i]<200] = 0

    self.hsv = cv2.cvtColor(self.bgr,cv2.COLOR_BGR2HSV)

    self.mono = np.logical_and((self.bgr[...,0]==self.bgr[...,1]).all(),
                               (self.bgr[...,1]==self.bgr[...,2]).all())

    if self.mono:
      self.hsv[...,0] = self.hsv[...,2].copy()
    else:
      self.hsv[self.hsv[...,0]>150.00,0] = 0.00

    self.h, self.w, _ = self.bgr.shape

# Convert key name
# Ported from the pretty-midi package
# -------------------------------------
def nametopitch(name):
    pitch_map = {'C': 0, 'D': 2, 'E':  4, 'F':  5, 'G': 7, 'A': 9, 'B': 11}
    accen_map = {'#': 1,  '': 0, 'b': -1, '!': -1}

    try:
      match = re.match(r'^(?P<n>[A-Ga-g])(?P<off>[#b!]?)(?P<oct>[+-]?\d+)$',name)

      pitch = match.group('n').upper()
      offset = accen_map[match.group('off')]
      octave = int(match.group('oct'))
    except:
      raise ValueError('Improper note format: {0}'.format(name))

    return 12*(octave+1)+pitch_map[pitch]+offset

# Keyboard press
# -------------------------------------
def on_press(key):
  global pressed
  if key == Key.right: pressed = 'right'
  if key == Key.left:  pressed = 'left'

# Build the edukoi player
# =====================================
class start:
  def __init__(self,image=None,show=True,mode='single',port={},video=0,box=2,**kwargs):

    global pressed

    self.listener = keyboard.Listener(on_press=on_press)
    self.listener.start()  

    if image is None:
      tkinter.Tk().withdraw()
      imgpath = filedialog.askopenfilenames()
        
      if len(imgpath)<1: sys.exit(1)
    else: imgpath = image

    if isinstance(imgpath,str): imgpath = [imgpath]
    self.imglist = False if len(imgpath)==1 else True

    imginit = 0

    if mode not in ['single','adaptive','scan']:
      raise NotImplementedError('"{0}" mode is unknown'.format(mode))

    self.valname = 'edukoi'

  # Start capture from webcam
  # -------------------------------------
    while True:
      self.opvideo = cv2.VideoCapture(video)
      self.opmusic = gethsv(imgpath[imginit])

      cv2.namedWindow('imframe',cv2.WINDOW_NORMAL)

      self.mphands = mp.solutions.hands
      self.mpdraws = mp.solutions.drawing_utils
      self.mpstyle = mp.solutions.drawing_styles

      self.opindex = 8
      self.opthumb = 4
      
      if mode=='adaptive':
        self.oppatch = None
      else:
        self.oppatch = np.minimum(self.opmusic.w,self.opmusic.h)
        self.oppatch = int(np.clip((box/100)*self.oppatch,2,None))
      
      self.opcolor = {'Left': (0,255,  0), 
                     'Right': (0,255,255)}

      if 'volume' in kwargs:
        vlims = (np.interp(kwargs['volume'],(0,100),(0,127)),127)
      else: vlims = vlims_

      if 'notes' in kwargs:
        flims = (nametopitch(kwargs['notes'][0]),
                 nametopitch(kwargs['notes'][1]),
                 nametopitch(kwargs['notes'][2]))
      else: flims = flims_
    
      fluidsynth.set_instrument(0,2); fluidsynth.pan(0,  0)
      fluidsynth.set_instrument(1,0); fluidsynth.pan(1, 50)
      fluidsynth.set_instrument(2,1); fluidsynth.pan(2,100)

      self.run(show,mode,vlims=vlims,flims=flims,**kwargs)

      if pressed=='right' and imginit<(len(imgpath)-1):
        imginit += 1
      elif pressed=='left' and imginit>0:
        imginit -= 1
      pressed = None

# Convert H and B to note and loudness
# =====================================
  def getmex(self,posx,box,vlims=vlims_,flims=flims_):
    def getval(img,clip):
      val = np.median(img[np.clip(posx[1]-box[1]//2,0,self.opmusic.h-1):np.clip(posx[1]+box[1]//2,0,self.opmusic.h-1),
                          np.clip(posx[0]-box[0]//2,0,self.opmusic.w-1):np.clip(posx[0]+box[0]//2,0,self.opmusic.w-1)])
      vmidi = 0 if np.isnan(val) else val
      vmidi = int(np.interp(vmidi,(img.min(),img.max()),clip))
      return vmidi

    fb = getval(self.opmusic.bgr[...,0],(flims[0],flims[0]))
    fg = getval(self.opmusic.bgr[...,1],(flims[1],flims[1]))
    fr = getval(self.opmusic.bgr[...,2],(flims[2],flims[2]))

    print(fb,fg,fr)
    vb = getval(self.opmusic.bgr[...,0],vlims)
    vg = getval(self.opmusic.bgr[...,1],vlims)
    vr = getval(self.opmusic.bgr[...,2],vlims)

    return [fb, fg, fr], [vb, vg, vr]

# Draw and return hand markers position
# =====================================
  def posndraw(self,frame,marks,label,draw=True):
    if draw: self.mpdraws.draw_landmarks(frame,marks,self.mphands.HAND_CONNECTIONS,None)

    point = marks.landmark[self.opindex]
    posix = [int(point.x*frame.shape[1]),
             int(point.y*frame.shape[0]),np.abs(point.z)*300]

    if draw and self.oppatch is not None: 
      cv2.circle(frame,(posix[0],posix[1]),np.clip(int(posix[2]),2,None),self.opcolor[label],-1)

    return posix

# Rescale image according to input
# =====================================
  def rescale(self,image):
    if image.shape[1]>image.shape[0]:
      if (self.opmusic.w<self.opmusic.h) or \
         (self.opmusic.h/self.opmusic.w)>(image.shape[0]/image.shape[1]):
        wk = (self.opmusic.w/self.opmusic.h)*image.shape[0]
        wi = int(0.50*(image.shape[1]-wk))     
        return image[:,wi:-wi]
      else: 
        hk = (self.opmusic.h/self.opmusic.w)*image.shape[1]
        hi = int(0.50*(image.shape[0]-hk))
        return image[hi:-hi,:]
    else:
      return image

# Single-user mode
# =====================================
  def run(self,show=True,mode='single',vlims=vlims_,flims=flims_,**kwargs):
    ophands = self.mphands.Hands(max_num_hands=2 if mode=='scan' else 1)

    onmusic = False

    pxshift = kwargs.get('shift',2)
    pxshift = (pxshift/100)*np.minimum(self.opmusic.w,self.opmusic.h)

    toctime = kwargs.get('toc',0.05)
    offtime = kwargs.get('off',0.05)
    tictime = time.time()

    while True:
      _, opframe = self.opvideo.read()

      opframe = self.rescale(opframe)

      opframe = cv2.flip(opframe,1)
      imframe = cv2.cvtColor(opframe,cv2.COLOR_BGR2RGB)

      immusic = self.opmusic.bgr.copy()
      imhands = ophands.process(imframe)

      bhmidif_r, bhmidiv_r = None, None
      bhmidif_g, bhmidiv_g = None, None
      bhmidif_b, bhmidiv_b = None, None

      opmodes = mode

      if imhands.multi_hand_landmarks:
        if mode=='scan' and len(imhands.multi_hand_landmarks)==1: opmodes = 'single'

        if opmodes=='scan':
          pxmusic = [0,0,50]
          for mi, immarks in enumerate(imhands.multi_hand_landmarks):
            imlabel = imhands.multi_handedness[mi].classification[0].label
            
            self.mpdraws.draw_landmarks(immusic,immarks,self.mphands.HAND_CONNECTIONS,None)
            self.mpdraws.draw_landmarks(opframe,immarks,self.mphands.HAND_CONNECTIONS,None)

            px, py, _ = self.posndraw(immusic,immarks,imlabel,False)

            if imlabel=='Right': pxmusic[0] = px
            if imlabel=='Left':  pxmusic[1] = py

          cv2.circle(immusic,(pxmusic[0],pxmusic[1]),pxmusic[2],(255,255,255),-1)

        else:
          for mi, immarks in enumerate(imhands.multi_hand_landmarks):
            imlabel = imhands.multi_handedness[mi].classification[0].label

            _       = self.posndraw(opframe,immarks,imlabel,True)

            if self.oppatch is None:
              pxindex = immarks.landmark[self.opindex]
              pxthumb = immarks.landmark[self.opthumb]
              pxpatch = [int(np.abs(pxindex.x-pxthumb.x)*immusic.shape[1]),
                         int(np.abs(pxindex.y-pxthumb.y)*immusic.shape[0])]

              _ = self.posndraw(immusic,immarks,imlabel,True)
              pxmusic = [0.50*(pxindex.x+pxthumb.x),0.50*(pxindex.y+pxthumb.y),0.50*(pxindex.z+pxthumb.z)]
              pxmusic = [int(pxmusic[0]*immusic.shape[1]),
                         int(pxmusic[1]*immusic.shape[0]),int(pxmusic[2]*300)]

              cv2.rectangle(immusic,(int(pxthumb.x*immusic.shape[1]),int(pxthumb.y*immusic.shape[0])),
                                    (int(pxindex.x*immusic.shape[1]),int(pxindex.y*immusic.shape[0])),self.opcolor[imlabel],1)
              cv2.circle(immusic,(pxmusic[0],pxmusic[1]),2,self.opcolor[imlabel],-1)
 
            else:
              pxmusic = self.posndraw(immusic,immarks,imlabel,True)
              pxpatch = [self.oppatch,self.oppatch]

            if (opmodes in ['single','adaptive'] and imlabel=='Left') or (opmodes=='party'):
              bhmidif, bhmidiv = self.getmex(pxmusic,pxpatch,vlims,flims)
              bhmidif_b, bhmidif_g, bhmidif_r = bhmidif
              bhmidiv_b, bhmidiv_g, bhmidiv_r = bhmidiv

            if (opmodes in ['single','adaptive'] and imlabel=='Right'):
              rhmidif, rhmidiv = self.getmex(pxmusic,pxpatch,vlims,flims)

              rhmidif_b, rhmidif_g, rhmidif_r = rhmidif
              rhmidiv_b, rhmidiv_g, rhmidiv_r = rhmidiv

              bhmidif_b = rhmidif_b if bhmidif_b is None else int(0.50*(rhmidif_b+bhmidif_b))
              bhmidif_g = rhmidif_g if bhmidif_g is None else int(0.50*(rhmidif_g+bhmidif_g))
              bhmidif_r = rhmidif_r if bhmidif_r is None else int(0.50*(rhmidif_r+bhmidif_r))

              bhmidiv_b = rhmidiv_b if bhmidiv_b is None else int(0.50*(rhmidiv_b+bhmidiv_b))
              bhmidiv_g = rhmidiv_g if bhmidiv_g is None else int(0.50*(rhmidiv_g+bhmidiv_g))
              bhmidiv_r = rhmidiv_r if bhmidiv_r is None else int(0.50*(rhmidiv_r+bhmidiv_r))

        if opmodes in ['single','adaptive']:
          if (bhmidif_r is not None) and (bhmidif_g is not None) and (bhmidif_b is not None):
            if time.time()-tictime>toctime and not onmusic:
              fluidsynth.play_Note(bhmidif_r,0,bhmidiv_r)
              fluidsynth.play_Note(bhmidif_g,1,bhmidiv_g)
              fluidsynth.play_Note(bhmidif_b,2,bhmidiv_b)

              pxmusicold = pxmusic
              onmusic = True

            if time.time()-tictime>toctime+offtime and np.hypot(pxmusicold[0]-pxmusic[0],pxmusicold[1]-pxmusic[1])>pxshift:
              fluidsynth.stop_everything()
              onmusic = False

              tic = time.time()
          else: fluidsynth.stop_everything()
      else: fluidsynth.stop_everything()

      cv2.imshow('imframe',opframe)
      if show: cv2.imshow('immusic',immusic)
      
      imgw = cv2.getWindowImageRect('imframe')[2]

      cv2.moveWindow('imframe',scrw-imgw,0)

      if (cv2.waitKey(1) & 0xFF == ord('q')) or (self.imglist and pressed is not None): break

    self.opvideo.release()
    cv2.destroyAllWindows()
