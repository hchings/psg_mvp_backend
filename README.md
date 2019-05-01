# Backend Service
This is the core RESTful web backend for the mvp consisted of multiple docker instances.
Please refer to the documents (WIP) for details.


## A. Prerequisits
Since we're developing with docker, all you need is to install [docker](https://docs.docker.com/) on your local environment. 

## B. To Run
1. Clone to code to your local env
2. Run the following command, which will start all the instances.
```sh
$ docker-compose up web
```

Make sure you've run the following commands for the initial run:
```sh
$ python manage.py makemigrations
$ python manage.py migrate
$ python manage.py createsuperuser
```

To rebuild the docker image:
```
$ docker-compose build web
```

When running, the **Admin page** of the backend by default will be served at: `http://localhost:8000/admin`, and the Swagger Doc (Interactive API Doc) is at `http://localhost:8000`.


## C. To Test
#### C.1 Unit Tests
The following commands will run all the unit tests with filename `test_*.py` and show you the number of pass/failed.
```sh
$ cd ./backend
$ pytest
or
$ pytest -v --disable-pytest-warnings
```
#### C.2 Coverage Report
The coverage report is to show which parts of the code are untested.
Use the below commands to generate the coverage report:
```sh
$ cd ./backend
$ pytest --cov-report html --cov=./
```
This will generate a report under a new folder `htmlcov`.
Open the `htmlcov/index.html` to view the report.


## D. Notes for Developemnt
#### D.1 Suggested development flow
1. Make sure you've opened a corresponding ticket in [Youtrack](https://plastic-surgery-mvp.myjetbrains.com/youtrack/dashboard?id=eeadcb37-ab59-4eb1-9ddc-903e398e712a).
2. Checkout a local branch with the **ticket number** as the branch name
3. Add your unittests and ensure a high test coverage 
4. Run all unittests
5. Add Swagger document, docstring, and update README.md if needed. 
6. Push your new branch with the code changes, create a PR, and assign a reviewer
7. Note down the implementation details in the Youtrack ticket and update its status. 
#### D.2 Manage / Develop in Containers
Recommended tool: [portainer](https://github.com/portainer/portainer)
To install:
```sh
docker run -d -p 9000:9000 --name portainer --restart always -v /var/run/docker.sock:/var/run/docker.sock -v portainer_data:/data portainer/portainer -H unix:///var/run/docker.sock
```
By default, the portainer UI will be served at `http://localhost:9000`
