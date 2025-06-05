from src.responder import Responder
from src.speaker import Speaker
# from src.onlineSpeaker import Speaker

responder = Responder()
speaker = Speaker()
response = responder.get_response("I will be taking you to Riverside Iowa in 24 days")
# print("Nomad says: ",response)
speaker.speak(response)

