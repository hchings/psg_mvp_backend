<p align="center">
  <a href="https://angular.io/">
    <img src="https://surgi.fyi/assets/images/design/surgi_mobile_auth.png" alt="Logo" width=72 height=72>
  </a>
  <h2 align="center">Surgi MVP Backend</h3>
</p>

This is the RESTful web backend for Surgi MVP consisted of the following containers.
Please refer to `docker-compose.yml` (for dev) or `docker-compose-prod.yml` (for production) for details.

1. `web` (Django web service)
2. `mongo` (core database)
3. `cache` (memory cache)
4. `celery`
5. `redis`

We also use [Algolia](https://www.algolia.com/) as the managed ElasticSearch for both dev and prod.

## A. Prerequisites
Install [docker](https://docs.docker.com/) on your local environment. 

## B. To Develop
### B.1 Local Setup
Clone to repo to your local env and run the following command:
```sh
$ docker-compose up web
```
Note that when the container is first created, the below commands will be run:
```sh
$ python manage.py makemigrations
$ python manage.py migrate
```
 Make sure to run the below command if you want to use the admin page:
```sh
$ python manage.py createsuperuser
```

To rebuild the docker image:
```
$ docker-compose build web
```

When running, the **Admin page** of the backend by default will be served at: `http://localhost:8000/admin`, and the Swagger Doc (Interactive API Doc) is at `http://localhost:8000`.

### B.2 To Restore Data into local MongoDB
First, put two given unzipped folders into the corresponding place:
1. Put `dump/` under the top folder (the folder where README.md resides)
2. Put `media/` under **psg_mvp_backend/** (in parallel to **fixtures/**)

Then, run the backend (if you haven't, please refer to B.1.1) and step into mongoDB container to run the following commands:
```
$ mongorestore dump/
```
If your local mongoDB already have data, you'll need to run this first:
```
$ mongo
$ use core_db
$ db.dropDatabase()
```


## C. To Deploy to Production
### C.1 To Run
The production is using a typical Djagno settings as below:
- one container for Nginx, take in and balance requests. This is a standard nginx image which can be configured through nginx.conf.
- another is Django + Gunicorn (they always go together), no port exposed

Set IP=<your external IP> in your env variable.

1. Collect staticfiles
    ```bash
    python manage.py collectstatic
    ```
2. Start/build containers
    ```bash
    docker-compose -f docker-compose-prod.yml up -d nginx
    ```
    
The backend will now be served at `<your ip>:8000`.

**[Important!!]** On production server, ensure you have a `security/` folder in the same folder as `Dockerfile.prod` which contains crt from [ZeroSSL](https://app.zerossl.com/): 
1. certificate.crt
2. private.key


### C.2 To back up mongoDB
First ensure you have the following env variables set:
```
export IP=
export DB_USERNAME=
export DB_PW=
export PROJECT_ROOT=/root/workspace/psg_mvp/psg_mvp_backend
export DB_CONTAINER_ID=<mongo's container id>
```
Then, run:
```
sh .backup_mongo.sh
```

## D. To Test
### D.1 Run Unit Tests only
The following commands will run all the unit tests with filename `test_*.py` and show you the number of pass/failed.
```sh
$ cd ./backend
$ pytest
or
$ pytest -v --disable-pytest-warnings
```
### D.2 Run Unit Tests with Coverage Report
The coverage report is to show which parts of the code are untested.
Use the below commands to generate the coverage report:
```sh
$ cd ./backend
$ pytest --cov-report html --cov=./
```
This will generate a report under a new folder `htmlcov`.
Open the `htmlcov/index.html` to view the report.


## E. Notes for Contribution
### E.1 Suggested development flow
1. Make sure a corresponding ticket is created in  [Jira](https://surgi.atlassian.net/jira/software/projects/SURGI/boards/1/roadmap).
2. Checkout a local branch with the **ticket number** as the branch name
3. Add unittests if needed and ensure all other unittests passed
5. Please update the Swagger document and/or docstring as much as you can for readability. 
6. Create a PR and assign a reviewer
7. Note down the implementation details in either the JIRA ticket or Confluence pages. 
### E.2 Manage or step in containers
Recommended tool: [portainer](https://github.com/portainer/portainer)
To install:
```sh
docker run -d -p 9000:9000 --name portainer --restart always -v /var/run/docker.sock:/var/run/docker.sock -v portainer_data:/data portainer/portainer -H unix:///var/run/docker.sock
```
Or to run the exisiting container:
```sh
docker start portainer
```

By default, the portainer UI will be served at `http://localhost:9000`
                              

