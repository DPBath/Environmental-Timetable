def get_all_modules(population):
    all_modules = set()
    
    for student in population:
        for module in student['modules']:
            all_modules.add(module)
    
    return list(all_modules)

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

def get_students_in_module(population, module):
    students_in_module = []

    for student in population:
        if module in student['modules']:
            students_in_module.append(student)

    return students_in_module

def get_all_lectures_from_population(population):
    all_lectures = set()
    for student in population:
        for lectures in student['lectures'].values():
            all_lectures.update(lectures)
    return all_lectures

def get_room_sizes(lecture_assignments, room_capacity):
    room_sizes = {}

    for lecture, assignment in lecture_assignments.items():
        room = assignment['room']
        room_sizes[lecture] = room_capacity.get(room, None)

    return room_sizes

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

def find_students_in_same_module(population, target_module):
    students_in_module = []

    for student in population:
        if target_module in student['modules']:
            students_in_module.append(student['name'])

    return students_in_module
