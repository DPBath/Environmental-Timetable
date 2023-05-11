import openpyxl
from collections import defaultdict
import re

faculty_names = ['Eng', 'Hum', 'Man', 'Sci']
num_lectures_list = [3, 2, 2, 3]
number_modules = 5

# Read Room and Time colums 
import openpyxl

timeList = ['08:15', '09:15', '10:15', '11:15', '12:15', '13;15', '14:15', '15:15', '16:15', '17:15', '18:15', '19:15']

U2python = [61.47,63.12,62.38,61.47,61.47,62.38,62.38,62.09,61.28,62.75,62.75,62.38]
U21      = [73.41,73.98,75.09,74.25,74.25,74.81,74.81,73.69,73.41,75.93,75.93,74.81]
U22      = [48.76,100.75,78.98,63.87,63.87,73.94,73.94,53.80,48.76,94.09,94.09,73.94]
U23      = [72.14,75.36,75.29,73.71,73.71,74.76,74.76,72.66,72.14,76.86,76.86,74.76]
U24      = [67.21,78.24,73.23,70.22,70.22,72.22,72.22,68.21,67.21,76.24,76.24,72.22]

def read_excel_column_to_list(file_path, sheet_name, column, start_row):
    # Load the workbook and select the desired worksheet
    workbook = openpyxl.load_workbook(file_path)
    worksheet = workbook[sheet_name]

    # Find the end row by detecting the first empty cell in the column
    end_row = start_row
    while True:
        cell = worksheet[f"{column}{end_row}"]
        if cell.value is None:
            break
        end_row += 1

    # Read cells from the specified column and row range into a list
    output = [cell.value for cell in worksheet[column][start_row-1:end_row-1]]

    return output, workbook, worksheet

def read_lecture_assignments(file_path):
    lecture_assignments = {}
    with open(file_path, "r") as file:
        for line in file:
            lecture, assignment_str = line.strip().split(':', 1)
            assignment = eval(assignment_str.strip())  # Evaluate the string as a Python dictionary
            lecture_assignments[lecture] = assignment
    return lecture_assignments

# Read dictionary from text file
file_path = "/Users/DanPage/Library/Mobile Documents/com~apple~CloudDocs/Documents/Year5-Semester2/FYP/Code/test/lecture_assignments19.txt"
lecture_assignments = read_lecture_assignments(file_path)

roomAll, workbook, worksheet = read_excel_column_to_list('Tables.xlsx', 'Rooms', 'A', 2)
capacity, workbook, worksheet = read_excel_column_to_list('Tables.xlsx', 'Rooms', 'B', 2)

#excel = 'TimeTableBIG.xlsx'
excel = '/Users/DanPage/Library/Mobile Documents/com~apple~CloudDocs/Documents/Year5-Semester2/FYP/Code/test/TimeTable19.xlsx'

lastElement = 961

room, workbook, worksheet = read_excel_column_to_list(excel, 'Sheet1', 'D', 2)
time, workbook, worksheet = read_excel_column_to_list(excel, 'Sheet1', 'E', 2)
lec, workbook, worksheet = read_excel_column_to_list(excel, 'Sheet1', 'B', 2)


#excel = 'lecture_timesBIG.xlsx'
excel = '/Users/DanPage/Library/Mobile Documents/com~apple~CloudDocs/Documents/Year5-Semester2/FYP/Code/test/lecture_times19.xlsx'

lastElement = 27406

student_list, workbook, worksheet = read_excel_column_to_list(excel, 'Students', 'A', 2)
timeslots_list, workbook, worksheet = read_excel_column_to_list(excel, 'Students', 'E', 2)
lecture_list, workbook, worksheet = read_excel_column_to_list(excel, 'Students', 'C', 2)

#excel = 'lecture_timesBIG.xlsx'
excel = '/Users/DanPage/Library/Mobile Documents/com~apple~CloudDocs/Documents/Year5-Semester2/FYP/Code/test/lecture_times19.xlsx'

lastElement = 961

teacher_list, workbook, worksheet = read_excel_column_to_list(excel, 'Teachers', 'A', 2)
teachertimes_list, workbook, worksheet = read_excel_column_to_list(excel, 'Teachers', 'E', 2)
lec_teach_list, workbook, worksheet = read_excel_column_to_list(excel, 'Students', 'C', 2)

# Combine them

combined_list = [a + b for a, b in zip(room, time)]

# Check for duplicate timeslots
def has_duplicates(input_list):
    if len(set(input_list)) < len(input_list):
        print('There are duplicate timeslots.')
        return True
    else:
        print('There are no duplicate timeslots.')
        return False

has_duplicates(combined_list)  # Output: There are duplicate timeslots.


# Find number of modules for student

def count_student_modules(student_list, lecture_list, number_modules):
    student_modules = defaultdict(set)
    module_pattern = re.compile(r'M\d+')

    for student, lecture in zip(student_list, lecture_list):
        module = module_pattern.search(lecture).group()
        student_modules[student].add(module)

    incorrect_module_counts = {student: len(modules) for student, modules in student_modules.items() if len(modules) != number_modules}

    if not incorrect_module_counts:
        print("All students have the correct number of modules.")
    else:
        for student, module_count in incorrect_module_counts.items():
            print(f"Student {student} has {module_count} modules instead of {number_modules}.")

# Example usage
count_student_modules(student_list, lecture_list, number_modules)



# Check to see if teachers and students have multiple things scheduled at the same time
def check_timeslot_conflicts(student_list, timeslots_list, lecture_list):
    student_timeslots = defaultdict(lambda: defaultdict(set))

    for student, timeslot, lecture in zip(student_list, timeslots_list, lecture_list):
        if timeslot in student_timeslots[student]:
            if lecture not in student_timeslots[student][timeslot]:
                return f"Conflict: Student {student} has more than one lecture ({lecture} and {next(iter(student_timeslots[student][timeslot]))}) at timeslot {timeslot}"
        else:
            student_timeslots[student][timeslot].add(lecture)
    
    return "No conflicts found"

result = check_timeslot_conflicts(student_list, timeslots_list, lecture_list)
print(result)


# Check for teachers as well
result = check_timeslot_conflicts(teacher_list, teachertimes_list, lec_teach_list)
print(result)




# Lectures per year and time

def lecture_count_per_time_and_year_v4(lecture_assignments):
    time_year_count = defaultdict(lambda: defaultdict(int))

    for lecture, assignment in lecture_assignments.items():
        time = assignment['time'][-5:]
        year = "Y" + lecture.split("_")[2][-1]

        time_year_count[time][year] += 1

    # Find all unique years in the data
    unique_years = sorted(set(year for year_counts in time_year_count.values() for year in year_counts.keys()))

    # Sort the times in ascending order
    sorted_times = sorted(time_year_count.keys(), key=lambda x: (int(x.split(':')[0]), int(x.split(':')[1])))

    # Print the table
    header = "Time\t" + "\t".join(unique_years)
    print(header)

    for time in sorted_times:
        year_counts = time_year_count[time]
        row = f"{time}\t" + "\t".join(str(year_counts[year]) for year in unique_years)
        print(row)

lecture_count_per_time_and_year_v4(lecture_assignments)


# Find average days per faculty and for the whole university
def average_days_per_faculty_and_university_v3(student_list, timeslots_list):
    faculty_students = defaultdict(set)
    faculty_days = defaultdict(int)
    total_students = 0
    total_days = 0

    student_timeslots = defaultdict(set)
    for student, timeslot in zip(student_list, timeslots_list):
        student_timeslots[student].add(timeslot[:3])

    for student in student_timeslots.keys():
        faculty = student[:3]
        faculty_students[faculty].add(student)

    for faculty, students in faculty_students.items():
        faculty_total_days = sum(len(student_timeslots[student]) for student in students)
        faculty_days[faculty] = faculty_total_days / len(students)
        total_days += faculty_total_days
        total_students += len(students)

    university_average = total_days / total_students

    return faculty_days, university_average

# Example usage
faculty_averages, university_average = average_days_per_faculty_and_university_v3(student_list, timeslots_list)
print(f"Faculty averages: {faculty_averages}")
print(f"University average: {university_average}")


def check_room_capacity_sufficiency(lecture_list, lecture_assignments, roomAll, capacity):
    lecture_counts = defaultdict(int)

    # Count duplicates in lecture_list
    for lecture in lecture_list:
        lecture_counts[lecture] += 1

    # Check if room capacity is sufficient for each lecture
    for lecture, count in lecture_counts.items():
        assigned_room = lecture_assignments[lecture]['room']
        room_index = roomAll.index(assigned_room)
        room_capacity = capacity[room_index]

        if room_capacity < count:
            print(f"Insufficient capacity for lecture {lecture}: {count} students, room capacity {room_capacity}")
        # else:
        #     print(f"Sufficient capacity for lecture {lecture}: {count} students, room capacity {room_capacity}")

# Example usage
check_room_capacity_sufficiency(lecture_list, lecture_assignments, roomAll, capacity)

used_rooms_per_day = defaultdict(set)

for assignment in lecture_assignments.values():
    day = assignment['time'][:3]
    used_rooms_per_day[day].add(assignment['room'])

for day, rooms in used_rooms_per_day.items():
    print(f"Number of rooms used on {day}: {len(rooms)}")

print('hi')
specified_room = "CB1.10"

timeslots = [
    'MON08:15', 'MON09:15', 'MON10:15', 'MON11:15', 'MON12:15', 'MON13:15', 'MON14:15', 'MON15:15', 'MON16:15', 'MON17:15', 'MON18:15', 'MON19:15', 'MON20:15', 'MON21:15', 'MON22:15', 'MON23:15',
    'TUE00:15', 'TUE01:15', 'TUE02:15', 'TUE03:15', 'TUE04:15', 'TUE05:15', 'TUE06:15', 'TUE07:15', 'TUE08:15', 'TUE09:15', 'TUE10:15', 'TUE11:15', 'TUE12:15', 'TUE13:15', 'TUE14:15', 'TUE15:15', 'TUE16:15', 'TUE17:15', 'TUE18:15', 'TUE19:15', 'TUE20:15', 'TUE21:15', 'TUE22:15', 'TUE23:15',
    'WED00:15', 'WED01:15', 'WED02:15', 'WED03:15', 'WED04:15', 'WED05:15', 'WED06:15', 'WED07:15', 'WED08:15', 'WED09:15', 'WED10:15', 'WED11:15', 'WED12:15', 'WED13:15', 'WED14:15', 'WED15:15', 'WED16:15', 'WED17:15', 'WED18:15', 'WED19:15', 'WED20:15', 'WED21:15', 'WED22:15', 'WED23:15',
    'THU00:15', 'THU01:15', 'THU02:15', 'THU03:15', 'THU04:15', 'THU05:15', 'THU06:15', 'THU07:15', 'THU08:15', 'THU09:15', 'THU10:15', 'THU11:15', 'THU12:15', 'THU13:15', 'THU14:15', 'THU15:15', 'THU16:15', 'THU17:15', 'THU18:15', 'THU19:15', 'THU20:15', 'THU21:15', 'THU22:15', 'THU23:15',
    'FRI00:15', 'FRI01:15', 'FRI02:15', 'FRI03:15', 'FRI04:15', 'FRI05:15', 'FRI06:15', 'FRI07:15', 'FRI08:15', 'FRI09:15', 'FRI10:15', 'FRI11:15', 'FRI12:15', 'FRI13:15', 'FRI14:15', 'FRI15:15', 'FRI16:15', 'FRI17:15', 'FRI18:15'
]


def count_students_in_room_v5(specified_room, room_list, time_list, lec_list, lecture_list, timeslots):
    students_in_room = {}

    for time_slot in timeslots:
        students_in_room[time_slot] = 0

        for i, assigned_room in enumerate(room_list):
            if assigned_room == specified_room and time_list[i] == time_slot:
                lecture = lec_list[i]
                students_in_room[time_slot] += lecture_list.count(lecture)

    return students_in_room


students_in_room = count_students_in_room_v5(specified_room, room, time, lec, lecture_list, timeslots)

# for time, count in students_in_room.items():
#     print(f"{time}: {count} students")

# students_count_list = [count for time, count in students_in_room.items()]
# print(students_count_list)



# timeslots = [
#     'MON08:15', 'MON09:15', 'MON10:15', 'MON11:15', 'MON12:15', 'MON13:15', 'MON14:15', 'MON15:15', 'MON16:15', 'MON17:15', 'MON18:15',
#     'TUE08:15', 'TUE09:15', 'TUE10:15', 'TUE11:15', 'TUE12:15', 'TUE13:15', 'TUE14:15', 'TUE15:15', 'TUE16:15', 'TUE17:15', 'TUE18:15',
#     'WED08:15', 'WED09:15', 'WED10:15', 'WED11:15', 'WED12:15', 'WED13:15', 'WED14:15', 'WED15:15', 'WED16:15', 'WED17:15', 'WED18:15',
#     'THU08:15', 'THU09:15', 'THU10:15', 'THU11:15', 'THU12:15', 'THU13:15', 'THU14:15', 'THU15:15', 'THU16:15', 'THU17:15', 'THU18:15',
#     'FRI08:15', 'FRI09:15', 'FRI10:15', 'FRI11:15', 'FRI12:15', 'FRI13:15', 'FRI14:15', 'FRI15:15', 'FRI16:15', 'FRI17:15', 'FRI18:15'
# ]

def print_unique_students_count(student_list):
    unique_students = set(student_list)
    print("Number of unique students:", len(unique_students))


def calculate_total_emissions_for_methods(student_list, timeslots_list, emissions_lists):
    method_emissions = []

    for emissions in emissions_lists:
        total_emissions = 0

        student_timeslots = {}
        for student, time_slot in zip(student_list, timeslots_list):
            if student not in student_timeslots:
                student_timeslots[student] = []

            student_timeslots[student].append(time_slot)

        for timeslots in student_timeslots.values():
            student_lectures_by_day = {}

            for time_slot in timeslots:
                if len(time_slot) < 6:  # If the time format is incorrect, skip this time slot
                    continue

                day = time_slot[:3]
                time = time_slot[3:]

                if day not in student_lectures_by_day:
                    student_lectures_by_day[day] = []

                student_lectures_by_day[day].append(time)

            for day_lectures in student_lectures_by_day.values():
                earliest_time = min(day_lectures)
                latest_time = max(day_lectures)

                earliest_hour = int(earliest_time[:2])
                latest_hour = int(latest_time[:2])

                earliest_emission = emissions[earliest_hour - 8]
                latest_emission = emissions[latest_hour - 7]  # Add 1 to get the next time slot for going home

                total_emissions += earliest_emission + latest_emission

        method_emissions.append(total_emissions)

    return method_emissions

emissions_lists = [U2python, U21, U22, U23, U24]
print_unique_students_count(student_list)
method_emissions = calculate_total_emissions_for_methods(student_list, timeslots_list, emissions_lists)
for i, emissions in enumerate(method_emissions, start=1):
    print("Total emissions for method {}: {:.2f} kg".format(i, emissions))



# no_y1_student_list = [student for student in student_list if student.split("_")[2] != "Y1"]
# print(len(no_y1_student_list))
# no_y1_emissions = calculate_total_emissions_for_methods(no_y1_student_list, timeslots_list, emissions_lists)

# print("Total emissions for each method (no Y1 students):")
# for i, emissions in enumerate(no_y1_emissions, start=1):
#     print("Total emissions for method {}: {:.2f} kg".format(i, emissions))


# y1_hum_student_list = [student for student in student_list if student.split("_")[1] != "Y1" or (student.split("_")[1] == "Y1" and student.split("_")[0] == "Hum")]
# print(len(y1_hum_student_list))
# y1_hum_emissions = calculate_total_emissions_for_methods(y1_hum_student_list, timeslots_list, emissions_lists)

# print("Total emissions for each method (including Y1 Hum students):")
# for i, emissions in enumerate(y1_hum_emissions, start=1):
#     print("Total emissions for method {}: {:.2f} kg".format(i, emissions))

no_y1_student_list = [student for student in student_list if "Y1" not in student]
y1_hum_student_list = [student for student in student_list if "Y1" in student and "Hum" in student]

filtered_student_list = no_y1_student_list + y1_hum_student_list

print_unique_students_count(no_y1_student_list)
method_emissions_no_y1 = calculate_total_emissions_for_methods(no_y1_student_list, timeslots_list, emissions_lists)
method_emissions_y1_hum = calculate_total_emissions_for_methods(filtered_student_list, timeslots_list, emissions_lists)

for i, emissions in enumerate(method_emissions_no_y1, start=1):
    print("Total emissions for method {} (no Y1 students): {:.2f} kg".format(i, emissions))
print_unique_students_count(filtered_student_list)

for i, emissions in enumerate(method_emissions_y1_hum, start=1):
    print("Total emissions for method {} (including Y1 Hum students): {:.2f} kg".format(i, emissions))

import random

# Create a dictionary with the count of each student in student_list
student_counts = {}
for student in student_list:
    if student not in student_counts:
        student_counts[student] = 0
    student_counts[student] += 1

y1_student_list = [student for student in student_counts.keys() if "Y1" in student]
y1_excluded_randomly = set(random.sample(y1_student_list, 2900))

# Create a new list with the updated counts of each student
filtered_student_list_y1_included = []
filtered_timeslots_list_y1_included = []

for student, time_slot in zip(student_list, timeslots_list):
    if student not in y1_excluded_randomly:
        filtered_student_list_y1_included.append(student)
        filtered_timeslots_list_y1_included.append(time_slot)

# Calculate emissions for the scenario
method_emissions_y1_included = calculate_total_emissions_for_methods(filtered_student_list_y1_included, filtered_timeslots_list_y1_included, emissions_lists)
print_unique_students_count(filtered_student_list_y1_included)
for i, emissions in enumerate(method_emissions_y1_included, start=1):
    print("Total emissions for method {} (excluding 2900 random Y1 students): {:.2f} kg".format(i, emissions))


from collections import defaultdict

def count_students_by_faculty_and_year(student_list, faculty_names, num_years):
    faculty_year_counts = {faculty: {f"Y{i+1}": 0 for i in range(num_years)} for faculty in faculty_names}
    
    # Get unique students
    unique_students = set(student_list)
    
    for student in unique_students:
        parts = student.split("_")
        
        # Check if student name is in the expected format
        if len(parts) != 4:
            continue
        
        faculty = parts[0]
        year = parts[2]

        if faculty in faculty_year_counts:
            if year in faculty_year_counts[faculty]:
                faculty_year_counts[faculty][year] += 1

    return faculty_year_counts


def print_table(faculty_year_counts):
    header = "Faculty/Year\t" + "\t".join(f"Y{i+1}" for i in range(len(faculty_year_counts[next(iter(faculty_year_counts))])))
    print(header)

    for faculty, year_counts in faculty_year_counts.items():
        row = f"{faculty}\t\t" + "\t".join(str(year_counts[f"Y{i+1}"]) for i in range(len(year_counts)))
        print(row)

faculty_year_counts = count_students_by_faculty_and_year(student_list, faculty_names, 4)
print("\nNumber of students per faculty per year:")
print_table(faculty_year_counts)