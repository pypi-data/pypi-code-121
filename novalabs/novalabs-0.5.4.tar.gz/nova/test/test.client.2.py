import socketio
from flask_socketio import join_room, leave_room


# standard Python
sio = socketio.Client()
sio.connect('http://localhost:5000', wait_timeout=10)
print('my sid is', sio.sid)
sio.emit('MessageStream', {'data': {'message': 'Prise de position sur ETH', 'botId': '0071'}})
