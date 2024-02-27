
<h3 align="center">School Management System</h3>

<div align="center">

  ![Status](https://img.shields.io/badge/status-active-success.svg)
  ![GitHub issues](https://img.shields.io/github/issues/lesalami/lms_backend?color=yellow)
  ![GitHub pull requests](https://img.shields.io/github/issues-pr/lesalami/lms_backend?color=success)
  [![License](https://img.shields.io/badge/license-Proprietary-blue.svg)](/LICENSE)


</div>

# School Management System

A comprehensive management system for basics school including curriculum and administrative sections. A major part being the financial management aspects.
## Description
A comprehensive management system for  basics school including curriculum and administrative sections. A major part being the financial management aspects.

## Import Update:
* The student endpoint `/api/curriculum` has a filter parameter that is not on Swagger. The key is `student_class` and the value is the ID of the Class for which you wish to filter

## Running the Code Locally
To run the application outside docker compose(This assumes you are not new to django and understands how the django framework works well.), you will need to setup the following
* The PostgreSQL database or any other database and change the settings variables to match
* Run the application with the django management command


## Running Docker Compose
* Make sure docker and docker-compose are installed on your system
* Clone the project and switch to preferred branch
* Set the `EMAIL_HOST_USER` and `EMAIL_HOST_PASSWORD` in the docker-compose.yml file. In case you are using any email server different from GMAIL, you can change the `EMAIL_HOST` and `EMAIL_PORT` as well. (Using the EMAIL credentials in the compose environmental variables was failing the smtp connection, hence I left it in the settings.py file.)
* Start the project with 
    ```bash
    docker-compose up --build
    ```
    The above command is a combination of 
    ```bash
    docker-compose build
    ``` 
    and 
    ```bash
    docker-compose up
    ```
* When the docker container starts running successfully, visit the Swagger API documentation on `http://localhost:8056/api/docs` via the browser. The app is being served on port `8056` hence admin can be accessed on `http://localhost:8056/admin`.
* To run any migrations, run 
    ```bash
    docker-compose run --rm app sh -c "python manage.py migrate"
    ```
* To run tests, run 
    ```bash
    docker-compose run --rm app sh -c "python manage.py test"
    ```
* To create a superuser, run 
    ```bash
    docker-compose run --rm app sh -c "python manage.py createsuperuser"
    ```
* To create students with test data, run 
    ```bash
    docker-compose run --rm app sh -c "python manage.py create_students"
    ```
* To create teachers with test data, run 
    ```bash
    docker-compose run --rm app sh -c "python manage.py create_staff"
    ```
* To create financial data (income and expenditure), run
    ```bash
    docker-compose run --rm app sh -c "python manage.py create_transactions"
    ```


## THE END

