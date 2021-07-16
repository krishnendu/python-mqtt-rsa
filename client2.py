import paho.mqtt.client as mqtt
import rsa
import pickle

text = ""

clients={}
subTopics=['/fromclient1/rsa','/fromclient1']
pubTopics=['/fromclient2/rsa','/fromclient2']

def on_connect(client, userdata, flags, rc):
	global text
	global subTopics
	print("Connected with result code "+str(rc))
	client.subscribe(subTopics[1])
	client.subscribe(subTopics[0])
	text=None

def on_message(client, userdata, msg):
	global pubTopics
	global clients
	global text
	# print(msg.topic+" : "+str(msg.payload))
	if(msg.topic==subTopics[0]):
		if(msg.payload==b'GET PUBLIC KEY'):
			publicKey, privateKey = rsa.newkeys(512)
			clients[publicKey.n]=privateKey
			client.publish(pubTopics[0],pickle.dumps(publicKey))
		else:
			if(text!=None and msg.payload!=None):
				publicKey=pickle.loads(msg.payload)
				dataDict={'key':publicKey.n,'data':rsa.encrypt(text.encode(),publicKey)}
				dataByte=pickle.dumps(dataDict)
				client.publish(pubTopics[1],dataByte)
				text=None
	elif(msg.topic==subTopics[1]):
		dataDict=pickle.loads(msg.payload)
		key=dataDict['key']
		data=dataDict['data']
		privateKey=clients[key]
		decMessage = rsa.decrypt(data, privateKey).decode()
		print('Decrypted Message : ',decMessage)
		clients.pop(key,None)

client = mqtt.Client()
client.on_connect = on_connect
client.on_message = on_message

# client.connect("127.0.0.1", 1883, 60)
# client.loop_forever()
client.connect_async("127.0.0.1", 1883, 60)
client.loop_start()
while True:
	if(text==None):
		text=input('Enter Message to send : ')
		client.publish(pubTopics[0],'GET PUBLIC KEY')