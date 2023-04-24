from collections import defaultdict

def count_unassigned_lectures(lecture_assignments):
    unassigned_count = 0
    for lecture, assignment in lecture_assignments.items():
        if not assignment['room'] or not assignment['time']:
            unassigned_count += 1
    return unassigned_count

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

def count_students_without_breaks(lecture_assignments, population):
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

def count_students_without_breaks_per_day(lecture_assignments, population):
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

