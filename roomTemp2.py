import matplotlib.pyplot as plt
import openpyxl

# How much better than Building Regulations (Uni says 4x)
improvementFactor = 1
improvementFactorVent = 1

insideTemp = 18
outsideTemp = 2

# Time spent in the room (hour)
time = 1
# Heat power output of 1 person (W)
heatPower = 88

def average(lst):
    return sum(lst) / len(lst)

def read_excel_column_to_list(file_path, sheet_name, column, start_row, end_row):
    # Load the workbook and select the desired worksheet
    workbook = openpyxl.load_workbook(file_path)
    worksheet = workbook[sheet_name]

    # Read cells from the specified column and row range into a list
    output = [cell.value for cell in worksheet[column][start_row-1:end_row]]

    return output

# Read in from Table
file_path = 'Tables.xlsx'
sheet_name = 'Chancellors'
start_row = 2
end_row = 31

roomName = read_excel_column_to_list(file_path, sheet_name, 'V', start_row, end_row)
roomCapacity = read_excel_column_to_list(file_path, sheet_name, 'W', start_row, end_row)
floorArea = read_excel_column_to_list(file_path, sheet_name, 'X', start_row, end_row)
roomHeight = read_excel_column_to_list(file_path, sheet_name, 'Y', start_row, end_row)
extWallArea = read_excel_column_to_list(file_path, sheet_name, 'Z', start_row, end_row)
extDoorArea = read_excel_column_to_list(file_path, sheet_name, 'AA', start_row, end_row)
extWindowArea = read_excel_column_to_list(file_path, sheet_name, 'AB', start_row, end_row)
extFloorArea = read_excel_column_to_list(file_path, sheet_name, 'AC', start_row, end_row)
extRoofArea = read_excel_column_to_list(file_path, sheet_name, 'AD', start_row, end_row)


# # Capacity of the room
# roomCapacity = 80
# # Room Size
# roomHeight = 4.375 
# floorArea = 126.37 #m2s

# # Number of doors and door size (m)
# doorWidth = 1
# doorHeight = 1.98
# doorNum = 4
# doorArea = doorWidth * doorHeight

# # Size of windows in building
# windowWidth = 8
# windowHeight = roomHeight
# windowArea = windowWidth * windowHeight

# # If you dont know exact dimensions assume its a square
# roomLength = roomWidth = floorArea ** 0.5
# #roomLength = 9
# #roomWidth = floorArea/roomLength


airDensity = 1.275 #kg/m3
specificHeatCap = 1.006 #kJ/kgk

Uwall = 0.26 / improvementFactor
Uroof = 0.16 / improvementFactor
Ufloor = 0.18 / improvementFactor
Uwindow = 1.6 / improvementFactor
Udoor = 1.6 / improvementFactor

volumeFlowRate = 0.01 * improvementFactorVent

tempIncLog = []
deltaTLog = []

howMany = []



for i in range(len(roomCapacity)):
    #outsideTemp = i
    #outsideTemp = 0

    # Number of people in the room
    numPeople = 0

    volume = floorArea[i] * roomHeight[i]


    deltaT = insideTemp - outsideTemp
    deltaTLog.append(outsideTemp)

    airMass = volume * airDensity

    #tempChange = (heatPower * numPeople * time) / (airMass * specificHeatCap * 3.6)

    # Heat loss from each part of a room
    roofLoss = extRoofArea[i] * Uroof * deltaT
    floorLoss = extFloorArea[i] * Ufloor * deltaT
    windowLoss = extWindowArea[i] * Uwindow * deltaT
    doorLoss = extDoorArea[i] * Udoor * deltaT
    wallLoss = extWallArea[i] * Uwall * deltaT

    heatLossRate = roofLoss + floorLoss + wallLoss + windowLoss + doorLoss

    
    ventilation = volumeFlowRate * roomCapacity[i] * airDensity * specificHeatCap * deltaT
    
    heatGain = (heatPower * numPeople) - heatLossRate - ventilation
    tempInc = (heatGain * time)/(airMass * specificHeatCap * 3.6)
    
    while tempInc <= 0:
        numPeople += 1
        ventilation = volumeFlowRate * numPeople * airDensity * specificHeatCap * deltaT

        heatGain = (heatPower * numPeople) - heatLossRate - ventilation
        tempInc = (heatGain * time)/(airMass * specificHeatCap * 3.6)

    howMany.append(numPeople)
    tempIncLog.append(tempInc)

    #print(outsideTemp)
    #print(ventilation)

    #print(deltaTLog)
    #print(tempIncLog)

    #plt.plot(deltaTLog,tempIncLog)
    #plt.show()

print('Temp Incerase:', tempIncLog)
print('')
print('People required:',howMany)
print('')

res = [i / j for i, j in zip(howMany, roomCapacity)]

print('Fill ratio percentage to get min temp:',res)
print('')

#plt.scatter(roomCapacity,howMany)
#plt.show()

print('Average number of people required: ',average(howMany))
print('')

for i in range(len(howMany)):
    print(howMany[i])