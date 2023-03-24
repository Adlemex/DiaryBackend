from firebase_admin import credentials, messaging
import firebase_admin
cred = credentials.Certificate("./diary-b2ba2-firebase-adminsdk-nvon7-1be3dce4d4.json")
default_app = firebase_admin.initialize_app(cred)
topic = "marks_" + str(20)
print(topic)
message = messaging.Message(
        data={"type": "marks"},
        topic=topic)
messaging.send(message)
