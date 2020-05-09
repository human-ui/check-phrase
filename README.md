# check-phrase

Which article should I use? Use AI to help you out.

Demo: `http://check-phrase.appspot.com`

# How to set it up for yourself

Follow [Google Cloud instructions](https://cloud.google.com/appengine/docs/flexible/python/quickstart). Below is a quick summary of what we did.

## Create a project using Google App Engine
```
gcloud components update
gcloud projects create check-phrase
gcloud app create --project=check-phrase
```
We chose `europe-west3` (Frankfurt) in the last step

## Setup

- Create a project folder: `mkdir check-phrase && cd check-phrase`
- Create a virtual environment: `python3 -m venv .venv`
- Activate it: `source .venv/bin/activate`
- Clone this repository *inside* `check-phrase` (so that `.venc` stays outside of it)

### Important setup details

- `transformers` library takes a lot of resources, so we had to go for a **flexible** environment and choose `memory_gb: 6` and `disk_size_gb: 20`.
- Notice how in `app.yaml` we set `timeout = 240`. It takes a while to download the weight for our model the first time we start this service, so if you go with the default value (30 s), it might time out and raise `[CRITICAL] WORKER TIMEOUT` error.

## Work with the app locally

- `cd check-phrase`
- `python main.py`
- Open `http://localhost:8080` in your browser and check out the app

## Deploy

`gcloud app deploy --project check-phrase` (this costs money!)

