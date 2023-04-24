from get_info import get_students_in_module, get_all_modules

def is_valid_assignment(lecture, room, time, lecture_assignments, teachers, population):
    temp_assignment = lecture_assignments.copy()
    temp_assignment[lecture] = {'room': room, 'time': time}

    return check_multiple_lectures_same_time(teachers, population, temp_assignment)

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