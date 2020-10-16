# TMOS APP

This simple application logs data for the TMOS sensors together with Vicon position data

## Installation

Clone project to a folder of choice

```
> git clone git@gitlab.ethz.ch:tmos_iis/tmos_app.git
```

### Create conda/python environment

If you want you can create an environment for the project

```
> conda create -n [env_name] python=3.8
> conda activate [env_name]
```

Use the package manager [pip](https://pip.pypa.io/en/stable/) to install dependencies.

```bash
> pip install requirements.txt
```

### Vicon installation

This application uses the [Vicon SDK](https://www.vicon.com/software/datastream-sdk/?section=downloads). Download the newest version (> 1.11.0) for Python support. The current version only works on Windows machines.

Install the python data stream library <em>vicon_dssdk</em> by running the configuration file (in the installation folder).
Make sure the desired environment is activated (`conda activate [env_name]`)

```
> C:\Program Files\Vicon\DataStream SDK\Win64\Python\install_vicon_dssdk.bat
```

You can test the installation by running a simple python script

```python
from vicon_dssdk import ViconDataStream

client = ViconDataStream.Client() # Create Vicon DataStream object
print('Version', client.GetVersion()) # Print SDK version
```

### Required folders

The output logs will be saved in the `output/` folder. Create one if it does not already exist. Not creating one will crash the program.

## Usage

Just run the main python script `QtMain.py` and have fun!

```
> python QtMain.py
```