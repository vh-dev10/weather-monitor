from django.shortcuts import render
import requests
import math
import datetime
import os
# Create your views here.
# convert unix timestamp to human readable day name
def get_dayname(unix_timestamp):
    dt = datetime.datetime.fromtimestamp(unix_timestamp)
    return dt.strftime("%A")
# convert unix timestamp to human readable time
def get_time(unix_timestamp):
    rt = datetime.datetime.fromtimestamp(unix_timestamp).strftime('%I:%M %p')
    return rt
# convert unix timestamp to human readable time and day name
def get_date(unix_timestamp):
    rt = datetime.datetime.fromtimestamp(unix_timestamp).strftime('%A, %d %b')
    return rt
# function to sanitize usable data from json response to display in template.
def getCurrentData(jsonResponse):
        current_data={}
        current_data['city']=jsonResponse['name']
        current_data['timezone']=jsonResponse['timezone']
        current_data['country']=','+jsonResponse['sys']['country']
        current_data['weather_des']=jsonResponse['weather'][0]['description']
        current_data['icon']=jsonResponse['weather'][0]['icon']
        current_data['temp']=math.ceil(jsonResponse['main']['temp'])
        current_data['min_temp']=math.floor(jsonResponse['main']['temp_min'])
        current_data['max_temp']=math.ceil(jsonResponse['main']['temp_max'])
        current_data['feels_like']=math.ceil(jsonResponse['main']['feels_like'])
        current_data['sunrise']=get_time(jsonResponse['sys']['sunrise'])
        current_data['sunset']=get_time(jsonResponse['sys']['sunset'])
        current_data['wind_speed']=math.ceil((jsonResponse['wind']['speed']*3600)/1000)
        current_data['humidity']=jsonResponse['main']['humidity']
        current_data['visibiity']=math.ceil(jsonResponse['visibility']/1000)
        return current_data
# function to sanitize usable data from json response to display in template.
def getForecastData(jsonResponse):
    forecastdata=[]
    foretempdata={}
    for i in jsonResponse["list"]:
        if jsonResponse["list"].index(i)==0:
            continue
        a,b,c,d=i['temp']['day'],i['temp']['night'],i['temp']['eve'],i['temp']['morn']
        temp_avg=math.ceil((a+b+c+d)/4)
        w,x,y,z=i['feels_like']['day'],i['temp']['night'],i['temp']['eve'],i['temp']['morn']
        flike=math.ceil((w+x+y+z)/4)
        foretempdata["date"]=get_date(i["dt"])
        foretempdata["temp"]=temp_avg
        foretempdata["feels_like"]=flike
        foretempdata["min_temp"]=i['temp']['min']
        foretempdata["max_temp"]=i['temp']['max']
        foretempdata["sunrise"]=get_time(i['sunrise'])
        foretempdata["sunset"]=get_time(i['sunset'])
        foretempdata["humidity"]=i['humidity']
        foretempdata["wind_speed"]=math.ceil((i['speed']*3600)/1000)
        foretempdata["des"]=i['weather'][0]['description']
        foretempdata["icon"]=i['weather'][0]['icon']
        forecastdata.append(foretempdata)
        foretempdata={}
    return forecastdata
        
def weather_monitor_main(request):
    if request.method=="POST":
        location_flag=False
        try:
            if request.POST['flag']=="curr_location":
                location_flag=True
        except:
            pass
        curr_date=datetime.datetime.now()
        x=curr_date.strftime("%A, %d %b")
        api_key=os.environ.get('MY_API_KEY', 'default_value')#api secret key
        city=None # reciving user iput data
        data=[] # variable to store current weather data and forecast data
        # get current weather data
        response=None
        curr_data=None
        url=None
        if location_flag:
            lat=request.POST["latitude"]
            lon=request.POST["longitude"]
            url = f"https://api.openweathermap.org/data/2.5/weather?lat={lat}&lon={lon}&appid={api_key}&units=metric" #api call
            response = requests.get(url) # capture response from api
            curr_data = response.json() # get json into form of python dict
        else:
            city=request.POST['city']
            url = f"https://api.openweathermap.org/data/2.5/weather?q={city}&appid={api_key}&units=metric" #api call
            response = requests.get(url) # capture response from api
            curr_data = response.json() # get json into form of python dict
        # error handeling for searched city name not found
        if curr_data['cod']=="404":
            return render(request,'index.html',{"flg":False,"error":"city not found","err":True,"date":x})
        # end
        # data storing
        current_data=getCurrentData(curr_data)# get current data from funciton
        data.append(current_data) # store data in to list for sending to html template.
        data.append(x)
        # end
        
        # get forecast data
        city_forecast=current_data['city']
        url = f"https://api.openweathermap.org/data/2.5/forecast/daily?APPID={api_key}&q={city_forecast}&units=metric&cnt=8" #api call
        response = requests.get(url) # capture response from api
        fore_data = response.json() # get json into form of python dict
        #data storing
        forecast_data=getForecastData(fore_data)# get current data from funciton
        data.append(forecast_data) # store data in to list for sending to html template.
        #end
        #render template after sucessful response'''
        return render(request,'index.html',{"flg":True,"wdata":data})
    else:
        # inital page rendering
        return render(request,'index.html',{"flg":False})
