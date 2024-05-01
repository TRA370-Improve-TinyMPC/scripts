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

def pose_log_callback(timestamp, data, logconf):
    pose_logs.append(Pose_Log(timestamp, data[pose_fieldnames[1]], data[pose_fieldnames[2]]))

def start_pose_log(cf):
    log_conf = LogConfig(name='Position', period_in_ms=50)

    log_conf.add_variable(pose_fieldnames[1], 'float')
    log_conf.add_variable(pose_fieldnames[2], 'float')
    cf.log.add_config(log_conf)
    log_conf.data_received_cb.add_callback(pose_log_callback)
    log_conf.start()
    return log_conf

motor_fieldnames = ['timestamp','motor.m1','motor.m2','motor.m3','motor.m4']
motor_logs=[]

class Motor_Log:
    def __init__(self, timestamp, m1, m2, m3, m4):
        self.timestamp=timestamp
        self.m1=m1
        self.m2=m2
        self.m3=m3
        self.m4=m4

def motor_log_callback(timestamp, data, logconf):
    motor_logs.append(Motor_Log(timestamp, data[motor_fieldnames[1]], data[motor_fieldnames[2]], data[motor_fieldnames[3]], data[motor_fieldnames[4]]))

def start_motor_log(cf):
    log_conf = LogConfig(name='Motor', period_in_ms=50)

    log_conf.add_variable(motor_fieldnames[1], 'float')
    log_conf.add_variable(motor_fieldnames[2], 'float')
    log_conf.add_variable(motor_fieldnames[3], 'float')
    log_conf.add_variable(motor_fieldnames[4], 'float')
    cf.log.add_config(log_conf)
    log_conf.data_received_cb.add_callback(motor_log_callback)
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
    with open(f"logs/motor_log_{startTime.strftime('%Y-%m-%d_%H-%M-%S')}.csv", 'w', newline='') as csvfile:
        writer = csv.DictWriter(csvfile, fieldnames=motor_fieldnames)
        writer.writeheader()
        for log in motor_logs:
            writer.writerow({motor_fieldnames[0]:log.timestamp, motor_fieldnames[1]:log.m1, motor_fieldnames[2]:log.m2, motor_fieldnames[3]:log.m3, motor_fieldnames[4]:log.m4})
