import json
import os

BASE_DIR = os.path.dirname(os.path.abspath(__file__))
DATA_DIR = os.path.join(BASE_DIR, "data")


def load_json(filepath):
    with open(filepath, encoding="utf-8") as f:
        return json.load(f)


def analyze_course_content():
    courses_path = os.path.join(DATA_DIR, "courses.json")
    if not os.path.exists(courses_path):
        print(f"Error: courses.json not found at {courses_path}")
        return

    courses = load_json(courses_path)

    report = []

    for course in courses:
        course_id = course.get("id")
        course_name = course.get("name")
        print(f"Analyzing Course: {course_name} ({course_id})")
        report.append(f"# Analysis for Course: {course_name} ({course_id})")

        lessons_file = course.get("lessons_file")
        exercises_file = course.get("exercises_file")

        if not lessons_file or not exercises_file:
            print("  Skipping: Missing lesson or exercise file path.")
            report.append("  - ERROR: Missing file paths configuration.")
            continue

        lessons_path = os.path.join(DATA_DIR, lessons_file)
        exercises_path = os.path.join(DATA_DIR, exercises_file)

        if not os.path.exists(lessons_path):
            print(f"  Error: Lessons file not found: {lessons_path}")
            report.append(f"  - ERROR: Lessons file not found: {lessons_file}")
            continue

        if not os.path.exists(exercises_path):
            print(f"  Error: Exercises file not found: {exercises_path}")
            report.append(f"  - ERROR: Exercises file not found: {exercises_file}")
            continue

        lessons = load_json(lessons_path)
        exercises = load_json(exercises_path)

        lesson_ids = {lesson["id"]: lesson for lesson in lessons}

        exercises_by_lesson = {lid: [] for lid in lesson_ids}
        orphaned_exercises = []

        for ex in exercises:
            lid = ex.get("lesson_id")
            if lid in lesson_ids:
                exercises_by_lesson[lid].append(ex["id"])
            else:
                orphaned_exercises.append(ex["id"])

        # Metrics
        total_lessons = len(lessons)
        total_exercises = len(exercises)
        lessons_with_exercises = sum(1 for lid in exercises_by_lesson if exercises_by_lesson[lid])
        lessons_without_exercises = [lid for lid, exs in exercises_by_lesson.items() if not exs]

        report.append(f"  - Total Lessons: {total_lessons}")
        report.append(f"  - Total Exercises: {total_exercises}")
        report.append(
            f"  - Coverage: {lessons_with_exercises}/{total_lessons} lessons have at least one exercise ({lessons_with_exercises / total_lessons * 100:.1f}%)"
        )

        if orphaned_exercises:
            report.append(f"  - WARNING: {len(orphaned_exercises)} Orphaned Exercises (Invalid lesson_id):")
            for ex_id in orphaned_exercises:
                report.append(f"    - {ex_id}")
        else:
            report.append("  - No orphaned exercises found.")

        if lessons_without_exercises:
            report.append(f"  - GAPS: {len(lessons_without_exercises)} Lessons have NO exercises:")
            for lid in lessons_without_exercises:
                lesson_title = lesson_ids[lid].get("title", "Unknown Title")
                report.append(f"    - [{lid}] {lesson_title}")
        else:
            report.append("  - All lessons have at least one exercise.")

        report.append("")  # Separator

    with open(os.path.join(BASE_DIR, "content_coverage_report.txt"), "w", encoding="utf-8") as f:
        f.write("\n".join(report))

    print(f"Analysis complete. Report saved to {os.path.join(BASE_DIR, 'content_coverage_report.txt')}")


if __name__ == "__main__":
    analyze_course_content()
