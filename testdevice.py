from db.mysqlhelper import MySQLHelper
from transcode.device import Device

device = Device()
helper = MySQLHelper()
helper.connect()
helper.insert_device(device)