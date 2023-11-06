import uuid

node_id = uuid.uuid4()

with open('device.txt', 'w') as f:
    f.write(str(node_id))
f.close()
