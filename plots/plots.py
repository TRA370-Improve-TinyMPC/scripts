import csv
import sys
import numpy as np
import matplotlib.pyplot as plt
import pandas as pd
import os
import importlib
def csv_to_array(filename):
    data_2d = []
    with open(filename, 'r') as csvfile:
        reader = csv.reader(csvfile, quoting=csv.QUOTE_NONNUMERIC)
        # header = next(reader)
        for row in reader: # each row is a list
            data_2d.append(row)
    return data_2d

def reference_trajectory(x,y, t_segments,num_segments):
    #we need to reevaluate the polynomial coefficients because when outputed at the csv file we probably lose precision
    #one way to fix this is to export to csv without removing precision and remove the precision only when you upload
    i=0
    x_curve=np.array([])
    y_curve=np.array([])
    x_segments = np.array_split(x, num_segments) #the points need to be splitted depending on how much the points can fit in num_segments polynomials
    y_segments = np.array_split(y, num_segments)
    segments=[]
    for x_seg, y_seg in zip(x_segments, y_segments):
        t_fit = np.linspace(0, 2*np.pi, x_seg.size)
        coefficients_x_seg = np.polyfit(t_fit, x_seg, 7)
        coefficients_y_seg = np.polyfit(t_fit, y_seg, 7)
        segment=np.array([])
        segment=np.concatenate((segment, (coefficients_x_seg), (coefficients_y_seg), np.zeros(16)))
        segments.append(list(segment))
    segments.append(segments[0])
    for i in range(len(t_segments)):
        t=np.linspace(0,2*np.pi,t_segments[i].size)
        x_segment_curve = np.polyval(segments[i%num_segments][0:8], t)
        y_segment_curve = np.polyval(segments[i%num_segments][8:16], t)
        x_curve=np.concatenate((x_curve,x_segment_curve))
        y_curve=np.concatenate((y_curve, y_segment_curve))
    return x_curve, y_curve

def loadPoints(inputPath):
    sys.path.append(os.path.dirname(inputPath))
    module_name = os.path.splitext(os.path.basename(inputPath))[0]
    try:
        module = importlib.import_module(module_name)
    except ImportError:
        print(f"Error: Could not import module '{module_name}'")

    data=np.array(module.trajectory_points)
    x = data[:, 0]
    y = data[:, 1]
    return x,y

def splitTimestamps(df,segmentDuration):
    timestamps = df['Timestamp'].values
    part_duration=segmentDuration*1000 # seconds to ms
    num_parts = int(np.ceil((timestamps[-1] - timestamps[0]) / part_duration))
    return np.array_split(timestamps, num_parts)

def extractData(poseDF, motorDF, firstLogLength, x_offset):
    if firstLogLength!=-1:
        poseDF=poseDF.head(firstLogLength)
        motorDF=motorDF.head(firstLogLength)
    timestamps = (poseDF['Timestamp'].values-poseDF['Timestamp'].values[0])/1000
    x=(poseDF['stateEstimateZ.x'].values-poseDF['stateEstimateZ.x'].values[0])/1000+x_offset
    y=(poseDF['stateEstimateZ.y'].values-poseDF['stateEstimateZ.y'].values[0])/1000
    vx=poseDF['stateEstimateZ.vx'].values/1000
    vy=poseDF['stateEstimateZ.vy'].values/1000
    qw=poseDF['stateEstimateZ.qw'].values/1000
    qx=poseDF['stateEstimateZ.qx'].values/1000
    rateRoll=poseDF['stateEstimateZ.rateRoll'].values/1000
    ratePitch=poseDF['stateEstimateZ.ratePitch'].values/1000
    rateYaw=poseDF['stateEstimateZ.rateYaw'].values/1000
    m1=motorDF['motor.m1']
    m2=motorDF['motor.m2']
    m3=motorDF['motor.m3']
    m4=motorDF['motor.m4']
    return {'timestamps':timestamps,'x':x,'y':y,'vx':vx,'vy':vy,'qw':qw,'qx':qx,'rateRoll':rateRoll,'ratePitch':ratePitch,'rateYaw':rateYaw,'m1':m1,'m2':m2,'m3':m3,'m4':m4}



if __name__ == "__main__":
    selected="circle" #"figure8", "circle","hover"
    if selected=='figure8':
        posePIDLogFile='logs/pid_pose_log_2024-05-08_15-08-47.csv'
        motorPIDLogFile='logs/pid_motor_log_2024-05-08_15-08-47.csv'
        poseTINYMPCLogFile='logs/tinympc_pose_log_2024-05-08_15-07-14.csv'
        motorTINYMPCLogFile='logs/tinympc_motor_log_2024-05-08_15-07-14.csv'
        num_segments=10
        segmentDuration=0.555556 # take this number from the csv file. we need to map the log file samples to the polynomial
        pointsFile="trajectories/figure8.py"
        x_offset=0
    elif selected=='circle':
        posePIDLogFile='logs/pid_pose_log_2024-05-08_16-38-22.csv'
        motorPIDLogFile='logs/pid_motor_log_2024-05-08_16-38-22.csv'
        poseTINYMPCLogFile='logs/tinympc_pose_log_2024-05-08_16-37-26.csv'
        motorTINYMPCLogFile='logs/tinympc_motor_log_2024-05-08_16-37-26.csv'
        num_segments=10
        segmentDuration=0.555555 # take this number from the csv file. we need to map the log file samples to the polynomial
        pointsFile="trajectories/circle.py"
        x_offset=1 #circle doesnt start from 0,0 but at (radius,0)
    elif selected=='hover':
        posePIDLogFile='logs/pid_pose_log_2024-05-08_15-19-22.csv'
        motorPIDLogFile='logs/pid_motor_log_2024-05-08_15-19-22.csv'
        poseTINYMPCLogFile='logs/tinympc_motor_log_2024-05-08_15-17-23.csv'
        motorTINYMPCLogFile='logs/tinympc_motor_log_2024-05-08_15-17-23.csv'
        segmentDuration=100
        firstLogLength=-1
        x_offset=0
    posePIDDF = pd.read_csv(posePIDLogFile)
    motorPIDDF=pd.read_csv(motorPIDLogFile)
    poseTINYMPCDF = pd.read_csv(poseTINYMPCLogFile)
    motorTINYMPCDF=pd.read_csv(motorTINYMPCLogFile)
    if selected=='circle' or selected=='figure8':
        timestamp_parts = splitTimestamps(posePIDDF,segmentDuration)[0:num_segments]
        firstLogLength = sum(len(row) for row in timestamp_parts) #the log files have many trials. keep one 1
        x,y=loadPoints(pointsFile)
        x_ref, y_ref=reference_trajectory(x,y,timestamp_parts,num_segments)
        pid_log=extractData(posePIDDF, motorPIDDF, firstLogLength, x_offset)
        tinympc_log=extractData(poseTINYMPCDF, motorTINYMPCDF, firstLogLength, x_offset)
        
        fig1, (ax1)=plt.subplots(1) #compare XY
        ax1.plot(x_ref,y_ref,label='Reference') 
        ax1.plot(pid_log['x'],pid_log['y'],label='PID')
        ax1.plot(tinympc_log['x'],tinympc_log['y'],label='TINYMPC')
        ax1.set_xlabel("Distance [m]")
        ax1.set_ylabel("Distance [m]")
        ax1.set_title("Trajectory")
        ax1.legend()
        fig2, (ax2,ax3)=plt.subplots(2,1) #compare X
        ax2.plot(pid_log['timestamps'],x_ref,label='Reference')
        ax2.plot(pid_log['timestamps'],pid_log['x'],label='PID')
        ax2.plot(pid_log['timestamps'],tinympc_log['x'],label='TINYMPC')
        ax2.set_xlabel("Time [s]")
        ax2.set_ylabel("Distance [m]")
        ax2.set_title("Lateral Position")
        ax2.legend()
        ax3.plot(pid_log['timestamps'],y_ref,label='Reference') #compare Y
        ax3.plot(pid_log['timestamps'],pid_log['y'],label='PID')
        ax3.plot(pid_log['timestamps'],tinympc_log['y'],label='TINYMPC')
        ax3.set_xlabel("Time [s]")
        ax3.set_ylabel("Distance [m]")
        ax3.set_title("Longitudinal Position")
        ax3.legend()
    else:
        pid_log=extractData(posePIDDF, motorPIDDF, firstLogLength, x_offset)
        tinympc_log=extractData(poseTINYMPCDF, motorTINYMPCDF, firstLogLength, x_offset)
    plt.show()