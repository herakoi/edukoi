# edukoi

## Installation
To install `edukoi`, you can do the following: 

```
git clone https://github.com/lucadimascolo/edukoi.git
cd edukoi
python -m pip install -e .
```

You than need to install the `fluidsynth` library as:
```
conda install -c conda-forge fluidsynth
```

Finally, you need to install `mediapipe`,

```
python -m pip install mediapipe
```

If you are running `edukoi` on an Apple computer with an Apple chip, you should instead do

```
python -m pip install mediapipe-silicon
```

## Running `edukoi`
From the `conda` within which you installed `edukoi`, simply type 

```
edukoi
```

This will prompt a browser window for selecting the image(s) to sonify. If you select multiple files, you can switch between the various images using the left and right arrows.
