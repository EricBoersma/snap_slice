# snap_slice

This is a work in progress. Right now, it's not fully functional. It'll read a video
and use Tensorflow to examine that video and determine which parts of a football
broadcast it's looking at. Eventually, the goal is to slice that video
into easily-uploadable clips. Unfortunately, it doesn't do that last part right now.

To install this, simply clone the repository on a system with python installed.
Installing the requirements for the project are as simple as

```bash
pip install -r requirements.txt
```

Once you've installed the requirements, you can run the slicer by running

```bash
python classify_video.py --help
```

That script accepts a number of arguments. Help will explain what each argument
does and how to pass it to the script. 

If you're trying to use this on Windows, I recommend installing [WSL](https://docs.microsoft.com/en-us/windows/wsl/install-win10).