import edukoi
import argparse

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

pars.add_argument('--hide',help='Hide sonified image',default=False,action=argparse.BooleanOptionalAction)

args = pars.parse_args()

edukoi.start(image=args.image,show=not args.hide,mode=args.mode,notes=(args.notes[0],args.notes[1],args.notes[2]),volume=0,box=args.box,renorm=True)
