# Sento Processing

*This project is part of Sento's backend*.

A Natural Language Processing tool designed to perform sentiment analysis
on tweets and store the results obtained.

# Table of contents

# Prerequisites

Sento Processing requires a spaCy model that categorizes text based on the possible sentiment
that it holds. The model must return the probabilities of three categories:

- `P` for positive sentiment.
- `N` for negative sentiment.
- `NEU` for neutral sentiment.

If you wish to create a spaCy model that can perform this task, in the `sento_processing/training`
directory you have some scripts used to develop a model for performing sentiment analysis of
tweets written in spanish. Treat them as an example that may be outdated, as the spaCy team could
have changed their API and those scripts may no longer work. You can store your models in the
`models` directory in the repository root, this directory will be ignored by git.

Processing requires a PostgreSQL database initialised previously using the instructions
available in [Sento API's readme](https://github.com/robgc/sento-api).

# Executing the tool

## Choosing your environment

You have two options:

- Running the Docker container using Docker Compose: `docker-compose up -d`.
  You need the following software installed:
  - _Docker Engine 17.12.0 or greater required_.
  - _Docker Compose 1.18.0 or greater required_.

- Running locally on your machine, requiring:
  - Python 3.7 or greater.
  - Pipenv.

## Configuring the tool

Create a `config.ini` file from a copy of `config.example.ini` and adjust
the configuration according to your needs. If you use the PostgreSQL container
provided in Sento API instructions, let the default value of `sento-db` in the
`[postgres].host` section of your `config.ini`.

## Running the tool

- **With Docker**: run `docker-compose up -d`, this will compile the container image for you if
  you have not done it previously. If you make any changes to your `config.ini` after running
  the container you will need to stop it, remove it and recreate the container's image before
  creating another container instance. This container will try to connect
  to the `sento-net` Docker network, where the PostGIS container is listening for connections.

- **Running locally**:
  - Install the necessary dependencies in a virtual environment with `pipenv sync`.
  - Run the following command `pipenv run sento_processing/main.py`, this will start the tool.

# Acknowledgements

The training and evaluation datasets used for creating models for Sento Processing come from
the Spanish Society for Natural Language Processing (SEPLN, in Spain). They were made for
the Workshop on Semantic Analysis at SEPLN (TASS, in Spain). You can download them
from their [official website](http://www.sepln.org/workshops/tass/).

# License

The source code of this project is licensed under the GNU Affero General Public License v3.0.
