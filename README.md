# PeerScout

## Configuration

### AWS Credentials and Configuration

Create `~/.aws/credentials` and populate the credentials, e.g.:

```ini
[default]
aws_access_key_id=<key id>
aws_secret_access_key=<access key>
```

You may also create `~/.aws/config`:

```ini
[default]
region=<region>
```

### App Configuration

Copy `app-example.cfg` to `app.cfg` and make the necessary configuration changes.

When using Docker for development, the configuration file is `app-dev.cfg` instead.
It would very much have the same config but the database should point to the `db` service (defined in [docker-compose.override.yml](docker-compose.override.yml)).

## Development with Docker

### Pre-requisites (with Docker)

* [Docker](https://www.docker.com/) and [Docker Compose](https://docs.docker.com/compose/)

### Create / Migrate Schema (with Docker)

```bash
make migrate-schema
```

### Populate Database (with Docker)

This will download updates from AWS and populate the database with it. This may take a while. It will also download data from Crossref, which might fail, which is 'okay'.

```bash
make update-data-and-reload
```

### Data Directory

Downloaded files and cache are stored to the `.data` directory. Which in development is mounted to the host. To make the directory writable by the Docker user (`elife`) call (writable to all users):

```bash
make fix-data-permissions
```

### Start

```bash
make start
```

## Development without Docker

### Pre-requisites (without Docker)

* Python 3 (including dev dependencies, e.g. `python3-dev` on Ubunutu / Debian)
* system dev dependencies (e.g. `build-essential`)
* [PostgreSQL](https://www.postgresql.org/) (although [SQLite](https://sqlite.org/) may work too)
* [Node.js](https://nodejs.org/) and [npm](https://www.npmjs.com/)

### Setup (without Docker)

#### Python Dependencies

##### A) Using Local Virtual Environment

If you want to use a separate virtual environment (`venv`) for this project.

```bash
./install.sh
source venv/bin/activate
```

##### B) Using Your Own Virtual Environment

Assuming you already created and switched to your own virtual environment.

```bash
for line in $(cat requirements.txt); do pip install $line; done
```

Download SpaCy models (~1 GB).

```bash
python -m spacy.en.download all
```

#### Database

The recommended database is [PostgreSQL](https://www.postgresql.org/).

Assuming you want to create a database _reviewer_suggestions_db_ with the user _reviewer_suggestions_user_ and password 'password', you may use the following commands as a guidance:

```bash
sudo -u postgres psql -c "create user reviewer_suggestions_user;"
sudo -u postgres psql -c "create database reviewer_suggestions_db;"
sudo -u postgres psql -c "alter user reviewer_suggestions_user with encrypted password 'password';"
sudo -u postgres psql -c "grant all privileges on database reviewer_suggestions_db to reviewer_suggestions_user;"
```

#### Create / Update Database Schema

```bash
python -m peerscout.preprocessing.migrateSchema
```

#### Populate Database

This will download updates from AWS and populate the database with it. This may take a while. It will also download data from Crossref, which might fail, which is 'okay'.

```bash
python -m peerscout.preprocessing.updateDataAndReload
```

#### Compile Client

```bash
cd client
npm install
npm run bundle
```

### Start Server

```bash
python -m peerscout.server
```

Then go to [http://localhost:8080/](http://localhost:8080/). (If you are getting a 'Not Found' error you may not have compiled the client)

The server will provide the REST API [http://localhost:8080/api/](http://localhost:8080/api/) and serve the static client bundle.

### Start Client Dev Server

Use this option to develop the client, in addition to the python server (which will still provide the API).

```bash
cd client
npm start
```

Then server will be availabe under [http://localhost:8081/](http://localhost:8081/).

### Tests

#### Run All Tests

```bash
./project_tests.sh
```

#### Python Tests

```bash
pytest
```

To watch tests, run `pytest-watch` instead.

## JavaScript Tests

```bash
cd client
npm test
```

Watch:

```bash
cd client
npm run ~test
```
