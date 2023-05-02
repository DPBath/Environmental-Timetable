import math
import requests
import sys
import random
import os
from datetime import datetime

fuelList = []
co2List = []
timeList = []

api_key = "AIzaSyBzPvM7fVj7GzozpAf6zEiHPBSJLl1Z8Ys"
# Add extra stops to a journey using this
additionalStops = 0
timePerStop = 0.25

# Python program to get average of a list
def Average(lst):
    return sum(lst) / len(lst)

# Functions

# Sometimes speed limits cant be found, in this case replace this data with the nearest available speed
def get_nearest_speed_limit(speed_limits, index):
    left, right = index - 1, index + 1
    while left >= 0 or right < len(speed_limits):
        if left >= 0 and speed_limits[left] != "No speed limit data available":
            return speed_limits[left]
        if right < len(speed_limits) and speed_limits[right] != "No speed limit data available":
            return speed_limits[right]
        left -= 1
        right += 1
    return "No speed limit data available"

# Using openmaps find the speed limit for given coordinates
def get_speed_limits(coord_list):
    overpass_url = "https://overpass-api.de/api/interpreter"
    speed_limits = []
    
    for coord_str in coord_list:
        lat, lng = map(float, coord_str.split(','))
        query = f"""
    [out:json];
    way(around:25,{lat},{lng})["highway"];
    (._;>;);
    out body;
        """
        
        response = requests.get(overpass_url, params={"data": query})
        
        if response.status_code == 200:
            data = response.json()
            speed_limit_found = False
            for element in data['elements']:
                if element['type'] == 'way' and 'maxspeed' in element['tags']:
                    speed_limits.append(int(element['tags']['maxspeed'].split(' ')[0]))
                    speed_limit_found = True
                    break
                    
            if not speed_limit_found:
                speed_limits.append("No speed limit data available")
        else:
            speed_limits.append(f"Error {response.status_code}: {response.text}")

    for i, speed_limit in enumerate(speed_limits):
        if speed_limit == "No speed limit data available":
            speed_limits[i] = get_nearest_speed_limit(speed_limits, i)

    return speed_limits

# From Google Maps api get the elevation of each coordinate
def get_elevation_data(locations, api_key):
    url = f"https://maps.googleapis.com/maps/api/elevation/json?locations={locations}&key={api_key}"
    response = requests.get(url)
    data = response.json()

    if data["status"] == "OK":
        return data["results"]
    else:
        return None

# Calculate the difference in altitude between adjacent coordinates
def get_elevation_difference(origin, destination, api_key):
    locations = f"{origin}|{destination}"
    elevation_data = get_elevation_data(locations, api_key)

    if elevation_data and len(elevation_data) == 2:
        origin_elevation = elevation_data[0]["elevation"]
        destination_elevation = elevation_data[1]["elevation"]
        elevation_difference = destination_elevation - origin_elevation
        return elevation_difference
    else:
        return None

def calculate_elevation_differences(coords_list, api_key):
    elevation_differences = []

    for i in range(len(coords_list) - 1):
        origin = coords_list[i]
        destination = coords_list[i + 1]
        elevation_difference = get_elevation_difference(origin, destination, api_key)

        if elevation_difference is not None:
            elevation_differences.append(elevation_difference)
        else:
            elevation_differences.append(None)
            print(f"Error getting elevation difference for {origin} -> {destination}")

    return elevation_differences

# Find the distance between adjacent coordiantes
def get_walking_distance(origin, destination, api_key):
    url = f"https://maps.googleapis.com/maps/api/directions/json?origin={origin}&destination={destination}&mode=walking&key={api_key}"
    response = requests.get(url)
    data = response.json()

    if data["status"] == "OK":
        route = data["routes"][0]
        leg = route["legs"][0]
        distance = leg["distance"]["value"]
        return distance
    else:
        return None

def calculate_distances(coords_list, api_key):
    distances = []
    
    for i in range(len(coords_list) - 1):
        origin = coords_list[i]
        destination = coords_list[i + 1]
        distance = get_walking_distance(origin, destination, api_key)
        
        if distance is not None:
            distances.append(distance)
        else:
            distances.append(None)
            print(f"Error getting distance for {origin} -> {destination}")
    
    return distances

# Add additional stops or remove stops to a journey
def modify_points(num_points, *lists):
    modified_lists = [lst.copy() for lst in lists]

    if num_points > 0:
        # Add points
        for _ in range(num_points):
            index = random.randint(0, len(modified_lists[0]) - 1)
            split_ratio = random.random()

            for i, lst in enumerate(modified_lists):
                if i != 2:  # Only apply the ratio to distances and gradients lists (0 and 1)
                    first_part = lst[index] * split_ratio
                    second_part = lst[index] * (1 - split_ratio)
                    lst[index] = first_part
                    lst.insert(index + 1, second_part)
                else:  # Keep the same speed value for the added element
                    lst.insert(index + 1, lst[index])

    elif num_points < 0:
        # Remove points
        for _ in range(abs(num_points)):
            if len(modified_lists[0]) > 1:
                index = random.randint(0, len(modified_lists[0]) - 2)

                for i, lst in enumerate(modified_lists):
                    if i != 2:  # Only apply the ratio to distances and gradients lists (0 and 1)
                        combined_value = lst[index] + lst[index + 1]
                        lst[index] = combined_value
                        del lst[index + 1]
                    else:  # Keep the same speed value for the combined element
                        del lst[index + 1]

    return modified_lists

# To save run time save variables to a text file, check if it needs generating
def fileMaker(fileName,routeText,feature):
    if os.path.exists(fileName):
        routeTime = os.path.getmtime(routeText)
        fileTime = os.path.getmtime(fileName)

        # If it exists and was generated after the route file read it
        if fileTime > routeTime:
            my_file = open(fileName, "r")
            data = my_file.read()
            output = data.split("\n")
            output = output[ : -1]
            output = [eval(i) for i in output]
            my_file.close()

    else:
            # Get speed limit in mph
        if feature == 'speed':    
            output = get_speed_limits(coords_list)

            # Write this to file
            with open(fileName, 'w') as file:
                for item in output:
                    # Write each item on a new line
                    file.write(f'{item}\n')

                    # Get speed limit in mph
        elif feature == 'distance':    
            output = calculate_distances(coords_list, api_key)

            # Write this to file
            with open(fileName, 'w') as file:
                for item in output:
                    # Write each item on a new line
                    file.write(f'{item}\n')
        elif feature == 'altitude':    
            output = calculate_elevation_differences(coords_list, api_key)

            # Write this to file
            with open(fileName, 'w') as file:
                for item in output:
                    # Write each item on a new line
                    file.write(f'{item}\n')
    
    return output

def journey_times_and_avg_speeds(distances, max_speeds, acceleration):
    avg_speeds = []
    times = []

    for i in range(len(distances)):
        distance = distances[i]
        max_speed = max_speeds[i]

        # Calculate time to reach max_speed
        time_to_max_speed = max_speed / acceleration

        # Calculate distance during acceleration
        distance_during_accel = 0.5 * acceleration * time_to_max_speed ** 2

        # If distance is covered during acceleration phase
        if distance <= distance_during_accel:
            avg_speed = (2 * distance / time_to_max_speed) / 2
            time = 2 * time_to_max_speed / 2
        else:
            remaining_distance = distance - distance_during_accel

            # Calculate time at max_speed
            time_at_max_speed = remaining_distance / max_speed

            # Calculate total time
            total_time = time_to_max_speed + time_at_max_speed

            # Calculate average speed
            avg_speed = distance / total_time
            time = total_time

        avg_speeds.append(avg_speed)
        times.append(time)

    return times, avg_speeds


########################################################
### CODE

coords_list = []

# Choose which route you would like to look at
# route = input('Which bus route would you like? (U1, U2, U2car, 20, 22, real): ')

# if route == 'U1' or  route == 'U2' or  route == 'U2car' or  route == '20' or  route == '22' or route == 'real':
#     print('Valid Route')
# else:
#     sys.exit('Not a valid route')

route = ['U1','U2','U2car','20','22','real','home','test']
routeBusStops = [30 + additionalStops,33 + additionalStops,0 + additionalStops,35 + additionalStops,65 + additionalStops,0 + additionalStops,0 + additionalStops,0 + additionalStops]

for routeNumber in range(len(route)):
    # File Names
    routeText = route[routeNumber] + '.txt'
    routeSpeed = route[routeNumber] + 'Speed.txt'
    routeDistance = route[routeNumber] + 'Distance.txt'
    routeAltitude = route[routeNumber] + 'Altitude.txt'

    # Read route coordinate file
    my_file = open(routeText, "r")
    data = my_file.read()
    coords_list = data.split("\n")
    my_file.close()

    speed_limits = []
    speed_limits = fileMaker(routeSpeed,routeText,'speed')

    # Convert to m/s
    speed_ms = [x / 2.237 for x in speed_limits]

    distances = []
    distances = fileMaker(routeDistance,routeText,'distance')

    elevation_differences = []
    elevation_differences = fileMaker(routeAltitude,routeText,'altitude')

    # VARIABLES

    if routeBusStops[routeNumber] < 0:
        routeBusStops[routeNumber] = 0

    # Gravity (m/s^2)
    g = 9.81
    # Air Density (kg/m^3)
    p = 1.225

    massPerson = 79.42
    busPopulation = 26.3

    velocity = speed_ms
    distance = distances

    gradient = []

    # Calculate gradient in radians
    for i in range(len(distances)):
        gradient.append(math.asin(elevation_differences[i] / distances[i]))

    distance, gradient, velocity = modify_points(additionalStops, distance, gradient, velocity)

    for count in range(2):

        if count == 0:
            # Bus Variables
            #print('bus')
            massVehicle = 18000
            m = massVehicle + (busPopulation * massPerson)
            # Coefficient of Drag
            cd = 0.706339
            # Size of Vehicle
            height = 4.3
            width = 2.55
            A = height * width
            # Coefficient of Rolling Resistance
            crr = 0.1
            # Density of Diesel
            fuelDensity = 35800000
            engineEff = 0.35
            # Acceleration of a bus (m/s^2)
            acceleration = 0.75
            engineSize = 6
            # CO2 released from burning diesel
            fuelMass = 2.68


        if count == 1:
            # Car Variables
            #print('car')
            massVehicle = 1375
            m = massVehicle + massPerson
            # https://www.firstpost.com/tech/auto-tech/mercedes-benz-a-class-sedan-has-lowest-drag-coefficient-of-any-production-car-4822801.html
            cd = 0.22
            # Size of Vehicle
            A = 2.19

            # Coefficient of Rolling Resistance
            # https://www.engineeringtoolbox.com/rolling-friction-resistance-d_1303.html
            crr = 0.02
            # Density of Petrol
            fuelDensity = 34200000
            engineEff = 0.25
            # Acceleration of a car (m/s^2)
            acceleration = 0.9
            engineSize = 1.3
            # CO2 released from burning petrol
            fuelMass = 2.31        

        # Calculations

        fuel_cum = []
        time_cum = []
        

        # Loop through each stop and calculate petrol to drive distance
        for i in range(len(velocity)-1):
            # Check velocity that will be reached in the given distance
            maxVelocity = (2*acceleration*distance[i])**0.5

            # if less than speed ms use that else use 
            if maxVelocity <= velocity[i]:
                velocity[i] = maxVelocity

            # Kinetic Energy
            KE = 0.5 * m * velocity[i]**2

            # Potential Energy
            PE = m * g * distance[i] * math.sin(gradient[i])
            
            # Air Resistance
            Ar = 0.5 * cd * A * p * (velocity[i]**2) * distance[i]
            
            # Rolling Resistance
            Rr = crr * m * g * distance[i] * math.cos(gradient[i])

            # Total Energy to go uphill
            total_energy = (KE + PE + Ar + Rr) / engineEff
            
            # Volume of fuel to go uphill
            fuel = total_energy / fuelDensity

            if fuel <= 0:
                fuel = 0

            # Starting Eninge
            start = engineSize/1000
            fuel = fuel + start

            fuel_cum.append(fuel)


            #time_seg = (2*distance[i])/(0+velocity[i])

            #time_seg = (velocity[i])/acceleration

            #time_seg = (velocity[i]-(velocity[i]**2 - 2*acceleration*distance[i])**0.5)/acceleration
            #print(time_seg)
            #time_seg = abs(time_seg)
            #time_cum.append(time_seg)
        
        time_cum, average_speed = journey_times_and_avg_speeds(distance,velocity,acceleration)

        #print('average speed: ',Average(average_speed))

        # Find the total amount of petrol for the journey.
        fuel_litres = sum(fuel_cum)
       # print('Litres of Fuel:')
        co2 = fuelMass * fuel_litres

       # print('kg of CO2: ')
       # print(co2)
        #print(time_cum)
        #print(distance)
        #print(speed_ms)

        time = sum(time_cum)
        time = time/60
        #print('Time to complete journey: ')

        #print((routeBusStops[routeNumber] * timePerStop))

        time = time + (routeBusStops[routeNumber] * timePerStop)

        time = round(time,2)
        #print(time)
        
        fuelList.append(fuel_litres)
        co2List.append(co2)
        timeList.append(time)




######## PRINT OUTPUT

fuelBus = fuelList[::2]
fuelCar = fuelList[1::2]

co2Bus = co2List[::2]
co2Car = co2List[1::2]

timeBus = timeList[::2]
timeCar = timeList[1::2]

# Print the header row
header = f"{'':<10}|{'Bus':^32}|{'Car':^32}"
print(header)
header = f"{'Row Name':<10}|{'Litres':^10}|{'Kg':^10}|{'Time':^10}|{'Litres':^10}|{'Kg':^10}|{'Time':^10}"
print(header)
print('-' * len(header))

# Print the data rows
for i in range(len(fuelBus)):
    row_str = f"{route[i]:<10}|{fuelBus[i]:^10.2f}|{co2Bus[i]:^10.2f}|{timeBus[i]:^10}|{fuelCar[i]:^10.2f}|{co2Car[i]:^10.2f}|{timeCar[i]:^10}"
    print(row_str)


#for i in range(len(timeBus)):
#    print(timeBus[i])
    