import pandas as pd
from collections import defaultdict

from assignments import *
from counting import *
from generation import *
from get_info import *
from input_data import *
from output_data import *
from population import *
from validity import *

# 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
print('hi')

faculty_names = ['Eng', 'Hum', 'Man', 'Sci']

room, workbook, worksheet = read_excel_column_to_list('Tables.xlsx', 'Rooms', 'A', 2, 164)
capacity, workbook, worksheet = read_excel_column_to_list('Tables.xlsx', 'Rooms', 'B', 2, 164)

##### Normal
room, workbook, worksheet = read_excel_column_to_list('Tables.xlsx', 'Rooms', 'A', 2, 164)
capacity, workbook, worksheet = read_excel_column_to_list('Tables.xlsx', 'Rooms', 'B', 2, 164)

students_per_faculty_year = [[893,1517,714,1339],[766,1302,613,1149],[520,884,416,780],[937,1358,639,1414]]
num_courses_list = [[7, 11, 4, 10],[7, 11, 4, 10],[7, 11, 4, 10],[6,13,5,6]]
num_assigned_modules = 5
num_total_modules = 9
#num_lectures_list = [3, 2, 2, 3]
num_lectures_list = [4, 3, 4, 4]
year_percentages = [40, 34, 23, 3]
num_teachers_per_faculty =[85,143,68,127]

##### Fast
# room, workbook, worksheet = read_excel_column_to_list(f'Tables.xlsx', 'Rooms', 'H', 2, 30)
# capacity, workbook, worksheet = read_excel_column_to_list('Tables.xlsx', 'Rooms', 'I', 2, 30)

# students_per_faculty_year = [[178,303,143,268],[153,260,123,230],[104,176,83,156],[187,271,127,283]]
# num_courses_list = [[4, 4, 4, 4],[4, 4, 4, 4],[4, 4, 4, 4],[4, 4, 4, 4]]
# num_lectures_list = [3, 3, 3, 3]
# year_percentages = [40, 34, 23, 3]
# num_assigned_modules = 3
# num_total_modules = 5
# num_teachers_per_faculty =[20,30,14,25]

##### Instant
# room, workbook, worksheet = read_excel_column_to_list(f'Tables.xlsx', 'Rooms', 'H', 2, 30)
# capacity, workbook, worksheet = read_excel_column_to_list('Tables.xlsx', 'Rooms', 'I', 2, 30)

# students_per_faculty_year = [[178,303,143,268],[153,260,123,230],[104,176,83,156],[187,271,127,283]]
# num_courses_list = [[1, 1, 1, 1],[1, 1, 1, 1],[1, 1, 1, 1],[1, 1, 1, 1]]
# num_lectures_list = [1, 1, 1, 1]
# year_percentages = [40, 34, 23, 3]
# num_assigned_modules = 1
# num_total_modules = 1
# num_teachers_per_faculty =[20,30,14,25]


# Comment - Similar to above, like that its a dictionary, but collate this operation with the above one so you only have to loop through student in population once.


# Look at doing lecturer profile with prefered hours etc, regular blockers

# ######################### TIME SHIT

# All possible working hours
all_hours = ['MON08:15', 'MON09:15', 'MON10:15', 'MON11:15', 'MON12:15', 'MON13:15', 'MON14:15', 'MON15:15', 'MON16:15', 'MON17:15', 'MON18:15', 'TUE08:15', 'TUE09:15', 'TUE10:15', 'TUE11:15', 'TUE12:15', 'TUE13:15', 'TUE14:15', 'TUE15:15', 'TUE16:15', 'TUE17:15', 'TUE18:15', 'WED08:15', 'WED09:15', 'WED10:15', 'WED11:15', 'WED12:15', 'WED13:15', 'THU08:15', 'THU09:15', 'THU10:15', 'THU11:15', 'THU12:15', 'THU13:15', 'THU14:15', 'THU15:15', 'THU16:15', 'THU17:15', 'THU18:15', 'FRI08:15', 'FRI09:15', 'FRI10:15', 'FRI11:15', 'FRI12:15', 'FRI13:15', 'FRI14:15', 'FRI15:15', 'FRI16:15', 'FRI17:15', 'FRI18:15']
#all_hours = ['MON08:15','MON09:15']
# Times that arent ideal - 8.15 and 18:15
nonideal_hours = ['MON08:15', 'MON18:15', 'TUE08:15', 'TUE18:15', 'WED08:15', 'THU08:15', 'THU18:15', 'FRI08:15', 'FRI18:15']
# High Carbon Times
highcarbon_hours = ['MON09:15', 'MON16:15', 'MON17:15', 'TUE09:15', 'TUE16:15', 'TUE17:15', 'WED09:15', 'THU09:15', 'THU16:15', 'THU17:15', 'FRI09:15', 'FRI16:15', 'FRI17:15']
# Low Carbon Times
lowcarbon_hours = ['MON10:15', 'MON11:15', 'MON12:15', 'MON13:15', 'MON14:15', 'MON15:15', 'TUE10:15', 'TUE11:15', 'TUE12:15', 'TUE13:15', 'TUE14:15', 'TUE15:15', 'WED10:15', 'WED11:15', 'WED12:15', 'WED13:15', 'THU10:15', 'THU11:15', 'THU12:15', 'THU13:15', 'THU14:15', 'THU15:15', 'FRI10:15', 'FRI11:15', 'FRI12:15', 'FRI13:15', 'FRI14:15', 'FRI15:15']
# Typical 9-15
typical_hours = ['MON9:15', 'MON10:15', 'MON11:15', 'MON12:15', 'MON13:15', 'MON14:15', 'MON15:15', 'MON16:15', 'TUE9:15', 'TUE10:15', 'TUE11:15', 'TUE12:15', 'TUE13:15', 'TUE14:15', 'TUE15:15', 'TUE16:15', 'WED9:15', 'WED10:15', 'WED11:15', 'WED12:15', 'WED13:15', 'THU9:15', 'THU10:15', 'THU11:15', 'THU12:15', 'THU13:15', 'THU14:15', 'THU15:15', 'THU16:15', 'FRI9:15', 'FRI10:15', 'FRI11:15', 'FRI12:15', 'FRI13:15', 'FRI14:15', 'FRI15:15', 'FRI16:15']
# Postgraduate Times
postgrad_hours = ['WED14:15', 'WED15:15', 'WED16:15', 'WED17:15', 'WED16:15']






def visualize_assignments(lecture_assignments):
    data = []

    for lecture, assignment in lecture_assignments.items():
        module, lecture_num = lecture.rsplit('_', 1)
        room = assignment['room']
        time = assignment['time']
        data.append([module, lecture, lecture_num, room, time])

    df = pd.DataFrame(data, columns=['Module', 'Lecture', 'Lecture_Num', 'Room', 'Time'])
    df.sort_values(by=['Module', 'Lecture_Num'], inplace=True)
    return df



####### OUTPUT
population = generate_population(students_per_faculty_year, faculty_names, num_courses_list, year_percentages, num_assigned_modules, num_total_modules, num_lectures_list)

# Finding students in the same module
target_module = 'Man_C1_Y4_M3'
students_in_module = find_students_in_same_module(population, target_module)

print(f"\nStudents in module {target_module}:")
for student_name in students_in_module:
    print(student_name)

print(len(population))

check_assigned_modules(population, num_assigned_modules)

# Count students per faculty and print the results
faculty_counts = count_students_by_faculty(population, faculty_names)

print("Number of students per faculty:")
for faculty, count in faculty_counts.items():
    print(f"{faculty}: {count}")


# Count students per faculty and year and print the table
faculty_year_counts = count_students_by_faculty_and_year(population, faculty_names, len(year_percentages))
print("\nNumber of students per faculty per year:")
print_table(faculty_year_counts)

# Example usage:
#display_students_in_lecture(population, "Man_C1_Y4_M3_L1")
#display_students_in_lecture(population, "Man_C1_Y4_M3_L2")

print_unique_modules_and_lectures(population)

all_modules = get_all_modules(population)
print(len(all_modules))

teachers = assign_modules_to_teachers(population, num_teachers_per_faculty, faculty_names, num_lectures_list)

# Assuming the previously generated population and teachers
module_assignment_check = check_module_assignment(population, teachers)

#print(teachers)

print(module_assignment_check)
#print(len(teachers))

#print(len(get_all_lectures(population)))

student_occupied_time_slots = {student['name']: set() for student in population}
teacher_occupied_time_slots = {teacher['teacher_id']: set() for teacher in teachers}

room_capacity_dict = dict(zip(room, capacity))






#lecture_assignments = assign_rooms_and_times_v10(population, teachers, room, room_capacity_dict, all_hours)
#lecture_assignments = assign_rooms_and_times_v11(population, teachers, room, room_capacity_dict, all_hours)
#lecture_assignments = assign_rooms_and_times_v12(population, teachers, room, room_capacity_dict, lowcarbon_hours, highcarbon_hours, nonideal_hours)
#lecture_assignments = assign_rooms_and_times_v13(population, teachers, room, room_capacity_dict, lowcarbon_hours, highcarbon_hours, nonideal_hours)
#lecture_assignments = assign_rooms_and_times_v16(population, teachers, room, room_capacity_dict, lowcarbon_hours, highcarbon_hours, nonideal_hours)
#lecture_assignments = assign_rooms_and_times_v17(population, teachers, room, room_capacity_dict, lowcarbon_hours, highcarbon_hours, nonideal_hours)
#lecture_assignments = assign_rooms_and_times_v18(population, teachers, room, room_capacity_dict, lowcarbon_hours, highcarbon_hours, nonideal_hours, postgrad_hours)
lecture_assignments = assign_rooms_and_times_v19(population, teachers, room, room_capacity_dict, lowcarbon_hours, highcarbon_hours, nonideal_hours, postgrad_hours)



with open("lecture_assignments.txt", "w") as file:
    for lecture, assignment in lecture_assignments.items():
        file.write(f"{lecture}: {assignment}\n")



#print(lecture_assignments)

df = visualize_assignments(lecture_assignments)
print(df)

df.to_excel('TimeTable.xlsx', index=False)

unassigned_lectures = count_unassigned_lectures(lecture_assignments)
print(f"Number of unassigned lectures: {unassigned_lectures}")

# all_lectures = get_all_lectures_from_population(population)
# print("All lectures from population:")
# print(all_lectures)

# assigned_lectures = set(lecture_assignments.keys())
# print("Assigned lectures:")
# print(assigned_lectures)

# missing_lectures = all_lectures - assigned_lectures
# print("Missing lectures:")
# print(missing_lectures)

students_per_lecture = count_students_per_lecture(population, lecture_assignments)

#print("Number of students per lecture:")
#for lecture, count in students_per_lecture.items():
#    print(f"{lecture}: {count}")

room_capacity_dict = {room: capacity for room, capacity in zip(room, capacity)}

# print(room_capacity_dict)

lecture_room_sizes = get_room_sizes(lecture_assignments, room_capacity_dict)
# print("Room sizes for lectures:")
# for lecture, room_size in lecture_room_sizes.items():
#     if room_size is None:
#         print(f"{lecture}: Room not found")
#     else:
#         print(f"{lecture}: {room_size}")

# Call the function with the lecture_student_counts and lecture_room_sizes dictionaries
check_room_capacity(students_per_lecture, lecture_room_sizes)

# Call the function with the population, teachers, and lecture_assignments dictionaries
student_timeslots, teacher_timeslots, allocation_check = check_allocations(population, teachers, lecture_assignments)

# unassigned_room_timeslots = get_unassigned_room_timeslots(lecture_assignments, room, all_hours)
# print("Unassigned room timeslots:")
# for room, times in unassigned_room_timeslots.items():
#     print(f"{room}: {times}")


# Example usage
# student_name = "Man_C3_Y4_MP"  # Replace with the student name you want to check
# days_at_university = count_days_at_university(student_timeslots, student_name)
# print(f"{student_name} spends {days_at_university} days at university.")

# Example usage
faculty_year_averages = average_days_per_faculty_and_university(population, student_timeslots)



# Create a DataFrame for student lecture times
student_data = []

for student in population:
    student_name = student['name']
    for module, lectures in student['lectures'].items():
        for lecture in lectures:
            time = lecture_assignments[lecture]['time']
            room = lecture_assignments[lecture]['room']
            student_data.append([student_name, module, lecture, room, time])

student_df = pd.DataFrame(student_data, columns=['Student', 'Module', 'Lecture', 'Room', 'Time'])
student_df.sort_values(by=['Student', 'Time'], inplace=True)

# Create a DataFrame for teacher lecture times
teacher_data = []

for teacher in teachers:
    teacher_id = teacher['teacher_id']
    for module, lectures in teacher['lectures'].items():
        for lecture in lectures:
            time = lecture_assignments[lecture]['time']
            room = lecture_assignments[lecture]['room']
            teacher_data.append([teacher_id, module, lecture, room, time])

teacher_df = pd.DataFrame(teacher_data, columns=['Teacher', 'Module', 'Lecture', 'Room', 'Time'])
teacher_df.sort_values(by=['Teacher', 'Time'], inplace=True)

# Export the DataFrames to Excel sheets in the same file
with pd.ExcelWriter('lecture_times.xlsx') as writer:
    student_df.to_excel(writer, sheet_name='Students', index=False)
    teacher_df.to_excel(writer, sheet_name='Teachers', index=False)

lecture_count_per_time_and_year_v4(lecture_assignments)

used_rooms_per_day = defaultdict(set)

for assignment in lecture_assignments.values():
    day = assignment['time'][:3]
    used_rooms_per_day[day].add(assignment['room'])

for day, rooms in used_rooms_per_day.items():
    print(f"Number of rooms used on {day}: {len(rooms)}")


lecture_count_per_day_and_time(lecture_assignments)


print('hi')

students_without_breaks_per_day = count_students_without_breaks_per_day(lecture_assignments, population)
print("Students without breaks between 11:15 and 15:15 per day (including total):", students_without_breaks_per_day)

