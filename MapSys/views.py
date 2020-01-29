from django.shortcuts import render
from django.http import HttpResponse
from django.template import loader
from django.core.files.storage import FileSystemStorage

# Create your views here.

def index(request):
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
    return render(request, 'MapSys/index.html')
