### Requirements

- virtualenv
- python2
- (ngrok)[https://ngrok.com/]

### Starting up

- `clone repository`
- `cd AlexaMediTrack`
- `virtualenv .`
- `source bin/activate`
- `pip install -r requirements.txt`
- `python main.py`

in another console:

- go to ngrok location
- `./ngrok http 5000`


### Editing Alex Skill

- go to (alex skill page)[https://developer.amazon.com/alexa/console/ask]
- create new skill
- copy and paste everything in `intent_schema.json` in to the JSON editor
- save and build the Skill
- for endpoint:
  - choose HTTPS
  - copy and paste ngrok url to Default region url box
  - SSL type pick `My development endpoint is a sub-domain of a domain that has a wildcard certificate...`
