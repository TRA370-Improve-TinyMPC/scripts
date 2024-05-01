# -*- coding: utf-8 -*-
#
#     ||          ____  _ __
#  +------+      / __ )(_) /_______________ _____  ___
#  | 0xBC |     / __  / / __/ ___/ ___/ __ `/_  / / _ \
#  +------+    / /_/ / / /_/ /__/ /  / /_/ / / /_/  __/
#   ||  ||    /_____/_/\__/\___/_/   \__,_/ /___/\___/
#
#  Copyright (C) 2018 Bitcraze AB
#
#  This program is free software; you can redistribute it and/or
#  modify it under the terms of the GNU General Public License
#  as published by the Free Software Foundation; either version 2
#  of the License, or (at your option) any later version.
#
#  This program is distributed in the hope that it will be useful,
#  but WITHOUT ANY WARRANTY; without even the implied warranty of
#  MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
#  GNU General Public License for more details.
# You should have received a copy of the GNU General Public License
# along with this program. If not, see <https://www.gnu.org/licenses/>.
"""
Simple example that connects to one crazyflie (check the address at the top
and update it to your crazyflie address) and uses the high level commander
to send setpoints and trajectory to fly a figure 8.

This example is intended to work with any positioning system (including LPS).
It aims at documenting how to set the Crazyflie in position control mode
and how to send setpoints using the high level commander.
"""
import sys
import os
import time

import cflib.crtp
from cflib.crazyflie import Crazyflie

from cflib.crazyflie.mem import MemoryElement
from cflib.crazyflie.mem import Poly4D
from cflib.crazyflie.syncCrazyflie import SyncCrazyflie
from cflib.utils import uri_helper
import csv
import matplotlib.pyplot as plt
import numpy as np
# from traj_fig8_single import trajectory_points
import datetime
# URI to the Crazyflie to connect to
uri = uri_helper.uri_from_env(default='radio://0/90/2M')
HEIGHT=0.4

from crazyflieLog import start_pose_log, start_motor_log, outputLogs


def upload_trajectory(cf, trajectory_id, trajectory):
    trajectory_mem = cf.mem.get_mems(MemoryElement.TYPE_TRAJ)[0]
    trajectory_mem.trajectory = []

    total_duration = 0
    for row in trajectory:
        duration = row[0]
        x = Poly4D.Poly(row[1:9])
        y = Poly4D.Poly(row[9:17])
        z = Poly4D.Poly(row[17:25])
        yaw = Poly4D.Poly(row[25:33])
        trajectory_mem.trajectory.append(Poly4D(duration, x, y, z, yaw))
        total_duration += duration

    upload_result = trajectory_mem.write_data_sync()
    if not upload_result:
        print('Upload failed, aborting!')
        sys.exit(1)
    cf.high_level_commander.define_trajectory(trajectory_id, 0, len(trajectory_mem.trajectory))
    return total_duration

def run_sequence(cf, trajectory_id, duration, timescale):
    commander = cf.high_level_commander
    relative = True
    commander.start_trajectory(trajectory_id, timescale, relative)
    time.sleep(duration)
    commander.stop()

def csv_to_array(filename):
    data_2d = []
    with open(filename, 'r') as csvfile:
        reader = csv.reader(csvfile, quoting=csv.QUOTE_NONNUMERIC)
        # header = next(reader)
        for row in reader: # each row is a list
            data_2d.append(row)
    return data_2d

def take_off(cf):
    commander = cf.high_level_commander
    commander.takeoff(HEIGHT, 2.0)
    time.sleep(3)

def land(cf):
    commander = cf.high_level_commander
    commander.land(0.0, 1.0)
    time.sleep(2)
    commander.stop()

def go_to(cf, x, y, z, duration):
    commander = cf.high_level_commander
    commander.go_to(x, y, z, 0, duration, relative=False)



TINYMPC=True
if __name__ == '__main__':
    if len(sys.argv) !=2:
        print("Usage: python3 autonomous_sequence.py [polynomials.csv]")
        exit()
    startTime=datetime.datetime.now()
    cflib.crtp.init_drivers()
    trajectory=csv_to_array(sys.argv[1])
    time.sleep(5)
    # x_ref = np.array([point[0] for point in trajectory_points])
    # y_ref = np.array([point[1] for point in trajectory_points])
    with SyncCrazyflie(uri, cf=Crazyflie(rw_cache='./cache')) as scf:
        cf = scf.cf
        trajectory_id = 1
        duration = upload_trajectory(cf, trajectory_id, trajectory)
        cf.param.set_value('stabilizer.controller', '1')
        # if TINYMPC==True:
        #     cf.param.set_value('stabilizer.controller', '5')
        pose_log=start_pose_log(cf)
        motor_log=start_motor_log(cf)
        take_off(cf)
        go_to(cf, 0, 0, HEIGHT, 1.0)
        # run_sequence(cf, trajectory_id, duration, 1)
        pose_log.stop()
        motor_log.stop()
        cf.param.set_value('stabilizer.controller', '1')
        land(cf)

    outputLogs(startTime)
    # x=[log.x for log in pose_logs]
    # y=[log.y for log in pose_logs]
    # if TINYMPC==True:
    #     plt.plot(x, y, label="tinympc")
    # else:
    #     plt.plot(x, y, label="pid")
    # plt.plot(x_ref, y_ref, label="ground truth")
    # plt.legend()
    # plt.show()
