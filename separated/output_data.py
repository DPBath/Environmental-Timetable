def print_table(faculty_year_counts):
    header = "Faculty/Year\t" + "\t".join(f"Y{i+1}" for i in range(len(faculty_year_counts[next(iter(faculty_year_counts))])))
    print(header)

    for faculty, year_counts in faculty_year_counts.items():
        row = f"{faculty}\t\t" + "\t".join(str(year_counts[f"Y{i+1}"]) for i in range(len(year_counts)))
        print(row)


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
