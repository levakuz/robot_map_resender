import requests
from PIL import Image
from pymongo import MongoClient
import pika
import numpy as np
import json
from matplotlib import pyplot as plt
from requests import post
from io import BytesIO


credentials = pika.PlainCredentials('admin', 'admin')
connection = pika.BlockingConnection(pika.ConnectionParameters('192.168.0.17',
                                                               5672,
                                                               '/',
                                                               credentials))
channel = connection.channel()
channel.queue_declare(queue='robot_map', durable=False)


def get_map(ch, method, properties, body):
    print(json.loads(body))
    new_message = json.loads(body)
    rows = new_message['rows']
    cols = new_message['cols']
    map = np.zeros((int(rows), int(cols)))
    for i in range(0, int(rows)):
        map[i] = new_message[str(i)]
    for i in range(0, int(rows)):
        for j in range(0, int(cols)):
            if map[i][j] == True:
                map[i][j] = 0
            else:
                map[i][j] = 255
    print(map)

    """
    for i in range(0, int(rows)):
        print(i)
        for j in range(0, int(cols)):

            if map[i][j] == 1:
                plt.scatter(i, j, c='black')
    plt.show()"""

    i = Image.fromarray(map, mode='1')
    i.save('checker.png')
    im = Image.fromarray(map)
    im = im.convert('1')
    im.show()
    fp = BytesIO()
    im.save(fp, format='PNG')
    im.save('map.png')
    fp.seek(0)
    #files = ('image', ('map.png', open('map.png', 'rb'), 'map'))
    files = {'file': ('map.png', fp, 'map')}
    foo = post('http://192.168.0.17:15032/map', files=files)


channel.basic_consume(on_message_callback=get_map, queue='robot_map', auto_ack=True)
print(' [*] Waiting for messages. To exit press CTRL+C')
channel.start_consuming()