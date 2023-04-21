import random
random.seed(10)
import string
import openpyxl
import itertools
import pandas as pd
from tqdm import tqdm
from collections import defaultdict
from tabulate import tabulate
from random import shuffle


print('hi')
def read_excel_column_to_list(file_path, sheet_name, column, start_row, end_row):
    # Load the workbook and select the desired worksheet
    workbook = openpyxl.load_workbook(file_path)
    worksheet = workbook[sheet_name]

    # Read cells from the specified column and row range into a list
    output = [cell.value for cell in worksheet[column][start_row-1:end_row]]

    return output, workbook, worksheet

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


def generate_teacher_work_hours(teacher_id, early_start_prob=0.2, late_start_prob=0.2, working_days=['MON', 'TUE', 'WED', 'THU', 'FRI']):
    start_times = [8, 9, 10]
    
    # Choose start time based on the specified probabilities
    rand_value = random.random()
    if rand_value < early_start_prob:
        start_time = 8
    elif rand_value < late_start_prob:
        start_time = 10
    else:
        start_time = 9

    end_time = start_time + 8  # Ensure the teacher works 8 hours per day
        
    work_hours = []
    
    for day in working_days:
        for hour in range(start_time, end_time):
            work_hour = f'{day}{hour:02d}:15'
            if day == 'WED' and hour >= 14:  # Skip afternoon hours on Wednesday
                continue
            work_hours.append(work_hour)
    
    return work_hours


def find_students_in_same_module(population, target_module):
    students_in_module = []

    for student in population:
        if target_module in student['modules']:
            students_in_module.append(student['name'])

    return students_in_module

def count_students_by_faculty(population, faculty_names):
    faculty_counts = {faculty: 0 for faculty in faculty_names}

    for student in population:
        faculty_counts[student['faculty']] += 1

    return faculty_counts


def count_students_by_faculty_and_year(population, faculty_names, num_years):
    faculty_year_counts = {faculty: {f"Y{i+1}": 0 for i in range(num_years)} for faculty in faculty_names}

    for student in population:
        faculty_year_counts[student['faculty']][student['year']] += 1

    return faculty_year_counts

def print_table(faculty_year_counts):
    header = "Faculty/Year\t" + "\t".join(f"Y{i+1}" for i in range(len(faculty_year_counts[next(iter(faculty_year_counts))])))
    print(header)

    for faculty, year_counts in faculty_year_counts.items():
        row = f"{faculty}\t\t" + "\t".join(str(year_counts[f"Y{i+1}"]) for i in range(len(year_counts)))
        print(row)

def generate_population(students_per_faculty_year, faculty_names, num_courses_list, year_percentages, num_assigned_modules, num_total_modules, num_lectures_list):
    assert len(students_per_faculty_year[0]) == len(faculty_names) == len(num_courses_list[0]) == len(num_lectures_list), "Length of students_per_faculty_year, faculty_names, num_courses_list, and num_lectures_list must be equal"
    assert sum(year_percentages) == 100, "Sum of year_percentages must be equal to 100"

    def generate_unique_id(existing_ids):
        unique_id = ''.join(random.choices(string.ascii_uppercase, k=5))
        while unique_id in existing_ids:
            unique_id = ''.join(random.choices(string.ascii_uppercase, k=5))
        return unique_id

    population = []
    unique_ids = set()

    for year_idx, year_student_count in enumerate(students_per_faculty_year):
        year = f"Y{year_idx+1}"

        for idx, (faculty_student_count, faculty_name, num_courses, num_lectures) in enumerate(zip(year_student_count, faculty_names, num_courses_list[year_idx], num_lectures_list)):
            num_students_in_faculty = faculty_student_count

            for i in range(num_students_in_faculty):
                course = f"C{random.randint(1, num_courses)}"
                unique_id = generate_unique_id(unique_ids)
                unique_ids.add(unique_id)
                student_name = f"{faculty_name}_{course}_{year}_{unique_id}"

                module_prefix = f"{faculty_name}_{course}_{year}_M"
                available_modules = [f"{module_prefix}{i+1}" for i in range(num_total_modules)]
                assigned_modules = random.sample(available_modules, num_assigned_modules)

                lectures = {}
                for module in assigned_modules:
                    module_lectures = [f"{module}_L{j+1}" for j in range(num_lectures)]
                    lectures[module] = module_lectures

                student = {
                    'name': student_name,
                    'faculty': faculty_name,
                    'course': course,
                    'year': year,
                    'unique_id': unique_id,
                    'modules': assigned_modules,
                    'lectures': lectures
                }

                population.append(student)

    return population


def check_assigned_modules(population, num_assigned_modules):
    incorrect_module_counts = {}

    for student in population:
        assigned_module_count = len(student['modules'])

        if assigned_module_count != num_assigned_modules:
            incorrect_module_counts[student['name']] = assigned_module_count

    if not incorrect_module_counts:
        print("All students have the correct number of assigned modules.")
    else:
        for student_name, module_count in incorrect_module_counts.items():
            print(f"Student {student_name} has {module_count} assigned modules instead of {num_assigned_modules}.")


def display_students_in_lecture(population, target_lecture):
    students_in_lecture = []

    for student in population:
        for module, lectures in student['lectures'].items():
            if target_lecture in lectures:
                students_in_lecture.append(student['name'])
                break

    print(f"\nStudents in lecture {target_lecture}:")
    for student_name in students_in_lecture:
        print(student_name)


def print_unique_modules_and_lectures(population):
    unique_modules = set()
    unique_lectures = set()

    for student in population:
        for module in student['modules']:
            unique_modules.add(module)
        for lectures in student['lectures'].values():
            for lecture in lectures:
                unique_lectures.add(lecture)
    print ('')
    print(f"Total unique modules in the population: {len(unique_modules)}")
    print(f"Total unique lectures in the population: {len(unique_lectures)}")


def get_all_modules(population):
    all_modules = set()
    
    for student in population:
        for module in student['modules']:
            all_modules.add(module)
    
    return list(all_modules)


def assign_modules_to_teachers(population, num_teachers_per_faculty, faculty_names, num_lectures_list, early_start_prob=0.2, late_start_prob=0.2):
    all_modules = get_all_modules(population)
    faculty_modules = {faculty: set() for faculty in faculty_names}
    
    for module in all_modules:
        faculty = module.split('_')[0]
        faculty_modules[faculty].add(module)
    
    teachers = []
    teacher_id = 1
    
    for faculty, num_teachers, num_lectures in zip(faculty_names, num_teachers_per_faculty, num_lectures_list):
        modules = list(faculty_modules[faculty])
        faculty_teachers = []

        for i in range(num_teachers):
            teacher = {
                'teacher_id': teacher_id,
                'faculty': faculty,
                'modules': [],
                'lectures': {},
                'work_hours': generate_teacher_work_hours(teacher_id, early_start_prob, late_start_prob)
            }
            faculty_teachers.append(teacher)
            teacher_id += 1

        for module_idx, module in enumerate(modules):
            teacher_idx = module_idx % num_teachers
            faculty_teachers[teacher_idx]['modules'].append(module)

            # Assign lectures to teachers
            module_lectures = [f"{module}_L{j+1}" for j in range(num_lectures)]
            faculty_teachers[teacher_idx]['lectures'][module] = module_lectures

        teachers.extend(faculty_teachers)
            
    return teachers


def check_module_assignment(population, teachers):
    all_modules = get_all_modules(population)
    assigned_modules = set()
    
    for teacher in teachers:
        for module in teacher['modules']:
            assigned_modules.add(module)

    unassigned_modules = set(all_modules) - assigned_modules

    if unassigned_modules:
        print(f"Unassigned modules with students: {unassigned_modules}")
        return False
    else:
        print("All modules with students are assigned to teachers.")
        return True


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

def get_all_lectures(population):
    all_lectures = set()

    for student in population:
        for module_lectures in student['lectures'].values():
            all_lectures.update(module_lectures)

    return sorted(list(all_lectures))


def get_number_of_students_in_module(population, module):
    count = 0
    for student in population:
        if module in student['modules']:
            count += 1
    return count

def get_module_faculty(module):
    return module.split('_')[0]


def check_multiple_lectures_same_time(teachers, students, lecture_assignments):
    teacher_timeslots = {}
    student_timeslots = {}

    for lecture, assignment in lecture_assignments.items():
        room, time_slot = assignment['room'], assignment['time']

        # Check teacher availability
        teacher_id = lecture.split("_")[1]
        teacher_list = [t for t in teachers if t['teacher_id'] == teacher_id]

        if not teacher_list:
            return False

        teacher = teacher_list[0]

        if teacher_id not in teacher_timeslots:
            teacher_timeslots[teacher_id] = []

        if time_slot in teacher_timeslots[teacher_id]:
            return False

        teacher_timeslots[teacher_id].append(time_slot)

        # Check student availability
        module = lecture.split("_")[0]
        students_in_module = get_students_in_module(students, module)

        for student in students_in_module:
            student_name = student['name']

            if student_name not in student_timeslots:
                student_timeslots[student_name] = []

            if time_slot in student_timeslots[student_name]:
                return False

            student_timeslots[student_name].append(time_slot)

    return True


def get_students_in_module(population, module):
    students_in_module = []

    for student in population:
        if module in student['modules']:
            students_in_module.append(student)

    return students_in_module


def is_valid_assignment(lecture, room, time, lecture_assignments, teachers, population):
    temp_assignment = lecture_assignments.copy()
    temp_assignment[lecture] = {'room': room, 'time': time}

    return check_multiple_lectures_same_time(teachers, population, temp_assignment)


def check_teacher_availability(teacher, lecture_assignments, time_slot):
    for lecture, assignment in lecture_assignments.items():
        if str(teacher['teacher_id']) in lecture and assignment['time'] == time_slot:  # Fix: Convert teacher_id to string
            return False
    return True



def check_students_availability(module, population, lecture_assignments, time_slot):
    students_in_module = get_students_in_module(population, module)

    for student in students_in_module:
        student_lectures = list(itertools.chain(*student['lectures'].values()))
        for lecture in student_lectures:
            if lecture in lecture_assignments and lecture_assignments[lecture]['time'] == time_slot:
                return False

    return True


def are_students_and_teacher_available(population, teacher, student_names, time_slot, lecture_assignments):
    for student_name in student_names:
        student = next(s for s in population if s['name'] == student_name)
        for module, lectures in student['lectures'].items():
            for lecture in lectures:
                if lecture in lecture_assignments and lecture_assignments[lecture]['time'] == time_slot:
                    return False

    teacher_id = teacher['teacher_id']
    for module, lectures in teacher['lectures'].items():
        for lecture in lectures:
            if lecture in lecture_assignments and lecture_assignments[lecture]['time'] == time_slot:
                return False

    return True

def are_students_and_teacher_available_v2(population, teachers, teacher, student_names, time_slot, lecture_assignments):
    restricted_slots = ['Mon_11:15', 'Mon_12:15', 'Mon_13:15', 'Mon_14:15']

    def check_availability(entity, restricted_slots):
        restricted_slot_count = 0
        for module, lectures in entity['lectures'].items():
            for lecture in lectures:
                if lecture in lecture_assignments and lecture_assignments[lecture]['time'] in restricted_slots:
                    restricted_slot_count += 1
                    if restricted_slot_count >= 3:
                        return False
                if lecture in lecture_assignments and lecture_assignments[lecture]['time'] == time_slot:
                    return False
        return True

    for student_name in student_names:
        student = next(s for s in population if s['name'] == student_name)
        if not check_availability(student, restricted_slots):
            return False

    if not check_availability(teacher, restricted_slots):
        return False

    return True





def assign_rooms_and_times_v10(population, teachers, rooms, capacity, all_hours):
    lecture_assignments = {}
    
    # Wrap the outer loop with tqdm
    for teacher in tqdm(teachers, desc="Teachers"):
        for module, lectures in teacher['lectures'].items():
            for lecture in lectures:
                assigned = False
                
                for time_slot in all_hours:
                    if assigned:
                        break
                        
                    for room in rooms:
                        student_names = [s['name'] for s in population if module in s['lectures'] and lecture in s['lectures'][module]]
                        
                        if len(student_names) > capacity[room]:
                            continue
                        
                        if any(assignment['room'] == room and assignment['time'] == time_slot for assignment in lecture_assignments.values()):
                            continue
                            
                        if not are_students_and_teacher_available(population, teacher, student_names, time_slot, lecture_assignments):
                            continue
                            
                        lecture_assignments[lecture] = {'room': room, 'time': time_slot}
                        assigned = True
                        break

    return lecture_assignments

def assign_rooms_and_times_v11(population, teachers, rooms, capacity, all_hours):
    lecture_assignments = {}
    
    # Sort rooms by capacity (smallest to largest)
    sorted_rooms = sorted(rooms, key=lambda x: capacity[x])

    # Sort teachers' lectures by class size (largest to smallest)
    sorted_teacher_lectures = []
    for teacher in teachers:
        for module, lectures in teacher['lectures'].items():
            for lecture in lectures:
                student_names = [s['name'] for s in population if module in s['lectures'] and lecture in s['lectures'][module]]
                sorted_teacher_lectures.append((teacher, module, lecture, len(student_names)))
    sorted_teacher_lectures.sort(key=lambda x: x[3], reverse=True)

    for teacher, module, lecture, _ in tqdm(sorted_teacher_lectures, desc="Lectures"):
        assigned = False

        for time_slot in all_hours:
            if assigned:
                break

            for room in sorted_rooms:
                student_names = [s['name'] for s in population if module in s['lectures'] and lecture in s['lectures'][module]]

                if len(student_names) > capacity[room]:
                    continue

                if any(assignment['room'] == room and assignment['time'] == time_slot for assignment in lecture_assignments.values()):
                    continue

                if not are_students_and_teacher_available(population, teacher, student_names, time_slot, lecture_assignments):
                    continue

                lecture_assignments[lecture] = {'room': room, 'time': time_slot}
                assigned = True
                break

    return lecture_assignments

def assign_rooms_and_times_v12(population, teachers, rooms, capacity, optimal_hours, less_optimal_hours, lesser_optimal_hours):
    lecture_assignments = {}
    
    # Sort rooms by capacity (smallest to largest)
    sorted_rooms = sorted(rooms, key=lambda x: capacity[x])

    # Sort teachers' lectures by class size (largest to smallest)
    sorted_teacher_lectures = []
    for teacher in teachers:
        for module, lectures in teacher['lectures'].items():
            for lecture in lectures:
                student_names = [s['name'] for s in population if module in s['lectures'] and lecture in s['lectures'][module]]
                sorted_teacher_lectures.append((teacher, module, lecture, len(student_names)))
    sorted_teacher_lectures.sort(key=lambda x: x[3], reverse=True)

    priority_hours = [optimal_hours, less_optimal_hours, lesser_optimal_hours]

    for teacher, module, lecture, _ in tqdm(sorted_teacher_lectures, desc="Lectures"):
        assigned = False

        for priority in priority_hours:
            if assigned:
                break

            for time_slot in priority:
                if assigned:
                    break

                for room in sorted_rooms:
                    student_names = [s['name'] for s in population if module in s['lectures'] and lecture in s['lectures'][module]]

                    if len(student_names) > capacity[room]:
                        continue

                    if any(assignment['room'] == room and assignment['time'] == time_slot for assignment in lecture_assignments.values()):
                        continue

                    if not are_students_and_teacher_available(population, teacher, student_names, time_slot, lecture_assignments):
                        continue

                    lecture_assignments[lecture] = {'room': room, 'time': time_slot}
                    assigned = True
                    break

    return lecture_assignments


def assign_rooms_and_times_v13(population, teachers, rooms, capacity, optimal_hours, less_optimal_hours, lesser_optimal_hours):
    lecture_assignments = {}
    
    # Sort rooms by capacity (smallest to largest)
    sorted_rooms = sorted(rooms, key=lambda x: capacity[x])

    # Sort teachers' lectures by class size (largest to smallest) and year (higher years first)
    sorted_teacher_lectures = []
    for teacher in teachers:
        for module, lectures in teacher['lectures'].items():
            for lecture in lectures:
                student_names = [s['name'] for s in population if module in s['lectures'] and lecture in s['lectures'][module]]
                year = int(lecture.split("_")[2][-1])
                sorted_teacher_lectures.append((teacher, module, lecture, len(student_names), year))
    sorted_teacher_lectures.sort(key=lambda x: (x[4], x[3]), reverse=True)

    priority_hours = [optimal_hours, less_optimal_hours, lesser_optimal_hours]

    for teacher, module, lecture, _, _ in tqdm(sorted_teacher_lectures, desc="Lectures"):
        assigned = False

        for priority in priority_hours:
            if assigned:
                break

            for time_slot in priority:
                if assigned:
                    break

                for room in sorted_rooms:
                    student_names = [s['name'] for s in population if module in s['lectures'] and lecture in s['lectures'][module]]

                    if len(student_names) > capacity[room]:
                        continue

                    if any(assignment['room'] == room and assignment['time'] == time_slot for assignment in lecture_assignments.values()):
                        continue

                    if not are_students_and_teacher_available(population, teacher, student_names, time_slot, lecture_assignments):
                        continue

                    lecture_assignments[lecture] = {'room': room, 'time': time_slot}
                    assigned = True
                    break

    return lecture_assignments


def assign_rooms_and_times_v15(population, teachers, rooms, capacity, optimal_hours, less_optimal_hours, lesser_optimal_hours):
    lecture_assignments = {}
    
    # Sort rooms by capacity (smallest to largest)
    sorted_rooms = sorted(rooms, key=lambda x: capacity[x])

    # Sort teachers' lectures by class size (largest to smallest) and year (higher years first)
    sorted_teacher_lectures = []
    for teacher in teachers:
        for module, lectures in teacher['lectures'].items():
            for lecture in lectures:
                student_names = [s['name'] for s in population if module in s['lectures'] and lecture in s['lectures'][module]]
                year = int(lecture.split("_")[2][-1])
                sorted_teacher_lectures.append((teacher, module, lecture, len(student_names), year))
    sorted_teacher_lectures.sort(key=lambda x: (x[4], x[3]), reverse=True)

    priority_hours = [optimal_hours, less_optimal_hours, lesser_optimal_hours]

    def get_day(time_slot):
        return time_slot.split("_")[0]

    for teacher, module, lecture, _, _ in tqdm(sorted_teacher_lectures, desc="Lectures"):
        assigned = False

        for priority in priority_hours:
            if assigned:
                break

            # Group time slots by day
            grouped_time_slots = {day: [time_slot for time_slot in priority if get_day(time_slot) == day] for day in set(get_day(time_slot) for time_slot in priority)}

            for day, time_slots in grouped_time_slots.items():
                if assigned:
                    break

                for time_slot in time_slots:
                    if assigned:
                        break

                    for room in sorted_rooms:
                        student_names = [s['name'] for s in population if module in s['lectures'] and lecture in s['lectures'][module]]

                        if len(student_names) > capacity[room]:
                            continue

                        if any(assignment['room'] == room and assignment['time'] == time_slot for assignment in lecture_assignments.values()):
                            continue

                        if not are_students_and_teacher_available(population, teacher, student_names, time_slot, lecture_assignments):
                            continue

                        lecture_assignments[lecture] = {'room': room, 'time': time_slot}
                        assigned = True
                        break

    return lecture_assignments

def assign_rooms_and_times_v16(population, teachers, rooms, capacity, optimal_hours, less_optimal_hours, lesser_optimal_hours):
    lecture_assignments = {}

    # Sort rooms by capacity (smallest to largest)
    sorted_rooms = sorted(rooms, key=lambda x: capacity[x])

    # Sort teachers' lectures by class size (largest to smallest) and year (higher years first)
    sorted_teacher_lectures = []
    for teacher in teachers:
        for module, lectures in teacher['lectures'].items():
            for lecture in lectures:
                student_names = [s['name'] for s in population if module in s['lectures'] and lecture in s['lectures'][module]]
                year = int(lecture.split("_")[2][-1])
                sorted_teacher_lectures.append((teacher, module, lecture, len(student_names), year))
    sorted_teacher_lectures.sort(key=lambda x: (x[4], x[3]), reverse=True)

    priority_hours = [optimal_hours, less_optimal_hours, lesser_optimal_hours]

    for teacher, module, lecture, _, _ in tqdm(sorted_teacher_lectures, desc="Lectures"):
        assigned = False

        student_lecture_days = defaultdict(set)
        for la, assignment in lecture_assignments.items():
            for s in population:
                if module in s['lectures'] and la in s['lectures'][module]:
                    student_lecture_days[s['name']].add(assignment['time'][:3])

        for priority in priority_hours:
            if assigned:
                break

            for time_slot in priority:
                if assigned:
                    break

                for room in sorted_rooms:
                    student_names = [s['name'] for s in population if module in s['lectures'] and lecture in s['lectures'][module]]

                    if len(student_names) > capacity[room]:
                        continue

                    if any(assignment['room'] == room and assignment['time'] == time_slot for assignment in lecture_assignments.values()):
                        continue

                    if not are_students_and_teacher_available(population, teacher, student_names, time_slot, lecture_assignments):
                        continue

                    # Removed the condition that checks if the new number of days is greater than the current number of days
                    lecture_assignments[lecture] = {'room': room, 'time': time_slot}
                    assigned = True
                    break

    return lecture_assignments

def assign_rooms_and_times_v17(population, teachers, rooms, capacity, optimal_hours, less_optimal_hours, lesser_optimal_hours):
    lecture_assignments = {}

    # Sort rooms by capacity (smallest to largest)
    # Group rooms by capacity
    rooms_by_capacity = defaultdict(list)
    for room in rooms:
        rooms_by_capacity[capacity[room]].append(room)

    # Shuffle rooms within each capacity group and then flatten the list
    sorted_rooms = [room for cap in sorted(rooms_by_capacity.keys()) for room in (shuffle(rooms_by_capacity[cap]) or rooms_by_capacity[cap])]
    # Sort teachers' lectures by class size (largest to smallest) and year (higher years first)
    sorted_teacher_lectures = []
    for teacher in teachers:
        for module, lectures in teacher['lectures'].items():
            for lecture in lectures:
                student_names = [s['name'] for s in population if module in s['lectures'] and lecture in s['lectures'][module]]
                year = int(lecture.split("_")[2][-1])
                sorted_teacher_lectures.append((teacher, module, lecture, len(student_names), year))
    sorted_teacher_lectures.sort(key=lambda x: (x[4], x[3]), reverse=True)

    priority_hours = [optimal_hours, less_optimal_hours, lesser_optimal_hours]

    for teacher, module, lecture, _, _ in tqdm(sorted_teacher_lectures, desc="Lectures"):
        assigned = False

        student_lecture_days = defaultdict(set)
        for la, assignment in lecture_assignments.items():
            for s in population:
                if module in s['lectures'] and la in s['lectures'][module]:
                    student_lecture_days[s['name']].add(assignment['time'][:3])

        for priority in priority_hours:
            if assigned:
                break

            for time_slot in priority:
                if assigned:
                    break

                for room in sorted_rooms:
                    student_names = [s['name'] for s in population if module in s['lectures'] and lecture in s['lectures'][module]]

                    if len(student_names) > capacity[room]:
                        continue

                    if any(assignment['room'] == room and assignment['time'] == time_slot for assignment in lecture_assignments.values()):
                        continue

                    if not are_students_and_teacher_available(population, teacher, student_names, time_slot, lecture_assignments):
                        continue

                    # Removed the condition that checks if the new number of days is greater than the current number of days
                    lecture_assignments[lecture] = {'room': room, 'time': time_slot}
                    assigned = True
                    break

    return lecture_assignments

def assign_rooms_and_times_v18(population, teachers, rooms, capacity, optimal_hours, less_optimal_hours, lesser_optimal_hours, postgrad_hours):
    lecture_assignments = {}

    # Reorder time slots to start with Wednesday
    def reorder_time_slots(time_slots):
        wed_slots = [slot for slot in time_slots if slot.startswith("Wed")]
        other_slots = [slot for slot in time_slots if not slot.startswith("Wed")]
        return wed_slots + other_slots

    optimal_hours = reorder_time_slots(optimal_hours)
    less_optimal_hours = reorder_time_slots(less_optimal_hours)
    lesser_optimal_hours = reorder_time_slots(lesser_optimal_hours)
    postgrad_hours = reorder_time_slots(postgrad_hours)

    # Sort rooms by capacity (smallest to largest)
    sorted_rooms = sorted(rooms, key=lambda x: capacity[x])

    # Sort teachers' lectures by class size (largest to smallest) and year (higher years first)
    sorted_teacher_lectures = []
    for teacher in teachers:
        for module, lectures in teacher['lectures'].items():
            for lecture in lectures:
                student_names = [s['name'] for s in population if module in s['lectures'] and lecture in s['lectures'][module]]
                year = int(lecture.split("_")[2][-1])
                sorted_teacher_lectures.append((teacher, module, lecture, len(student_names), year))
    sorted_teacher_lectures.sort(key=lambda x: (x[4], x[3]), reverse=True)

    for teacher, module, lecture, _, year in tqdm(sorted_teacher_lectures, desc="Lectures"):
        assigned = False

        if year == 4:
            time_slots = postgrad_hours + optimal_hours + less_optimal_hours + lesser_optimal_hours
        else:
            time_slots = optimal_hours + less_optimal_hours + lesser_optimal_hours

        for time_slot in time_slots:
            if assigned:
                break

            for room in sorted_rooms:
                student_names = [s['name'] for s in population if module in s['lectures'] and lecture in s['lectures'][module]]

                if len(student_names) > capacity[room]:
                    continue

                if any(assignment['room'] == room and assignment['time'] == time_slot for assignment in lecture_assignments.values()):
                    continue

                if not are_students_and_teacher_available(population, teacher, student_names, time_slot, lecture_assignments):
                    continue

                lecture_assignments[lecture] = {'room': room, 'time': time_slot}
                assigned = True
                break

    return lecture_assignments



def assign_rooms_and_times_v19(population, teachers, rooms, capacity, optimal_hours, less_optimal_hours, lesser_optimal_hours, postgrad_hours):
    lecture_assignments = {}

    # Reorder time slots to start with Wednesday
    def reorder_time_slots(time_slots):
        wed_slots = [slot for slot in time_slots if slot.startswith("Wed")]
        other_slots = [slot for slot in time_slots if not slot.startswith("Wed")]
        return wed_slots + other_slots

    optimal_hours = reorder_time_slots(optimal_hours)
    less_optimal_hours = reorder_time_slots(less_optimal_hours)
    lesser_optimal_hours = reorder_time_slots(lesser_optimal_hours)
    postgrad_hours = reorder_time_slots(postgrad_hours)

    # Sort rooms by capacity (smallest to largest)
    sorted_rooms = sorted(rooms, key=lambda x: capacity[x])

    # Sort teachers' lectures by class size (largest to smallest) and year (higher years first)
    sorted_teacher_lectures = []
    for teacher in teachers:
        for module, lectures in teacher['lectures'].items():
            for lecture in lectures:
                student_names = [s['name'] for s in population if module in s['lectures'] and lecture in s['lectures'][module]]
                year = int(lecture.split("_")[2][-1])
                sorted_teacher_lectures.append((teacher, module, lecture, len(student_names), year))
    sorted_teacher_lectures.sort(key=lambda x: (x[4], x[3]), reverse=True)

    for teacher, module, lecture, _, year in tqdm(sorted_teacher_lectures, desc="Lectures"):
        assigned = False

        if year == 4:
            time_slots = postgrad_hours + optimal_hours + less_optimal_hours + lesser_optimal_hours
        else:
            time_slots = optimal_hours + less_optimal_hours + lesser_optimal_hours

        for time_slot in time_slots:
            if assigned:
                break

            for room in sorted_rooms:
                student_names = [s['name'] for s in population if module in s['lectures'] and lecture in s['lectures'][module]]

                if len(student_names) > capacity[room]:
                    continue

                if any(assignment['room'] == room and assignment['time'] == time_slot for assignment in lecture_assignments.values()):
                    continue

                if not are_students_and_teacher_available_v2(population, teachers, teacher, student_names, time_slot, lecture_assignments):
                    continue

                lecture_assignments[lecture] = {'room': room, 'time': time_slot}
                assigned = True
                break

    return lecture_assignments




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


def count_unassigned_lectures(lecture_assignments):
    unassigned_count = 0
    for lecture, assignment in lecture_assignments.items():
        if not assignment['room'] or not assignment['time']:
            unassigned_count += 1
    return unassigned_count


def get_all_lectures_from_population(population):
    all_lectures = set()
    for student in population:
        for lectures in student['lectures'].values():
            all_lectures.update(lectures)
    return all_lectures


def count_students_per_lecture(population, lecture_assignments):
    student_counts = {lecture: 0 for lecture in lecture_assignments}

    for student in population:
        for module, lectures in student['lectures'].items():
            for lecture in lectures:
                if lecture in student_counts:
                    student_counts[lecture] += 1
                else:
                    print(f"Warning: Lecture {lecture} not found in lecture_assignments")

    return student_counts


def get_room_sizes(lecture_assignments, room_capacity):
    room_sizes = {}

    for lecture, assignment in lecture_assignments.items():
        room = assignment['room']
        room_sizes[lecture] = room_capacity.get(room, None)

    return room_sizes


def check_room_capacity(lecture_student_counts, lecture_room_sizes):
    insufficient_rooms = []
    rooms_not_found = []

    for lecture, student_count in lecture_student_counts.items():
        room_size = lecture_room_sizes.get(lecture, None)

        if room_size is None:
            rooms_not_found.append(lecture)
        elif room_size < student_count:
            insufficient_rooms.append((lecture, room_size, student_count))

    if not insufficient_rooms and not rooms_not_found:
        print("All rooms sufficiently sized")
    else:
        if insufficient_rooms:
            print("Insufficient room capacities:")
            for lecture, room_size, student_count in insufficient_rooms:
                print(f"{lecture}: Capacity: {room_size}, Students: {student_count}")
            print()

        if rooms_not_found:
            print("Rooms not found:")
            for lecture in rooms_not_found:
                print(f"{lecture}")
            print()


def check_room_allocations(lecture_assignments):
    timeslot_rooms = {}

    for lecture, assignment in lecture_assignments.items():
        room = assignment['room']
        time = assignment['time']

        if time not in timeslot_rooms:
            timeslot_rooms[time] = set()

        if room in timeslot_rooms[time]:
            print(f"Room {room} has been allocated more than once at timeslot {time}")
            return False
        else:
            timeslot_rooms[time].add(room)

    print("All rooms allocated only once per timeslot")
    return True

def check_allocations(population, teachers, lecture_assignments):
    student_timeslots = {}
    teacher_timeslots = {}

    clashes_found = False

    for student in population:
        student_name = student['name']
        for module, lectures in student['lectures'].items():
            for lecture in lectures:
                time = lecture_assignments[lecture]['time']

                if student_name not in student_timeslots:
                    student_timeslots[student_name] = {}

                if time in student_timeslots[student_name] and student_timeslots[student_name][time] != lecture:
                    print(f"Student {student_name} has more than one lecture at timeslot {time}")
                    print(f"Current lecture: {lecture}, Previous lecture: {student_timeslots[student_name][time]}")
                    clashes_found = True
                else:
                    student_timeslots[student_name][time] = lecture

    for teacher in teachers:
        teacher_id = teacher['teacher_id']
        for module, lectures in teacher['lectures'].items():
            for lecture in lectures:
                time = lecture_assignments[lecture]['time']

                if teacher_id not in teacher_timeslots:
                    teacher_timeslots[teacher_id] = {}

                if time in teacher_timeslots[teacher_id] and teacher_timeslots[teacher_id][time] != lecture:
                    print(f"Teacher {teacher_id} has more than one lecture at timeslot {time}")
                    print(f"Current lecture: {lecture}, Previous lecture: {teacher_timeslots[teacher_id][time]}")
                    clashes_found = True
                else:
                    teacher_timeslots[teacher_id][time] = lecture

    if not clashes_found:
        print("No clashes found")

    return student_timeslots, teacher_timeslots, not clashes_found


def get_unassigned_room_timeslots(lecture_assignments, rooms, time_slots):
    assigned_room_times = {}
    for assignment in lecture_assignments.values():
        room_time = (assignment['room'], assignment['time'])
        assigned_room_times[room_time] = True

    unassigned_room_timeslots = {}
    for room in rooms:
        unassigned_times = []
        for time_slot in time_slots:
            if (room, time_slot) not in assigned_room_times:
                unassigned_times.append(time_slot)
        unassigned_room_timeslots[room] = unassigned_times

    return unassigned_room_timeslots


def count_days_at_university(student_timeslots, student_name):
    days = set()
    
    for time_slot in student_timeslots[student_name]:
        day = time_slot[:3]
        days.add(day)
    
    return len(days)


def average_days_per_faculty_and_university(population, student_timeslots):
    faculty_year_days = defaultdict(lambda: defaultdict(lambda: {'students': 0, 'total_days': 0}))
    university_year_days = defaultdict(lambda: {'students': 0, 'total_days': 0})

    for student in population:
        student_name = student['name']
        faculty = student['faculty']
        year = student['year']

        days_at_university = count_days_at_university(student_timeslots, student_name)

        faculty_year_days[faculty][year]['students'] += 1
        faculty_year_days[faculty][year]['total_days'] += days_at_university

        university_year_days[year]['students'] += 1
        university_year_days[year]['total_days'] += days_at_university

    faculty_year_averages = {
        faculty: {year: info['total_days'] / info['students'] for year, info in year_info.items()}
        for faculty, year_info in faculty_year_days.items()
    }
    university_year_averages = {
        year: info['total_days'] / info['students'] for year, info in university_year_days.items()
    }

    # Print the table
    unique_years = sorted(set(student['year'] for student in population))
    sorted_faculties = sorted(faculty_year_averages.keys())
    print('')
    print('Average number of days spent on campus per year and faculty')
    header = "Faculty\t" + "\t".join(unique_years)
    print(header)

    for faculty in sorted_faculties:
        year_averages = faculty_year_averages[faculty]
        row = f"{faculty}\t" + "\t".join(f"{year_averages.get(year, 0):.2f}" for year in unique_years)
        print(row)

    # Print the 'All' row for the entire university
    print('All\t' + "\t".join(f"{university_year_averages.get(year, 0):.2f}" for year in unique_years))
    print('')

    return faculty_year_averages


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

def lecture_count_per_day_and_time(lecture_assignments):
    day_time_count = defaultdict(lambda: defaultdict(int))

    for lecture, assignment in lecture_assignments.items():
        day = assignment['time'][:3]
        time = assignment['time'][3:]

        day_time_count[day][time] += 1

    # Find all unique days and times in the data
    day_order = ['MON', 'TUE', 'WED', 'THU', 'FRI']
    unique_days = sorted(set(day for day in day_time_count.keys()), key=lambda x: day_order.index(x))
    unique_times = sorted(set(time for time_counts in day_time_count.values() for time in time_counts.keys()))

    # Print the table
    header = "Time\t" + "\t".join(unique_days)
    print(header)

    for time in unique_times:
        row = f"{time}\t" + "\t".join(str(day_time_count[day][time]) for day in unique_days)
        print(row)


def count_students_without_breaks(lecture_assignments):
    students_without_breaks = 0

    for s in population:
        student_lecture_times = defaultdict(list)

        for module, lecture in s['lectures'].items():
            for la in lecture:
                if la in lecture_assignments:
                    time_slot = lecture_assignments[la]['time']
                    day, time = time_slot.split()
                    student_lecture_times[day].append(time)

        for day, times in student_lecture_times.items():
            times = sorted(times)
            has_continuous_lectures = False

            for i in range(len(times) - 3):
                if times[i] == "11:15" and times[i + 1] == "12:15" and times[i + 2] == "13:15" and times[i + 3] == "14:15":
                    has_continuous_lectures = True
                    break

            if has_continuous_lectures:
                students_without_breaks += 1
                break

    return students_without_breaks

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

def count_students_without_breaks_per_day(lecture_assignments):
    students_without_breaks = defaultdict(int, {'MON': 0, 'TUE': 0, 'WED': 0, 'THU': 0, 'FRI': 0, 'ALL': 0})

    for s in population:
        student_lecture_times = defaultdict(list)

        for module, lecture in s['lectures'].items():
            for la in lecture:
                if la in lecture_assignments:
                    time_slot = lecture_assignments[la]['time']
                    day, time = time_slot[:2], time_slot[2:]
                    student_lecture_times[day].append(time)

        for day, times in student_lecture_times.items():
            times = sorted(times)
            has_continuous_lectures = False

            for i in range(len(times) - 3):
                if times[i] == "11:15" and times[i + 1] == "12:15" and times[i + 2] == "13:15" and times[i + 3] == "14:15":
                    has_continuous_lectures = True
                    break

            if has_continuous_lectures:
                students_without_breaks[day] += 1
                students_without_breaks['ALL'] += 1

    return students_without_breaks

students_without_breaks_per_day = count_students_without_breaks_per_day(lecture_assignments)
print("Students without breaks between 11:15 and 15:15 per day (including total):", students_without_breaks_per_day)

