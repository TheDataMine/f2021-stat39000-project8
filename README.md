# Project 8

## Setup

1. Clone the repository into your `$HOME` directory.
 ```ipython
 %%bash

 cd $HOME
 git clone git@github.com:TheDataMine/f2021-stat39000-project8.git
 ```
2. Now, install the packages into a virtual environment.
 ```ipython
 %%bash

 module unload python/f2021-s2022-py3.9.6
 cd $HOME/f2021-stat39000-project8
 poetry install
 ```
3. Finally in order to run the server, run the following from *within* your `$HOME/f2021-stat39000-project8` directory.
 ```bash
 poetry run uvicorn app.main:app --reload
 ```

 Now, this will **most likely fail**. Read the instructions from the project to get this working for project 8!
