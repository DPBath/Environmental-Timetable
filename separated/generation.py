import random
random.seed(10)
import string

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
