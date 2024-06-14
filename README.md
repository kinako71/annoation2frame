# anotation2frame

This repository provides programs which links human annotations to each frame of videos.

### Requirements

Please install ffprobe and python.
Pandas, numpy and ffmpeg packages are required.

### Annoation
In this script, ELAN usage is assumed.
Please output ELAN annotation as shown in the figure below.
![test](elan_output.png)

### Step1 - Get data of each frame

Run ffprobe and you will get the data of pts/pts_time/pkt_duration_time.
Make a directory under "InputData/", and put videos under the directory.
Finally run "ffprobe.py".

```
python ffprobe.py -d DIRECTORY_NAME
```

If you just want to try running the script, please replace DIRECTORY_NAME to "Sample"

### Step2 - Link ffprobe data to annotation

Please set the name of the anotation file the same as the name of the video file.
Here, the results of ffprobe and annotation are merged.
Annotation is assumed to be produced using ELAN.
If you are using another annotation tool, you may need to modify the script.
Make a directory under "OutputData/ELAN" and name the same as video directory.
And put annotations under the directory corresponding to videos.
Finally run annotation.py like below.

```
python annotation.py -d DIRECTORY_NAME
```

We process each row in ELAN annotation in for loops.
In each raw, find the frame index of which “pts_time” is closest to “Begin Time” (begin_ind)
Similarly, find the frame index of which “pts_time” is closest to “End Time”(end_ind)
Fill frames between begin_ind and end_ind with the annotation of the row.
