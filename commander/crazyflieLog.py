from cflib.crazyflie.log import LogConfig
import os
import csv
from cflib.utils import uri_helper,encoding
pose_fieldnames = ['Timestamp', 'stateEstimateZ.x', 'stateEstimateZ.y', 'stateEstimateZ.z', 'stateEstimateZ.vx', 'stateEstimateZ.vy', 'stateEstimateZ.vz', 'stateEstimateZ.qw','stateEstimateZ.qx', 'stateEstimateZ.qy', 'stateEstimateZ.qz', 'stateEstimateZ.rateRoll', 'stateEstimateZ.ratePitch', 'stateEstimateZ.rateYaw']
pose_logs=[]

class Pose_Log:
    def __init__(self, timestamp, x, y, z, vx, vy, vz, qw, qx, qy, qz, rollrate, pitchrate, yawrate):
        self.timestamp=timestamp
        self.x=x
        self.y=y
        self.z=z
        self.vx=vx
        self.vy=vy
        self.vz=vz
        self.qw=qw
        self.qx=qx
        self.qy=qy
        self.qz=qz
        self.rollrate=rollrate
        self.pitchrate=pitchrate
        self.yawrate=yawrate

    def saveVars(self):
        return ([self.timestamp,self.x,self.y,self.z,self.vx,self.vy,self.vz,self.qw,self.qx,self.qy,self.qz,self.rollrate,self.pitchrate,self.yawrate])

def pose_log_callback(timestamp, data, logconf):
    quat_arr = encoding.decompress_quaternion(data['stateEstimateZ.quat'])
    pose_logs.append(Pose_Log(timestamp, data[pose_fieldnames[1]], data[pose_fieldnames[2]], data[pose_fieldnames[3]], data[pose_fieldnames[4]], data[pose_fieldnames[5]], data[pose_fieldnames[6]], quat_arr[0], quat_arr[1], quat_arr[2], quat_arr[3], data[pose_fieldnames[11]], data[pose_fieldnames[12]],  data[pose_fieldnames[13]]))
    
def start_pose_log(cf):
    log_conf = LogConfig(name='Position', period_in_ms=50)

    log_conf.add_variable('stateEstimateZ.x', 'int16_t')
    log_conf.add_variable('stateEstimateZ.y', 'int16_t')
    log_conf.add_variable('stateEstimateZ.z', 'int16_t')
    log_conf.add_variable('stateEstimateZ.vx', 'int16_t')
    log_conf.add_variable('stateEstimateZ.vy', 'int16_t')
    log_conf.add_variable('stateEstimateZ.vz', 'int16_t')
    log_conf.add_variable('stateEstimateZ.quat', 'uint32_t')
    log_conf.add_variable('stateEstimateZ.rateRoll', 'int16_t')
    log_conf.add_variable('stateEstimateZ.ratePitch', 'int16_t')
    log_conf.add_variable('stateEstimateZ.rateYaw', 'int16_t')
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

def outputLogs(startTime, TINYMPC):
    if not os.path.exists("logs"):
        os.makedirs("logs")
    if TINYMPC:
        prefix='tinympc'
    else:
        prefix='pid'
    with open(f"logs/{prefix}_pose_log_{startTime.strftime('%Y-%m-%d_%H-%M-%S')}.csv", 'w', newline='') as csvfile:
        writer = csv.DictWriter(csvfile, fieldnames=pose_fieldnames)
        writer.writeheader()
        for log in pose_logs:
            writer.writerow({pose_fieldnames[0]:log.timestamp,pose_fieldnames[1]:log.x,pose_fieldnames[2]:log.y,pose_fieldnames[3]:log.z,pose_fieldnames[4]:log.vx,pose_fieldnames[5]:log.vy,pose_fieldnames[6]:log.vz,pose_fieldnames[7]:log.qw,pose_fieldnames[8]:log.qx,pose_fieldnames[9]:log.qy,pose_fieldnames[10]:log.qz,pose_fieldnames[11]:log.rollrate,pose_fieldnames[12]:log.pitchrate,pose_fieldnames[13]:log.yawrate})
    with open(f"logs/{prefix}_motor_log_{startTime.strftime('%Y-%m-%d_%H-%M-%S')}.csv", 'w', newline='') as csvfile:
        writer = csv.DictWriter(csvfile, fieldnames=motor_fieldnames)
        writer.writeheader()
        for log in motor_logs:
            writer.writerow({motor_fieldnames[0]:log.timestamp, motor_fieldnames[1]:log.m1, motor_fieldnames[2]:log.m2, motor_fieldnames[3]:log.m3, motor_fieldnames[4]:log.m4})
