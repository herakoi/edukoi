from .core import *


def basic():
  pars = argparse.ArgumentParser()
  pars.add_argument('image',
                    help='Input image',
                    nargs='?')
  pars.add_argument('--notes',
                    help='Define the pitch values (as note+octave format; e.g., C4)',
                    nargs=3,default=['C3','C3','C3'],metavar=('red','green','blue'))
  pars.add_argument('--mode',
                    help='Select herakoi mode [single/adaptive/scan]',
                    default='single',metavar=('mode'))
  pars.add_argument('--box',
                    help='sonification box size in units of frame percentage',
                    default=2,metavar=('box'),type=float)

  args = pars.parse_args()

  start(image=args.image,show=True,mode=args.mode,notes=(args.notes[0],args.notes[1],args.notes[2]),volume=0,box=args.box)


def test():
  pars = argparse.ArgumentParser()
  pars.add_argument('image',
                    help='Input image',
                    nargs='?')
  pars.add_argument('--notes',
                    help='Define the pitch values (as note+octave format; e.g., C4)',
                    nargs=3,default=['C3','C3','C3'],metavar=('red','green','blue'))
  pars.add_argument('--mode',
                    help='Select herakoi mode [single/adaptive/scan]',
                    default='single',metavar=('mode'))
  pars.add_argument('--box',
                    help='sonification box size in units of frame percentage',
                    default=2,metavar=('box'),type=float)

  args = pars.parse_args()

  start(image=args.image,show=False,mode=args.mode,notes=(args.notes[0],args.notes[1],args.notes[2]),volume=0,box=args.box)
