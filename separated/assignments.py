import itertools
from get_info import get_students_in_module, get_all_modules
from generation import generate_teacher_work_hours
from tqdm import tqdm
from collections import defaultdict
import random


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
    sorted_rooms = [room for cap in sorted(rooms_by_capacity.keys()) for room in (random.shuffle(rooms_by_capacity[cap]) or rooms_by_capacity[cap])]
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


def assign_rooms_and_times_v10a(population, teachers, rooms, capacity, optimal_hours, less_optimal_hours, postgrad_hours):
    lecture_assignments = {}
    
    # Wrap the outer loop with tqdm
    for teacher in tqdm(teachers, desc="Teachers"):
        for module, lectures in teacher['lectures'].items():
            for lecture in lectures:
                assigned = False
                
                # Determine the appropriate timeslots based on the lecture year
                year = int(lecture.split("_")[2][-1])
                if year == 4:
                    time_slots = postgrad_hours + optimal_hours + less_optimal_hours
                else:
                    time_slots = optimal_hours + less_optimal_hours
                
                for time_slot in time_slots:
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

def assign_rooms_and_times_v10b(population, teachers, rooms, capacity, optimal_hours, less_optimal_hours, postgrad_hours):
    print('Number of Timeslots:', len(postgrad_hours + optimal_hours + less_optimal_hours ))
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
    
    # Wrap the outer loop with tqdm
    for teacher, module, lecture, _, year in tqdm(sorted_teacher_lectures, desc="Lectures"):
        assigned = False

        if year == 4:
            time_slots = postgrad_hours + optimal_hours + less_optimal_hours
        else:
            time_slots = optimal_hours + less_optimal_hours
                
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


def assign_rooms_and_times_v10c(population, teachers, rooms, capacity, optimal_hours, less_optimal_hours, lesser_optimal_hours, postgrad_hours):
    lecture_assignments = {}
    print('Number of Timeslots:', len(postgrad_hours + optimal_hours + less_optimal_hours + lesser_optimal_hours))
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
    
    # Wrap the outer loop with tqdm
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


def get_adjacent_slots(time_slot):
    days = ['MON', 'TUE', 'WED', 'THU', 'FRI']
    times = ['08:15', '09:15', '10:15', '11:15', '12:15', '13:15', '14:15', '15:15', '16:15', '17:15', '18:15']
    day, time = time_slot[:3], time_slot[3:]
    
    adjacent_slots = []
    day_index = days.index(day)
    time_index = times.index(time)
    
    if time_index > 0:
        adjacent_slots.append(day + times[time_index - 1])
    if time_index < len(times) - 1:
        adjacent_slots.append(day + times[time_index + 1])
        
    return adjacent_slots

def assign_rooms_and_times_v10d(population, teachers, rooms, capacity, optimal_hours, less_optimal_hours, postgrad_hours):
    print('Number of Timeslots:', len(postgrad_hours + optimal_hours + less_optimal_hours ))
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
    
    # Wrap the outer loop with tqdm
    for teacher, module, lecture, _, year in tqdm(sorted_teacher_lectures, desc="Lectures"):
        assigned = False

        if year == 4:
            time_slots = postgrad_hours + optimal_hours + less_optimal_hours
        else:
            time_slots = optimal_hours + less_optimal_hours

        # Prioritize adjacent time slots to minimize days on campus
        for time_slot in time_slots:
            adjacent_slots = [adj_slot for adj_slot in get_adjacent_slots(time_slot) if adj_slot in time_slots]
            prioritized_slots = adjacent_slots + [time_slot]
            
            for slot in prioritized_slots:
                if assigned:
                    break

                for room in sorted_rooms:
                    student_names = [s['name'] for s in population if module in s['lectures'] and lecture in s['lectures'][module]]
                    
                    if len(student_names) > capacity[room]:
                        continue
                    
                    if any(assignment['room'] == room and assignment['time'] == slot for assignment in lecture_assignments.values()):
                        continue
                        
                    if not are_students_and_teacher_available(population, teacher, student_names, slot, lecture_assignments):
                        continue
                        
                    lecture_assignments[lecture] = {'room': room, 'time': slot}
                    assigned = True
                    break

    return lecture_assignments


def assign_rooms_and_times_v10e(population, teachers, rooms, capacity, optimal_hours, less_optimal_hours, postgrad_hours):
    print('Number of Timeslots:', len(postgrad_hours + optimal_hours + less_optimal_hours))
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

    # Wrap the outer loop with tqdm
    for teacher, module, lecture, _, year in tqdm(sorted_teacher_lectures, desc="Lectures"):
        assigned = False

        if year == 4:
            time_slots = postgrad_hours + optimal_hours + less_optimal_hours
        else:
            time_slots = optimal_hours + less_optimal_hours

        for time_slot in time_slots:
            adjacent_slots = [adj_slot for adj_slot in get_adjacent_slots(time_slot) if adj_slot in time_slots]
            
            # Reorder the time slots to prioritize 10:15 to 16:15
            prioritized_slots = sorted(adjacent_slots, key=lambda x: (x[3:] >= '10:15' and x[3:] <= '16:15', x))

            for slot in prioritized_slots:
                if assigned:
                    break

                for room in sorted_rooms:
                    student_names = [s['name'] for s in population if module in s['lectures'] and lecture in s['lectures'][module]]

                    if len(student_names) > capacity[room]:
                        continue

                    if any(assignment['room'] == room and assignment['time'] == slot for assignment in lecture_assignments.values()):
                        continue

                    if not are_students_and_teacher_available(population, teacher, student_names, slot, lecture_assignments):
                        continue

                    lecture_assignments[lecture] = {'room': room, 'time': slot}
                    assigned = True
                    break

    return lecture_assignments

def assign_rooms_and_times_v10f(population, teachers, rooms, capacity, optimal_hours, less_optimal_hours, postgrad_hours):
    print('Number of Timeslots:', len(postgrad_hours + optimal_hours + less_optimal_hours))
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

    # Wrap the outer loop with tqdm
    for teacher, module, lecture, _, year in tqdm(sorted_teacher_lectures, desc="Lectures"):
        assigned = False

        if year == 4:
            time_slots = postgrad_hours + optimal_hours + less_optimal_hours
        else:
            time_slots = optimal_hours + less_optimal_hours

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

def assign_rooms_and_times_v10g(population, teachers, rooms, capacity, optimal_hours, less_optimal_hours, lesser_optimal_hours, postgrad_hours):
    print('Number of Timeslots:', len(postgrad_hours + optimal_hours + less_optimal_hours + lesser_optimal_hours))
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

    # Wrap the outer loop with tqdm
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

