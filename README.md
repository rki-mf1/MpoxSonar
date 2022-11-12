# MPXRadar-frontend
MonkeyPoxRadar frontend codebase.

MPXSonar intregated under `pages/libs` (Git subtree)

# Installation
1. Clone this project
```
git clone https://github.com/ferbsx/MPXRadar-frontend.git
```
2. We use conda package manager (also work with [mamba](https://mamba.readthedocs.io/en/latest/installation.html)) to initiate python environment.
```
conda create -n mpxradar python=3.9 poetry fortran-compiler emboss=6.6.0
conda activate mpxradar
```
3. Next, we use [poetry](https://python-poetry.org/docs/basic-usage/) to install/manage dependencies of the project.
```
cd MPXRadar-frontend
poetry install
```
4. By default, MPXSonar expects the file ".env" and is located in the current root directory. Please change the example ".env.template" to ".env".
```
cp .env.template .env
```
The ".env" variable can then be set according to the environment.

# Start App.

Right now we can start application by using below command.
```
python app.py
```

----

Quick Demo, please run below.
```
python example.app.py
```
