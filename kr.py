from firebase_admin import credentials, messaging

cred = credentials.Certificate("./diary-b2ba2-firebase-adminsdk-nvon7-1be3dce4d4.json")
default_app = firebase_admin.initialize_app(cred)
topic = "kr_" + str(18)
print(topic)
message = messaging.Message(
        data={"type": "kr_test"},
        topic=topic)
messaging.send(message)
