# Marketplace

## Setup

1. Make sure you have pipenv installed, if not [install it](https://pipenv.readthedocs.io/en/latest/install/#installing-pipenv)
2. Run `pipenv shell` to go start a virtual environment
3. Run `pipenv install` to install the required libraries in the virtual environment
4. Run `python app.py` to start the program. The API will start running by default in port 5000

## Using the API

You should find the Swagger documentation for the API at [http://localhost:5000](http://localhost:5000), which should provide enough information on the endpoints and how to call them.

You can call the different endpoints using the same Swagger UI or with any console or graphical REST client, eg. cURL, Postman, Insomnia... 

## Running the tests

Run `python test.py` to run the unit tests in the console
