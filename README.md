[![CI](https://github.com/cs-uh-2012-spring26/cs-uh-2012-software-engineering-groupproject-group_c/actions/workflows/ci.yml/badge.svg)](https://github.com/cs-uh-2012-spring26/cs-uh-2012-software-engineering-groupproject-group_c/actions/workflows/ci.yml)

# Fitness Class Management and Booking API

This is a repo for a Fitness Class Management and Booking API. The API manages user authentication, Class booking and Class listing

## Live Deployment

The API is live at:

```
http://139.59.24.188:8000/
```
[View the API](http://139.59.24.188:8000/)

Deployed automatically via GitHub Actions on every
push to `main` that passes CI.

## Prerequisites

- python 3.10 or higher
- MongoDB installed. Follow [https://www.mongodb.com/docs/manual/installation/](https://www.mongodb.com/docs/manual/installation/)
to install MongoDB locally. Select the right link for your operating system.

## Tech Stack

This flask web app uses:

- [Flask-RESTX][flask-restx] for creating REST APIs. Directory structure
follows [flask restx instructions on scaling your project][flask-restx-scaling]
  - flask-restx automatically generates
  [OpenAPI specifications][openapi-specification] for your API
- [PyMongo][pymongo] for communicating with the mongodb database
- [pytest][pytest] for testing
(see [flask specific testing instructions on pytest][pytest-flask]
for more info specific to testing Flask applications)
- [mongomock][mongomock] for mocking the mongodb during unit testing

[flask-restx]: https://flask-restx.readthedocs.io/en/latest/quickstart.html
[flask-restx-scaling]: https://flask-restx.readthedocs.io/en/latest/scaling.html
[openapi-specification]: https://swagger.io/docs/specification/v3_0/about/
[pymongo]: https://pymongo.readthedocs.io/en/stable/
[pytest]: https://docs.pytest.org/en/stable/
[pytest-flask]: https://flask.palletsprojects.com/en/stable/testing/
[mongomock]: https://docs.mongoengine.org/guide/mongomock.html

## Running Locally

This assumes you are already running MongoDB (e.g., through
`brew services restart mongodb-community` on MacOS or
`sudo systemctl restart mongod` on Linux.
Find the equivalent for your OS)

### Setting up the environment

1. Check `.samplenv` file and follow the instructions there to create
your `.env` file
2. Run `make dev_env` to create a virtual environment and install dependencies

### Running the server

1. Run `make run_local_server` to run the server. This will also run the tests first.
2. Go to [http://127.0.0.1:8000](http://127.0.0.1:8000) to see it running!

You can use `ctrl-c` to stop the server.

### Testing the API server

Run `make tests` to execute the test suite and see the coverage report
in your terminal. You can also see a visual report by viewing
[/htmlcov/index.html](/htmlcov/index.html) in your browser.

### Manually activating and deactivating the virtual environment

Manually activating and deactivating the virtual environment is useful for
debugging issues and running specific scripts with flexibility (e.g., you can
run `FLASK_APP=app flask run --debug --host=0.0.0.0 --port 8000`
inside the virtual environment to directly start
the server without running tests first).

To activate the virtual environment manually:

```sh
source .venv/bin/activate
```

Alternatively, you can use:

```sh
. .venv/bin/activate
```

To deactivate the virtual environment:

```sh
deactivate
```

## Email Reminder Feature

The API supports sending reminder emails to participants booked for a class via the `POST /classes/<class_id>/remind` endpoint. This requires an AWS account with Simple Email Service (SES) configured.

### AWS SES Setup

1. Create an [AWS account](https://aws.amazon.com/) if you don't have one.
2. Go to the [Amazon SES console](https://aws.amazon.com/ses/) and verify the sender email address you want to use.
3. If your account is in the SES sandbox, you must also verify any recipient email addresses before sending.
4. Create AWS access credentials (Access Key ID and Secret Access Key) for a user with SES send permissions.

### Environment Variables for Email

Add the following to your `.env` file (see `.samplenv` for the full template):

```
SES_SENDER_EMAIL="your-verified-sender@example.com"
AWS_SES_REGION="us-east-1"  
```

```sh
aws configure
```

Alternatively, set them as environment variables:

```sh
export AWS_ACCESS_KEY_ID="your-access-key-id"
export AWS_SECRET_ACCESS_KEY="your-secret-access-key"
```

> **Note:** In unit tests, the email service is mocked and no actual emails are sent. You do not need AWS credentials to run the test suite.


## Telegram Notification Feature

The API supports sending Telegram notifications to users. This requires a Telegram bot (for the server) and the personal chat ID of the user.

### Creating a Bot with BotFather

1. Open Telegram and search for **@BotFather**
2. Start a chat and send `/start` followed by `/newbot`
3. Follow the instructions to choose a name and username for your bot
4. BotFather will give you a **bot token**. Save this for your `.env` file

### Getting Your Telegram Chat ID

1. Open Telegram and search for **@Getmyid_Work_Bot**
2. Start a chat and send `/start`
3. The bot will reply with your **chat ID**. The user should use this when registering as a member.

### Environment Variables for Telegram
Add the following to your `.env` file:

```env
TELEGRAM_BOT_TOKEN="your-bot-token-from-botfather"
```

## Design Analysis Tools (Sprint 3A)


### Generating a Class Diagram with pyreverse
`pyreverse` is included with `pylint` and can generate a starting class diagram from the source code.


1. Install pylint if not already installed:
  ```sh
  pip install pylint
  ```
2. From the project root (with the virtual environment active), run:
  ```sh
  pyreverse -o png -p FitnessApp app/
 ```
3. This outputs `classes_FitnessApp.png` in the current directory. Note that the output may need manual refinement for readability.

or use `PySequenceReverse Sequence Diagram Builder for Python` extension on VS Code.

### Generating UML Diagrams with Planttext

The Planttext diagram files for the class diagram and sequence diagrams are located in `reports/files/` that we generated and rendered the diagrams in [https://www.planttext.com/](https://www.planttext.com/)

## Best Practices

See [/docs/BestPractices.md](/docs/BestPractices.md) for advice regarding branch naming and other useful tips.

## Running with Docker

### Prerequisites
- Docker and Docker Compose installed

### Setup

1. Clone the repository:
   ```
   git clone https://github.com/cs-uh-2012-spring26/cs-uh-2012-software-engineering-groupproject-group_c.git
   cd cs-uh-2012-software-engineering-groupproject-group_c
   ```

2. Copy the sample env and fill in values:
   ```
   cp .samplenv .env
   # edit .env with your Atlas URI, JWT secret etc.
   ```

3. Start the server:
   ```
   docker compose up --build
   ```

4. The API is accessible at:
   ```
   http://localhost:8000
   ```

### Stopping

```
docker compose down
```
