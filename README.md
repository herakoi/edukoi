# edukoi

Education-tailored version of [`herakoi`](https://github.com/lucadimascolo/herakoi) — a motion-sensing experiment in the context of image sonification


## Installation
Before building `edukoi`, let us install some key dependencies.
First, you need to get the `fluidsynth` library:

```
conda install -c conda-forge fluidsynth
```


Finally, you need to install `mediapipe` as:

```
python -m pip install mediapipe
```

If you want to run `edukoi` on an Apple computer with an Apple Silicon chip, you should instead do:

```
python -m pip install mediapipe-silicon
```

Finally, to install `edukoi`, you can do the following: 

```
git clone https://github.com/lucadimascolo/edukoi.git
cd edukoi
python -m pip install -e .
```

### Common issues
We observed that the `opencv-python` library has some compatibility issues with older operating systems (e.g., earlier than MacOS 11 Big Sur in the case of Apple machines). In such a case, installing a version of `opencv-python` earlier than `4.0` seems to solve the issue:

```
python -m pip install --force-reinstall "opencv-python<4"
```


## Running `edukoi`
From the `conda` within which you installed `edukoi`, simply type 

```
edukoi
```

This will prompt a browser window for selecting the image(s) to sonify. If you select multiple files, you can switch between the various images using the left and right arrows.
