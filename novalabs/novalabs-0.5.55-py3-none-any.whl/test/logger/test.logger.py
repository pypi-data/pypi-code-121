import socketio
from flask_socketio import join_room, leave_room


# standard Python #2
sio = socketio.Client()
sio.connect('http://localhost:5000', wait_timeout=10)
print('my sid is', sio.sid)
sio.emit('MessageStream', {'data': {'message': 'Prise de position sur ETH', 'botId': '0071'}})


# standard Python #1
sio = socketio.Client()
sio.connect('http://localhost:5000', wait_timeout=10)
print('my sid is', sio.sid)
sio.emit('MessageStream', {'data': {'message': 'Prise de position sur BTC', 'botId': '625b79e80b7b1aab05575e7d'}})
print('Message send.')