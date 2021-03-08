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

## Usage

First, make sure you are connected to the device's WiFi `tmos_wifi`. Then just run the main python script `QtMain.py` and have fun!

```
> python QtMain.py
```