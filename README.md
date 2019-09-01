# Redpoints - Python Developer (ML Team)

Technical exam that emulates a small service working with images.


# Requirements

 - virtualenv
 - python3.7
 - docker
 - git

## Installation & Local run

 - Without docker:
 

    ```bash
    virtualenv --python=python3 redpoints/.env && source redpoints/.env/bin/activate
    ```
    ```bash
    git clone https://github.com/bighelmet7/redpoints.git redpoints/src
    ```
    ```bash
    cd redpoinst/src && pip install -r requirements
    ```
    ```bash
    python -m unittest models/tests/test_images.py && python -m unittest v1/resources/tests/test_images.py
    ```
    ```bash
    gunicorn -b 0.0.0.0:5000 application:app
    ```
 - With docker:
    ```bash
    docker-compose up
    ```
## Project & concept

There is not templates for rendering, because this services is mostly an API logics.

The main purpose of the project is basically a technical exam for RedPoints where reflects the Python Backend skills. All the endpoints are for image treatment: getting size, dimension, format, resizing images, ... And a Redis queue for pushing any kind of treatment.
 
## TODO

-images_info endpoint -> DONE
- images_info_async push elements in the redis queue. -> DONE
- batch_size endpoint -> DONE
- restrucutre the project for a larger scale -> DONE
- testing -> DONE
- docker compose -> DONE
- documentantion -> DONE
- LAST: added module **v1** where lives the API. -> DONE

##  Technology Stack

Python is the main core of all service with Flask as a webservice.
Redis as a queue messaging system.
Numpy, Pillow Flask-Restful and Pandas are the mostly important Python frameworks to mention.
Docker.

## Endpoints

| ROUTE |  METHOD | DATA
|--|--|--|
| /api/v1/images_info | POST | {"filepath": "target"} |
| /api/v1/images_info_async | POST | {"filepath": "target"} |
| /api/v1/batch_predict | POST | {"filepath": "target", "batch_size": integer} |

**NOTE**: the filepath in this case is /application/vol/dependencies/images.tsv, so any new tsv file should be cp to this route. Also you could access directly through /application/dependencies/images.tsv

## Timing

This could be different for each computer, bandwidth, ... It is just an global understanding.

```bash
bighelmet7@Abners-MacBook-Pro ~/redpoints/src (master) $ time curl -XPOST http://localhost:5000/api/v1/images_info/ -H "Content-Type: application/json" --data-binary '{"filepath": "/application/vol/dependencies/images.tsv"}'
real	4m30.942s
user	0m0.014s
sys	0m0.029s
```
```bash
bighelmet7@Abners-MacBook-Pro ~/redpoints/src (master) $ time curl -XPOST http://localhost:5000/api/v1/images_info_async/ -H "Content-Type: application/json" --data-binary '{"filepath": "/application/vol/dependencies/images.tsv"}'
{"ok": "Processing Images"}

real	0m58.715s
user	0m0.009s
sys	0m0.009s
```
```bash
bighelmet7@Abners-MacBook-Pro ~/redpoints/src (master) $ time curl -XPOST http://localhost:5000/api/v1/batch_predict/ -H "Content-Type: application/json" --data-binary '{"filepath": "/application/vol/dependencies/images.tsv", "batch_size": 5}'
{"ok": "Processing Images"}

real	14m33.282s
user	0m0.026s
sys	0m0.048s
```

## Update

- Mount a nfs for handling all the *.tsv files that contains all the ids and URLs, instead of using a docker volume or even better calling directly a S3 bucket, for speed up the I/O operations.

- batch_predict endpoint could by async and speed-up all the requests.

- Instead of doing concurrency, it would handy if there is a worker that handles all the work so the client
will retrieve a more quicker service.

- Microservice structure, the three endpoints are completely independent from each other, instead of having a 1.1GB project it could be done with an API Gateway calling those three different service so if a replica of each service is needed could be done quick and with less effort and resources.
