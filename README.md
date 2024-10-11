![GitHub language count](https://img.shields.io/github/languages/count/ADv0rnik/SpecReader?style=flat-square)
[![Python 3.12](https://img.shields.io/badge/python-3.12-blue.svg)](https://www.python.org/downloads/release/python-312/)

### Gamma Analytics

A web application for simulate gamma source localization using bayessian inference and Monte Carlo simulations.  

#### Usage

The application requires Python version 3.11 or older. To install the application on your local machine, please follow these steps:
1. clone the repo using comand
 ```commandline
git clone https://github.com/ADv0rnik/Gamma_analytics.git
 ```
or (Use a password-protected SSH key)
```commandline
git clone git@github.com:ADv0rnik/Gamma_analytics.git
```

2. Install and activate virtual environment.
For UNIX-based systems:
```commandline
   python -m venv venv
   source venv/bin/activate
```
For Windows OS:
```commandline
python virtualenv venv
venv/Scripts/activate
```
3. Install dependencies `pip install -r requirements.txt` 
4. Create a `.env` file to store project configurations. Refer to `.env_example` for more information on available variables. Set the following values:
- PROJECT_HOST=127.0.0.1
- PROJECT_PORT=8000
5. Once the environment settings are defined, run the following command: `python main.py`
