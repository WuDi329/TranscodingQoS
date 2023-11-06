import mysql.connector
from transcode.video import Video
from transcode.videotask import VideoTask
from transcode.device import Device
from transcode.qosmetric import QualityOfServiceMetric
import uuid


class MySQLHelper:
    def __init__(self):
        self.host = '49.52.27.50'
        self.port = 33033
        self.user = 'wudi'
        self.password = '66666666'
        self.database = 'demo'
        self.cnx = None
        self.cursor = None

    def connect(self):
        try:
            self.cnx = mysql.connector.connect(
                host=self.host,
                port=self.port,
                user=self.user,
                password=self.password,
                database=self.database
            )
            self.cursor = self.cnx.cursor()
        except mysql.connector.Error as e:
            print(f"Failed to connect to MySQL server: {e}")
            raise

    def disconnect(self):
        self.cursor.close()
        self.cnx.close()

    def execute_query(self, query):
        self.cursor.execute(query)
        # self.cnx.commit()
        return self.cursor.fetchall()

    def execute_update(self, query, values):
        self.cursor.execute(query, values)
        self.cnx.commit()

    def execute_insert(self, query, values):
        self.cursor.execute(query, values)
        self.cnx.commit()
        return self.cursor.lastrowid

    def insert_video(self, video: Video):
        query = "INSERT INTO video (vid, path, outputpath, resolution, videocodec, bitrate, framerate, duration, audiocodec) VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s)"
        value = (video.vid, video.path, video.outputpath, video.resolution.value, video.videocodec.value,
                 video.bitrate, video.framerate, video.duration, video.audiocodec.value)
        self.execute_insert(query, value)

    def query_first_device(self):
        query = "SELECT mac FROM device LIMIT 1"
        return self.execute_query(query)

    def query_second_device(self):
        query = "SELECT mac FROM device ORDER BY deviceid DESC LIMIT 2"
        return self.execute_query(query)

    def insert_videotask(self, videotask:  VideoTask):
        query = "INSERT INTO videotask (taskid, path, outputpath, vid, duration, origincodec, outputcodec, originresolution, outputresolution, audiocodec, bitrate, framerate, mode) VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s)"
        value = (videotask.taskid, videotask.path, videotask.outputpath, videotask.vid, videotask.duration, videotask.origincodec.value, videotask.outputcodec.value,
                 videotask.originresolution.value, videotask.outputresolution.value, videotask.audiocodec.value, videotask.bitrate.value, videotask.framerate, videotask.mode.value)
        self.execute_insert(query, value)

    def insert_device(self, device: Device):
        query = "INSERT INTO device (mac) VALUES (%s)"
        value = device.macaddress
        self.execute_insert(query, (value, ))

    def insert_device_direct(self, mac):
        query = "INSERT INTO device (mac) VALUES (%s)"
        value = mac
        self.execute_insert(query, (value, ))

    def insert_metric(self, metric: QualityOfServiceMetric):
        query = "INSERT INTO metric (contractid, starttime, executiontime, videoqualitykind, audioqualitykind, originfilesize, outputfilesize, videoquality, audioquality) VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s)"
        value = (metric.contractid, metric.starttime, metric.executiontime, metric.videoqualitykind,
                 metric.audioqualitykind, metric.originfilesize, metric.outputfilesize, metric.videoquality, metric.audioquality)
        self.execute_insert(query, value)

    def contract_task(self, taskid, mac):
        query = "INSERT INTO contracttask (id, taskid, devicemac) VALUES (%s, %s, %s) "
        value = (str(uuid.uuid1()), taskid, mac)
        self.execute_insert(query, value)

    def finish_contract_task(self, id):
        query = "UPDATE contracttask SET status = 'finished' WHERE id = %s"
        value = (id)
        self.execute_insert(query, value)

    def search_mac_unfinished_videotasks(self, mac):
        """
            根据mac地址查询所有状态为pending的任务。
        """
        query = """
            SELECT  c.id, c.taskid, v.duration, v.origincodec, v.outputcodec, v.originresolution, v.audiocodec, v.bitrate, v.framerate, v.mode
            FROM contracttask c
            JOIN videotask v ON c.taskid = v.taskid
            WHERE c.devicemac = '{}' AND c.status = 'pending'
        """.format(mac)
        return self.execute_query(query)

    def search_current_mac_videotask(self, mac, taskid):
        """
            根据mac地址和taskid查询当前任务信息。
        """
        query = """
            SELECT  c.id, c.taskid, v.duration, v.origincodec, v.outputcodec, v.originresolution, v.audiocodec, v.bitrate, v.framerate, v.mode
            FROM contracttask c
            JOIN videotask v ON c.taskid = v.taskid
            WHERE c.devicemac = '{}' AND c.status = 'pending' AND c.taskid = '{}'
        """.format(mac, taskid)
        return self.execute_query(query)

    def search_specific_videotask(self, contractid):
        """
            根据taskid查询任务。
        """
        query = """
            SELECT  vt.taskid, v.path, v.outputpath, v.resolution, v.videocodec, v.bitrate, v.framerate, v.duration, v.audiocodec, vt.originresolution, vt.outputcodec, vt.bitrate, vt.mode, ct.id
            FROM contracttask ct
            JOIN videotask vt ON ct.taskid = vt.taskid
            JOIN video v ON v.vid = vt.vid
            WHERE ct.id = '{}'
        """.format(contractid)
        return self.execute_query(query)

    def update_mac_task(self, taskid, mac):
        """
            更新mac地址。
        """
        query = """
            UPDATE contracttask SET status = %s WHERE taskid = %s AND devicemac = %s
        """
        values = ('finished', taskid, mac)
        self.execute_update(query, values)
