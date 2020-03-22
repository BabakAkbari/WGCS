from django.http import JsonResponse
from django.shortcuts import render
from django.http import HttpResponse
from django.template import loader
from django.core.files.storage import FileSystemStorage
from dronekit import connect, VehicleMode, LocationGlobalRelative, LocationGlobal, Command
import time
import math
import dronekit
from Mission import mission
from pymavlink import mavutil
import json
vehicle = []
flag = 0
last = 0
start_time = 0
disconnected = 0
def index(request):
    '''
    if request.method == 'POST' and request.FILES['File']:
        file = request.FILES['File']
        fs = FileSystemStorage()
        filename = fs.save("MapSys/"+file.name,file)
        f = open(filename,"r")
        f1 = open("MapSys/static/js/realworld.388.js", "w")
        lat = []
        lon = []
        f1.write("var addressPoints = [\n")
        secondLastLine = None
        lastline = None
        secondLastLine, lastline = f.readline(),f.readline()
        for line in f:
        #    lat.append(line.split(",")[2])
            secondLastLine = lastline
            lastline = line
            f1.write("[\""+secondLastLine.split(",")[0]+"\","+secondLastLine.split(",")[1]+","+secondLastLine.split(",")[2]+"],")
        #    lon.append(line.split(",")[1])
        f1.write("[\""+secondLastLine.split(",")[0]+"\","+lastline.split(",")[1]+","+lastline.split(",")[2]+"]")
        f1.write("]")
        f1.close()
        f.close()
        return render(request, 'MapSys/index.html',{'lat': lat ,'lon': lon})
    f1 = open("MapSys/static/js/realworld.388.js", "w").close()
    '''
    return render(request, 'MapSys/index.html')

def uploadpoints(request):
        if request.method == 'POST' and request.FILES['File']:
            print("hereZ")
            file = request.FILES['File']
            fs = FileSystemStorage()
            filename = fs.save("MapSys/"+file.name,file)
            f = open(filename,"r")
            f1 = open("MapSys/static/js/fff.js", "w")
            lat = []
            lon = []
            f1.write("var addressPoints = [\n")
            secondLastLine = None
            lastline = None
            secondLastLine, lastline = f.readline(),f.readline()
            for line in f:
            #    lat.append(line.split(",")[2])
                secondLastLine = lastline
                lastline = line
                f1.write("[\""+secondLastLine.split(",")[0]+"\","+secondLastLine.split(",")[1]+","+secondLastLine.split(",")[2]+"],")
            #    lon.append(line.split(",")[1])
            f1.write("[\""+secondLastLine.split(",")[0]+"\","+lastline.split(",")[1]+","+lastline.split(",")[2]+"]")
            f1.write("]")
            f1.close()
            f.close()
            return JsonResponse({'status':'uploaded'})
        return JsonResponse({'status':'notuploaded'})
    # Connect to the Vehicle
    #vehicle = connect('udp:127.0.0.1:14551',wait_ready=True)
    #if(isinstance(vehicle, dronekit.Vehicle)):
    #    return JsonResponse({'status':'connected'})
    #else:
    #    return JsonResponse({'status':'notconnected'})
# Check that vehicle is armable.
    # This ensures home_location is set (needed when saving WP file)
def getloc(request):
    if request.method == 'GET':
        print(vehicle.location.global_frame)
        return JsonResponse([vehicle.location.global_frame.lat,vehicle.location.global_frame.lon,vehicle.location.global_frame.alt], safe=False)
    else:
        return HttpResponse("Request method is not a GET")

def connect(request):
    global vehicle
    global check
    global disconnected
    if isinstance(vehicle, dronekit.Vehicle) and disconnected == 0:
        return JsonResponse({'status':'connected'})
    else:
        check = 1
        vehicle = dronekit.connect('127.0.0.1:14551', wait_ready=True)
        return JsonResponse({'status':'notconnected'})

def getstatus(request):
    global vehicle
    global last
    global flag
    global start_time
    global disconnected
    if(isinstance(vehicle, dronekit.Vehicle)):
        last = vehicle.last_heartbeat
        time.sleep(2)
        if vehicle.last_heartbeat > 2 or last == vehicle.last_heartbeat:
            print("1")
            disconnected =1
            return JsonResponse({'status':'notconnected'})
        else:
            disconnected =0
            return JsonResponse({'status':'connected'})


def getyaw(request):
    global vehicle
    if(isinstance(vehicle, dronekit.Vehicle)):
        return JsonResponse({'YawAngle':vehicle.heading})

def startmission(request):
    if request.method == 'POST':
        #print ('Raw Data: "%s"' % request.body)
        json_data = json.loads(request.body)
        print(json_data)
        fs = FileSystemStorage()
        f = open("mpmissionfile.txt", "w")
        f.write("QGC WPL 110\n")
        global check
        if check:
            check = 0
            f.write("0\t0\t0\t16\t0\t0\t0\t0\t35.591713\t51.206090\t1089.402021\t1\n")
        k = 1
        land = []
        y = []
        for i in json_data:
            if i['station'] == True:
                land.append(i)
            else:
                f.write(str(k)+"\t0\t3\t16\t"+str(i['delay'])+"\t0\t0\t0\t"+str(i['lat'])+"\t"+str(i['lng'])+"\t"+str(i['alt'])+"\t1\n")
                y = i
                # if i['num'] == len(json_data):
                #     f.write(str(k)+"\t0\t3\t16\t"+str(i['delay'])+"\t0\t0\t0\t"+str(i['lat'])+"\t"+str(i['lng'])+"\t"+str(i['alt'])+"\t1\n")
                #     f.write(str(k + 1)+"\t0\t3\t16\t"+str(i['delay'])+"\t0\t0\t0\t"+str(i['lat'])+"\t"+str(i['lng'])+"\t"+str(i['alt'])+"\t1\n")
                # else:
                #     f.write(str(k)+"\t0\t3\t16\t"+str(i['delay'])+"\t0\t0\t0\t"+str(i['lat'])+"\t"+str(i['lng'])+"\t"+str(i['alt'])+"\t1\n")
                k = k + 1
            # if i['num'] == len(json_data)-1:
            #     f.write(str(i['num'])+"\t0\t3\t16\t"+str(i['delay'])+"\t0\t0\t0\t"+str(i['lat'])+"\t"+str(i['lng'])+"\t"+str(i['alt'])+"\t1\n")
            #     f.write(str(i['num']+1)+"\t0\t3\t16\t"+str(i['delay'])+"\t0\t0\t0\t"+str(i['lat'])+"\t"+str(i['lng'])+"\t"+str(i['alt'])+"\t1\n")
            # elif i['num'] == len(json_data):
            #     f.write(str(i['num']+1)+"\t0\t3\t16\t"+str(i['delay'])+"\t0\t0\t0\t"+str(i['lat'])+"\t"+str(i['lng'])+"\t"+str(i['alt'])+"\t1\n")
            #     f.write(str(i['num']+2)+"\t0\t3\t16\t"+str(i['delay'])+"\t0\t0\t0\t"+str(i['lat'])+"\t"+str(i['lng'])+"\t"+str(i['alt'])+"\t1\n")
            # #elif i['num'] == 1:
            # #    f.write(str(i['num'])+"\t0\t3\t16\t"+str(i['delay'])+"\t0\t0\t0\t"+str(i['lat'])+"\t"+str(i['lng'])+"\t"+str(i['alt'])+"\t1\n")
            # else:
            #     f.write(str(i['num'])+"\t0\t3\t16\t"+str(i['delay'])+"\t0\t0\t0\t"+str(i['lat'])+"\t"+str(i['lng'])+"\t"+str(i['alt'])+"\t1\n")
        f.write(str(k)+"\t0\t3\t16\t"+str(y['delay'])+"\t0\t0\t0\t"+str(y['lat'])+"\t"+str(y['lng'])+"\t"+str(y['alt'])+"\t1\n")
        f.close()
        count = json_data[0]['count']
        #count = k
        #users = json.loads(request)
        #for user in users:
        #    print (user['num'])
    global vehicle
    if(isinstance(vehicle, dronekit.Vehicle)):
        print("hi")
        mission.start_mission(vehicle,int(count),land,json_data[0]['yaw'])
        return JsonResponse({'missionstate':'completed'})
