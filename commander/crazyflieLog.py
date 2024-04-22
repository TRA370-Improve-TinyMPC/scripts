from cflib.crazyflie.log import LogConfig
import os
import csv
pose_fieldnames = ['timestamp','kalman.stateX','kalman.stateY']
pose_logs=[]

class Pose_Log:
    def __init__(self, timestamp, x, y):
        self.timestamp=timestamp
        self.x=x
        self.y=y

def pose_log_callback(timestamp, data):
    pose_logs.append(Pose_Log(timestamp, data[pose_fieldnames[1]], data[pose_fieldnames[2]]))

def start_pose_log(cf):
    log_conf = LogConfig(name='Position', period_in_ms=50)

    log_conf.add_variable(pose_fieldnames[1], 'float')
    log_conf.add_variable(pose_fieldnames[2], 'float')
    cf.log.add_config(log_conf)
    log_conf.data_received_cb.add_callback(pose_log_callback)
    log_conf.start()
    return log_conf

def outputLogs(startTime):
    if not os.path.exists("logs"):
        os.makedirs("logs")
    with open(f"logs/pose_log_{startTime.strftime('%Y-%m-%d_%H-%M-%S')}.csv", 'w', newline='') as csvfile:
        writer = csv.DictWriter(csvfile, fieldnames=pose_fieldnames)
        writer.writeheader()
        for log in pose_logs:
            writer.writerow({pose_fieldnames[0]:log.timestamp, pose_fieldnames[1]:log.x, pose_fieldnames[2]:log.y})
