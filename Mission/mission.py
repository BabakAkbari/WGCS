#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""
© Copyright 2015-2016, 3D Robotics.
mission_import_export.py:

This example demonstrates how to import and export files in the Waypoint file format
(http://qgroundcontrol.org/mavlink/waypoint_protocol#waypoint_file_format). The commands are imported
into a list, and can be modified before saving and/or uploading.

Documentation is provided at http://python.dronekit.io/examples/mission_import_export.html
"""
from __future__ import print_function

from dronekit import connect, VehicleMode, LocationGlobalRelative, LocationGlobal, Command
import time
import math
from pymavlink import mavutil




def readmission(vehicle,aFileName):
    """
    Load a mission from a file into a list. The mission definition is in the Waypoint file
    format (http://qgroundcontrol.org/mavlink/waypoint_protocol#waypoint_file_format).

    This function is used by upload_mission().
    """
    print("\nReading mission from file: %s" % aFileName)
    cmds = vehicle.commands
    missionlist=[]
    with open(aFileName) as f:
        for i, line in enumerate(f):
            if i==0:
                if not line.startswith('QGC WPL 110'):
                    raise Exception('File is not supported WP version')
            else:
                linearray=line.split('\t')
                ln_index=int(linearray[0])
                ln_currentwp=int(linearray[1])
                ln_frame=int(linearray[2])
                ln_command=int(linearray[3])
                ln_param1=float(linearray[4])
                ln_param2=float(linearray[5])
                ln_param3=float(linearray[6])
                ln_param4=float(linearray[7])
                ln_param5=float(linearray[8])
                ln_param6=float(linearray[9])
                ln_param7=float(linearray[10])
                ln_autocontinue=int(linearray[11].strip())
                cmd = Command( 0, 0, 0, ln_frame, ln_command, ln_currentwp, ln_autocontinue, ln_param1, ln_param2, ln_param3, ln_param4, ln_param5, ln_param6, ln_param7)
                missionlist.append(cmd)
    return missionlist


def upload_mission(vehicle,aFileName):
    """
    Upload a mission from a file.
    """
    #Read mission from file
    missionlist = readmission(vehicle,aFileName)

    print("\nUpload mission from a file: %s" % aFileName)
    #Clear existing mission from vehicle
    print(' Clear mission')
    cmds = vehicle.commands
    cmds.clear()
    #Add new mission to vehicle
    for command in missionlist:
        cmds.add(command)
    print(' Upload mission')
    vehicle.commands.upload()


def download_mission(vehicle):
    """
    Downloads the current mission and returns it in a list.
    It is used in save_mission() to get the file information to save.
    """
    print(" Download mission from vehicle")
    missionlist=[]
    cmds = vehicle.commands
    cmds.download()
    cmds.wait_ready()
    for cmd in cmds:
        missionlist.append(cmd)
    return missionlist

def save_mission(vehicle,aFileName):
    count = 0
    """
    Save a mission in the Waypoint file format
    (http://qgroundcontrol.org/mavlink/waypoint_protocol#waypoint_file_format).
    """
    print("\nSave mission from Vehicle to file: %s" % aFileName)
    #Download mission from vehicle
    missionlist = download_mission(vehicle)
    #Add file-format information
    output='QGC WPL 110\n'
    #Add home location as 0th waypoint
    home = vehicle.home_location
    output+="%s\t%s\t%s\t%s\t%s\t%s\t%s\t%s\t%s\t%s\t%s\t%s\n" % (0,1,0,16,0,0,0,0,home.lat,home.lon,home.alt,1)
    #Add commands
    for cmd in missionlist:
        count = count + 1
        commandline="%s\t%s\t%s\t%s\t%s\t%s\t%s\t%s\t%s\t%s\t%s\t%s\n" % (cmd.seq,cmd.current,cmd.frame,cmd.command,cmd.param1,cmd.param2,cmd.param3,cmd.param4,cmd.x,cmd.y,cmd.z,cmd.autocontinue)
        output+=commandline
    with open(aFileName, 'w') as file_:
        print(" Write mission to file")
        file_.write(output)
    return count

def printfile(aFileName):
    """
    Print a mission file to demonstrate "round trip"
    """
    print("\nMission file: %s" % aFileName)
    with open(aFileName) as f:
        for line in f:
            print(' %s' % line.strip())


def condition_yaw(vehicle,heading, relative=False):
    if relative:
        is_relative=1 #yaw relative to direction of travel
    else:
        is_relative=0 #yaw is an absolute angle
    # create the CONDITION_YAW command using command_long_encode()
    msg = vehicle.message_factory.command_long_encode(
        0, 0,    # target system, target component
        mavutil.mavlink.MAV_CMD_CONDITION_YAW, #command
        0, #confirmation
        heading,    # param 1, yaw in degrees
        0,          # param 2, yaw speed deg/s
        1,          # param 3, direction -1 ccw, 1 cw
        is_relative, # param 4, relative offset 1, absolute angle 0
        0, 0, 0)    # param 5 ~ 7 not used
    # send command to vehicle
    vehicle.send_mavlink(msg)


def arm_and_takeoff(vehicle,aTargetAltitude):
    """
    Arms vehicle and fly to aTargetAltitude.
    """

    print("Basic pre-arm checks")
    # Don't let the user try to arm until autopilot is ready
    while not vehicle.is_armable:
        print(" Waiting for vehicle to initialise...")
        time.sleep(1)
    # Already in air
    if vehicle.armed and vehicle.location.global_relative_frame.alt>2:
        return
    print("Arming motors")

    # Copter should arm in GUIDED mode
    vehicle.mode = VehicleMode("GUIDED")
    while not vehicle.mode.name=="GUIDED":
        vehicle.mode = VehicleMode("GUIDED")
        print("Changing mode to GUIDED...")
        time.sleep(1)
    vehicle.armed = True

    while not vehicle.armed:
        print(" Waiting for arming...")
        time.sleep(1)

    print("Taking off!")
    vehicle.simple_takeoff(aTargetAltitude) # Take off to target altitude
    # Wait until the vehicle reaches a safe height before processing the goto (otherwise the command
    #  after Vehicle.simple_takeoff will execute immediately).
    while True:
        print(" Altitude: ", vehicle.location.global_relative_frame.alt)
        if vehicle.location.global_relative_frame.alt>=aTargetAltitude*0.95: #Trigger just below target alt.
            print("Reached target altitude")
            break
        time.sleep(1)

def get_location_metres(original_location, dNorth, dEast):
    """
    Returns a LocationGlobal object containing the latitude/longitude `dNorth` and `dEast` metres from the
    specified `original_location`. The returned Location has the same `alt` value
    as `original_location`.

    The function is useful when you want to move the vehicle around specifying locations relative to
    the current vehicle position.
    The algorithm is relatively accurate over small distances (10m within 1km) except close to the poles.
    For more information see:
    http://gis.stackexchange.com/questions/2951/algorithm-for-offsetting-a-latitude-longitude-by-some-amount-of-meters
    """
    earth_radius=6378137.0 #Radius of "spherical" earth
    #Coordinate offsets in radians
    dLat = dNorth/earth_radius
    dLon = dEast/(earth_radius*math.cos(math.pi*original_location.lat/180))

    #New position in decimal degrees
    newlat = original_location.lat + (dLat * 180/math.pi)
    newlon = original_location.lon + (dLon * 180/math.pi)
    return LocationGlobal(newlat, newlon,original_location.alt)


def get_distance_metres(aLocation1, aLocation2):
    """
    Returns the ground distance in metres between two LocationGlobal objects.

    This method is an approximation, and will not be accurate over large distances and close to the
    earth's poles. It comes from the ArduPilot test code:
    https://github.com/diydrones/ardupilot/blob/master/Tools/autotest/common.py
    """
    dlat = aLocation2.lat - aLocation1.lat
    dlong = aLocation2.lon - aLocation1.lon
    return math.sqrt((dlat*dlat) + (dlong*dlong)) * 1.113195e5



def distance_to_current_waypoint(vehicle):
    """
    Gets distance in metres to the current waypoint.
    It returns None for the first waypoint (Home location).
    """
    nextwaypoint = vehicle.commands.next
    if nextwaypoint==0:
        return None
    missionitem=vehicle.commands[nextwaypoint-1] #commands are zero indexed
    lat = missionitem.x
    lon = missionitem.y
    alt = missionitem.z
    targetWaypointLocation = LocationGlobalRelative(lat,lon,alt)
    distancetopoint = get_distance_metres(vehicle.location.global_frame, targetWaypointLocation)
    return distancetopoint
def dis(vehicle, station_pos):
    distances = []
    for lat,lng in station_pos:
        distances.append(get_distance_metres(vehicle.location.global_frame, LocationGlobalRelative(float(lat), float(lng), 0)))
    return distances.index(min(distances))
def start_mission(vehicle,num,land,heading):
    station_pos = []
    for latlng in land:
        station_pos.append([latlng['lat'], latlng['lng']])
    print(dis(vehicle, station_pos))
    import_mission_filename = 'mpmissionfile.txt'
    export_mission_filename1 = 'exportedmission1.txt'
    export_mission_filename2 = 'exportedmission2.txt'
    print(" Battery: %s" % vehicle.battery)
    i=1
    k=1
    nextwaypoint = 2
    #Upload mission from file
    cmds = vehicle.commands
    cmds.clear()
    cmds.upload()
    upload_mission(vehicle,import_mission_filename)
    #Download mission we just uploaded and save to a file
    count=save_mission(vehicle,export_mission_filename1)
    j =0
    while j < num:
        print("uuiwaiofjofpajfpaojpovjpaojpojajopgahgoh")
        print("num",num)
        print("j",j)
        print(count)
        bat_flag = 0
        bat_tim = 0
        # From Copter 3.3 you will be able to take off using a mission item. Plane must take off using a mission item (currently).
        arm_and_takeoff(vehicle,10)
        print("Starting mission")

        # Reset mission set to first (0) waypoint
        vehicle.commands.next=i
        print(i)
        vehicle.commands.wait_ready()
        while not vehicle.commands.next==i:
            vehicle.commands.next=i
        print(vehicle.commands.next)

        # Set mode to AUTO to start mission
        vehicle.mode = VehicleMode("AUTO")
        while not vehicle.mode.name=="AUTO":
            vehicle.mode = VehicleMode("AUTO")
            print("Changing mode to AUTO...")
            time.sleep(1)

        # Monitor mission.
        # Demonstrates getting and setting the command number
        # Uses distance_to_current_waypoint(), a convenience function for finding the
        #   distance to the next waypoint.
        outterflag = 0
        while j < num:
            #print(j)
            if vehicle.battery.voltage<11.6 and bat_flag == 0:
                print("# WARNING: Low Battery Waiting for 10 Seconds...")
                bat_flag = 1
                bat_tim = time.time()
            if vehicle.battery.voltage>=11.6:
                bat_flag = 0
            if bat_flag==1 and (time.time()-bat_tim) >= 10:
                print("# WARNING: Returning Back to Charging Station...")
                # vehicle.commands.next=count-1
                # while not vehicle.commands.next==count-1:
                #     vehicle.commands.next=count-1
                ##############################################
                  # vehicle.commands.next=count
                  # while not vehicle.commands.next==count:
                  #     vehicle.commands.next=count
                #########################################
                    #print(vehicle.commands.next)
                break;

            nextwaypoint=vehicle.commands.next
            print('Distance to waypoint (%s): %s' % (nextwaypoint, distance_to_current_waypoint(vehicle)))
            #if nextwaypoint==count-2: #Dummy waypoint - as soon as we reach waypoint 4 this is true and we exit.
            if nextwaypoint==count:
                j = j + 1
                if(j == num):
                    #vehicle.commands.next=count-1
                    pass
                else:
                    vehicle.commands.next=k
                vehicle.commands.wait_ready()
                print("Exit 'standard' mission when start heading to final waypoint")
            time.sleep(1)
        #while vehicle.commands.next==count-1:
        #while vehicle.commands.next==count:
        ###########################################
            #print(vehicle.commands.next)
            time.sleep(1)
        print("pospos:")
        print(dis(vehicle, station_pos))
        print(station_pos[dis(vehicle, station_pos)])
        vehicle.mode = VehicleMode("GUIDED")
        while not vehicle.mode.name=="GUIDED":
            vehicle.mode = VehicleMode("GUIDED")
            print("Changing mode to GUIDED...")
            time.sleep(1)
        vehicle.simple_goto(LocationGlobalRelative(float(station_pos[dis(vehicle, station_pos)][0]), float(station_pos[dis(vehicle, station_pos)][1]), 10))
        while get_distance_metres(vehicle.location.global_frame, LocationGlobalRelative(float(station_pos[dis(vehicle, station_pos)][0]), float(station_pos[dis(vehicle, station_pos)][1]), 10)) > 2:
            print(get_distance_metres(vehicle.location.global_frame, LocationGlobalRelative(float(station_pos[dis(vehicle, station_pos)][0]), float(station_pos[dis(vehicle, station_pos)][1]), 10)))
        time.sleep(2)
        # Set mode to Land
        time.sleep(2)
        condition_yaw(vehicle,float(heading),relative=False)
        time.sleep(5)
        vehicle.mode = VehicleMode("LAND")
        while not vehicle.mode.name=="LAND":
            vehicle.mode = VehicleMode("LAND")
            print("Changing mode to LAND...")
            time.sleep(1)
        if j == num:
            print("Mission Completed...")
            break
        while(vehicle.battery.voltage<12.1):
            print("Battery Voltage: %s" %vehicle.battery)
            time.sleep(2)
        k=1
        print("kkkkkkkkkkkkkkkkkkkkkkkkkkkkkkkkkkkkkkkkkkkkkkkkkkkkkkkkkkkkkkkkkkkkkkkk")
        print(nextwaypoint)
        if nextwaypoint == 1:
            print("gggggggggggggggggggggggggggggggggggggggggggggggggggggggggggggggggggggggggggggggggg")
            i = count - 1
        else:
            i = nextwaypoint - 1
