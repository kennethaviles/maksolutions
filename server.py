import os
from flask import Flask, request, url_for
from twilio.util import TwilioCapability
import twilio.twiml
from twilio.rest import TwilioRestClient

# Account Sid and Auth Token can be found in your account dashboard
ACCOUNT_SID = 'ACXXXXXXXXXXXXXXXXXXXXXXXXXXXXXX'
AUTH_TOKEN = 'YYYYYYYYYYYYYYYYYYYYYYYYYYYYYYYY'

# TwiML app outgoing connections will use
APP_SID = 'APZZZZZZZZZZZZZZZZZZZZZZZZZZZZZZZZ'

CALLER_ID = '+12345678901'
CLIENT = 'jenny'

app = Flask(__name__)

@app.route('/token')
def token():
  account_sid = os.environ.get("ACCOUNT_SID", ACCOUNT_SID)
  auth_token = os.environ.get("AUTH_TOKEN", AUTH_TOKEN)
  app_sid = os.environ.get("APP_SID", APP_SID)

  capability = TwilioCapability(account_sid, auth_token)

  # This allows outgoing connections to TwiML application
  if request.values.get('allowOutgoing') != 'false':
     capability.allow_client_outgoing(app_sid)

  # This allows incoming connections to client (if specified)
  client = request.values.get('client')
  if client != None:
    capability.allow_client_incoming(client)

  # This returns a token to use with Twilio based on the account and capabilities defined above
  return capability.generate()

@app.route('/call', methods=['GET', 'POST'])
def call():
  """ This method routes calls from/to client                  """
  """ Rules: 1. From can be either client:name or PSTN number  """
  """        2. To value specifies target. When call is coming """
  """           from PSTN, To value is ignored and call is     """
  """           routed to client named CLIENT                  """
  resp = twilio.twiml.Response()
  # from_value = request.values.get('From')
  from_value = "+12018174217"
  to = request.values.get('To')

  account_sid = os.environ.get("ACCOUNT_SID", ACCOUNT_SID)
  auth_token = os.environ.get("AUTH_TOKEN", AUTH_TOKEN)
  app_sid = os.environ.get("APP_SID", APP_SID)

  try:
    twilio_client = TwilioRestClient(account_sid, auth_token)
    resp.say("created client")
  except Exception, e:
    msg = 'Missing configuration variable: {0}'.format(e)
    resp.say(msg)
    return str(resp)

  try:
    twilio_client.calls.create(from_=from_value,to=to,url=url_for('.outbound', _external=True))
    resp.say("created call")
  except Exception, e:
    msg = str(e)
    resp.say(msg)
    return str(resp)

  return str(resp)

"""
  
  if not (from_value and to):
    return str(resp.say("Invalid request"))
  from_client = from_value.startswith('client')
  caller_id = os.environ.get("CALLER_ID", CALLER_ID)

  if not from_client:
    # PSTN -> client
    resp.say("first")
    resp.dial(callerId=from_value).client(CLIENT)
  elif to.startswith("client:"):
    # client -> client
    resp.say("second")
    resp.dial(callerId=from_value).client(to[7:])
  else:
    # client -> PSTN
    resp.say("third")
    with resp.gather(numDigits=1, action=url_for('menu'), method="POST") as g:
      # resp.dial(to, callerId=caller_id, action=url_for("outbound"))
      g.dial(to, callerId=caller_id)
  return str(resp)
"""

# method called when a call is made
@app.route('/outbound', methods=['POST'])
def outbound():
  resp = twilio.twiml.Response()
  with resp.gather(numDigits=1, action=url_for('menu'), method="POST") as g:
    # resp.dial(to, callerId=caller_id, action=url_for("outbound"))
    g.say("Por favor presione el numero 1 si me escucha, o undir 2 si esta ocupado", voice="alice",language="es-ES")

  return str(resp)

@app.route('/menu', methods="POST")
def menu():
  option = request.form['Digits']
  actions = {'1': _activate_Speaker,
             '2': _not_Available}
  if actions.has_key(option):
    response = twilio.twiml.Response()
    action[option](response)
    return str(response)

  return _redirect()

@app.route('/', methods=['GET', 'POST'])
def welcome():
  resp = twilio.twiml.Response()
  resp.say("Welcome to the MAK Solutions Testing ground")
  return str(resp)

#Private methods

#Will activate the speaker
def _activate_Speaker(response):
  response.say("Activate speaker")
  return response

def _not_Available(response):
  response.say("Sorry not available")
  response.hangup()
  return response

def _redirect():
  response = twilio.twiml.Response()
  response.say("Returning to the menu")
  response.redirect(url_for('outbound')

  return str(response) 

if __name__ == "__main__":
  port = int(os.environ.get("PORT", 5000))
  app.run(host='0.0.0.0', port=port, debug=True)
