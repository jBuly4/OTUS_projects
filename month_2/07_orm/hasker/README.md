# HaSKER for OTUS

## Description
**TASK:** Create Stackoverflow-like website.

## What is done:
- index - listing of quesions, 20 questions on a page
- minimal styling
- asking questions (only for authenticated users)
- answering questions (only for authenticated users)
- rating, answers and views stats
- rating like/dislike voting (votes only for authenticated users)
- mark correct answer (only for authenticated author of question)
- searching
- searching by tag with "tag:" prefix
- sorting by date, rating or tag
- trendings
- similar questions
- sign up, log in, log out and profile edition
- API:
  - token auth
  - get index
  - get trendings
  - get tags
  - get questions filtered for tag
  - get question
  - get answers for question
- Tests:
  - api
  - views

## Run deploy in Docker
- Clone repo
- Execute command and site will run with initial data, loaded from hasker_data.json
```commandline
make prod
```
- Open in browser http://127.0.0.1/hasker/

## Run app for develop
- Clone repo and run:
```commandline
make develop
```
- Open in browser http://127.0.0.1:8000/hasker/

## Run tests in develop
```commandline
python manage.py test --settings=hasker.settings.local
```
