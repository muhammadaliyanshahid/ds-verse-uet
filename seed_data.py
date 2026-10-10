import os
import datetime
from django.utils import timezone
from django.core.files.base import ContentFile

import django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'uet_ds_portal.settings')
django.setup()

from django.contrib.auth.models import User
from apps.accounts.models import StudentProfile
from apps.timetable.models import Semester, Section, TimetableEntry
from apps.papers.models import Course, PastPaper, PaperRating

def create_sample_pdf_content(title_text):
    """Generates a minimal valid PDF binary content with text."""
    pdf_template = (
        "%PDF-1.4\n"
        "1 0 obj << /Type /Catalog /Pages 2 0 R >> endobj\n"
        "2 0 obj << /Type /Pages /Kids [3 0 R] /Count 1 >> endobj\n"
        "3 0 obj << /Type /Page /Parent 2 0 R /Resources << /Font << /F1 4 0 R >> >> /Contents 5 0 R >> endobj\n"
        "4 0 obj << /Type /Font /Subtype /Type1 /BaseFont /Helvetica >> endobj\n"
        "5 0 obj << /Length 120 >> stream\n"
        "BT\n"
        "/F1 18 Tf\n"
        "50 700 Td\n"
        f"({title_text}) Tj\n"
        "ET\n"
        "endstream\n"
        "endobj\n"
        "xref\n"
        "0 6\n"
        "0000000000 65535 f \n"
        "0000000010 00000 n \n"
        "0000000060 00000 n \n"
        "0000000117 00000 n \n"
        "0000000220 00000 n \n"
        "0000000295 00000 n \n"
        "trailer << /Size 6 /Root 1 0 R >>\n"
        "startxref\n"
        "465\n"
        "%%EOF\n"
    )
    return pdf_template.encode('latin-1')

def seed_database():
    print("[*] Starting database seeding for UET Data Science Portal...")

    # 1. Superuser / Admin Account
    admin_user, created = User.objects.get_or_create(
        username='admin',
        defaults={
            'first_name': 'Dr. Aliyan',
            'last_name': 'Shahid',
            'email': 'aliyan.shahid@uet.edu.pk',
            'is_staff': True,
            'is_superuser': True
        }
    )
    if not created:
        admin_user.first_name = 'Dr. Aliyan'
        admin_user.last_name = 'Shahid'
        admin_user.email = 'aliyan.shahid@uet.edu.pk'
        admin_user.save()
    else:
        admin_user.set_password('admin123')
        admin_user.save()
        print("  [+] Superuser created: admin / admin123 (Dr. Aliyan Shahid)")

    # 2. Semesters
    sem_fall24, _ = Semester.objects.get_or_create(
        name='Fall 2024',
        defaults={'start_date': datetime.date(2024, 9, 1), 'end_date': datetime.date(2025, 1, 15), 'is_current': False}
    )
    sem_spring25, _ = Semester.objects.get_or_create(
        name='Spring 2025',
        defaults={'start_date': datetime.date(2025, 2, 1), 'end_date': datetime.date(2025, 6, 15), 'is_current': False}
    )
    sem_fall25, _ = Semester.objects.get_or_create(
        name='Fall 2025',
        defaults={'start_date': datetime.date(2025, 9, 1), 'end_date': datetime.date(2026, 1, 15), 'is_current': True}
    )
    sem_spring26, _ = Semester.objects.get_or_create(
        name='Spring 2026',
        defaults={'start_date': datetime.date(2026, 2, 1), 'end_date': datetime.date(2026, 6, 15), 'is_current': False}
    )
    print("  [+] Semesters created (Fall 2024, Spring 2025, Fall 2025 [Current], Spring 2026)")

    # 3. Sections
    sec_1a, _ = Section.objects.get_or_create(name='DS-1A', semester=sem_fall25, defaults={'batch_year': 2025})
    sec_3a, _ = Section.objects.get_or_create(name='DS-3A', semester=sem_fall25, defaults={'batch_year': 2024})
    sec_5a, _ = Section.objects.get_or_create(name='DS-5A', semester=sem_fall25, defaults={'batch_year': 2023})
    sec_7a, _ = Section.objects.get_or_create(name='DS-7A', semester=sem_fall25, defaults={'batch_year': 2022})
    print("  [+] Sections created (DS-1A, DS-3A, DS-5A, DS-7A)")

    # 4. Student Accounts & Student Profiles
    students_data = [
        {'username': 'student1', 'first_name': 'Ali', 'last_name': 'Raza', 'email': 'ali.raza@student.uet.edu.pk', 'roll': '2023-DS-12', 'sec': sec_5a, 'sem': 5, 'batch': 2023},
        {'username': 'student2', 'first_name': 'Fatima', 'last_name': 'Khan', 'email': 'fatima.k@student.uet.edu.pk', 'roll': '2024-DS-08', 'sec': sec_3a, 'sem': 3, 'batch': 2024},
        {'username': 'student3', 'first_name': 'Usman', 'last_name': 'Ahmad', 'email': 'usman.a@student.uet.edu.pk', 'roll': '2025-DS-01', 'sec': sec_1a, 'sem': 1, 'batch': 2025},
    ]

    for data in students_data:
        u, u_created = User.objects.get_or_create(
            username=data['username'],
            defaults={
                'first_name': data['first_name'],
                'last_name': data['last_name'],
                'email': data['email']
            }
        )
        if u_created:
            u.set_password('pass123')
            u.save()
        
        StudentProfile.objects.update_or_create(
            user=u,
            defaults={
                'roll_number': data['roll'],
                'section': data['sec'],
                'semester_number': data['sem'],
                'batch_year': data['batch'],
                'bio': f"BS Data Science student at UET Lahore (Batch {data['batch']})."
            }
        )
    print("  [+] Student accounts created: student1, student2, student3 (Password: pass123)")

    # 5. Courses
    courses_data = [
        {'code': 'DS-101', 'title': 'Introduction to Data Science', 'credit_hours': 3, 'semester_number': 1},
        {'code': 'CS-201', 'title': 'Data Structures & Algorithms', 'credit_hours': 4, 'semester_number': 2},
        {'code': 'DS-301', 'title': 'Statistical Inference & Probability', 'credit_hours': 3, 'semester_number': 3},
        {'code': 'DS-302', 'title': 'Database Management Systems', 'credit_hours': 4, 'semester_number': 3},
        {'code': 'DS-501', 'title': 'Machine Learning', 'credit_hours': 3, 'semester_number': 5},
        {'code': 'DS-502', 'title': 'Big Data Analytics & Systems', 'credit_hours': 3, 'semester_number': 5},
        {'code': 'DS-701', 'title': 'Deep Learning & Neural Networks', 'credit_hours': 3, 'semester_number': 7},
        {'code': 'DS-702', 'title': 'Natural Language Processing', 'credit_hours': 3, 'semester_number': 7},
    ]

    course_objs = {}
    for cdata in courses_data:
        cobj, _ = Course.objects.get_or_create(
            code=cdata['code'],
            defaults={
                'title': cdata['title'],
                'credit_hours': cdata['credit_hours'],
                'semester_number': cdata['semester_number'],
                'description': f"Official curriculum course for BS Data Science, Semester {cdata['semester_number']}."
            }
        )
        course_objs[cdata['code']] = cobj
    print(f"  [+] {len(course_objs)} Core BS Data Science Courses created")

    # 6. Timetable Entries for Section DS-5A and DS-3A
    timetable_data = [
        # Section DS-5A
        {'sec': sec_5a, 'course': course_objs['DS-501'], 'day': 'MON', 'start': datetime.time(8, 30), 'end': datetime.time(10, 0), 'room': 'Lab 03', 'instructor': 'Dr. Asim Farooq'},
        {'sec': sec_5a, 'course': course_objs['DS-502'], 'day': 'MON', 'start': datetime.time(10, 0), 'end': datetime.time(11, 30), 'room': 'Lecture Hall 204', 'instructor': 'Prof. Shahid Awan'},
        {'sec': sec_5a, 'course': course_objs['DS-501'], 'day': 'WED', 'start': datetime.time(11, 30), 'end': datetime.time(1, 0), 'room': 'Lab 03', 'instructor': 'Dr. Asim Farooq'},
        {'sec': sec_5a, 'course': course_objs['DS-502'], 'day': 'THU', 'start': datetime.time(8, 30), 'end': datetime.time(10, 0), 'room': 'Lab 01', 'instructor': 'Prof. Shahid Awan'},
        {'sec': sec_5a, 'course': course_objs['DS-302'], 'day': 'FRI', 'start': datetime.time(9, 0), 'end': datetime.time(11, 0), 'room': 'Hall 102', 'instructor': 'Dr. Rabia Noor'},

        # Section DS-3A
        {'sec': sec_3a, 'course': course_objs['DS-301'], 'day': 'MON', 'start': datetime.time(11, 30), 'end': datetime.time(1, 0), 'room': 'Hall 102', 'instructor': 'Prof. Tariq Mahmood'},
        {'sec': sec_3a, 'course': course_objs['DS-302'], 'day': 'TUE', 'start': datetime.time(8, 30), 'end': datetime.time(10, 0), 'room': 'Lab 02', 'instructor': 'Dr. Rabia Noor'},
        {'sec': sec_3a, 'course': course_objs['CS-201'], 'day': 'WED', 'start': datetime.time(8, 30), 'end': datetime.time(10, 0), 'room': 'Lab 01', 'instructor': 'Dr. Usman Ghani'},
        {'sec': sec_3a, 'course': course_objs['DS-301'], 'day': 'THU', 'start': datetime.time(10, 0), 'end': datetime.time(11, 30), 'room': 'Lecture Hall 204', 'instructor': 'Prof. Tariq Mahmood'},
    ]

    for tdata in timetable_data:
        TimetableEntry.objects.get_or_create(
            section=tdata['sec'],
            course=tdata['course'],
            day_of_week=tdata['day'],
            start_time=tdata['start'],
            defaults={
                'end_time': tdata['end'],
                'room': tdata['room'],
                'instructor_name': tdata['instructor']
            }
        )
    print("  [+] Timetable Schedule entries populated across sections")

    # 7. Past Papers (Approved & Pending)
    papers_data = [
        # Approved Papers
        {'course': course_objs['DS-501'], 'sem': sem_fall24, 'uploader': admin_user, 'type': 'mid', 'year': 2024, 'approved': True, 'downloads': 42},
        {'course': course_objs['DS-501'], 'sem': sem_spring25, 'uploader': User.objects.get(username='student1'), 'type': 'final', 'year': 2025, 'approved': True, 'downloads': 85},
        {'course': course_objs['DS-502'], 'sem': sem_fall24, 'uploader': User.objects.get(username='student1'), 'type': 'mid', 'year': 2024, 'approved': True, 'downloads': 29},
        {'course': course_objs['DS-301'], 'sem': sem_spring25, 'uploader': User.objects.get(username='student2'), 'type': 'final', 'year': 2025, 'approved': True, 'downloads': 64},
        {'course': course_objs['DS-302'], 'sem': sem_fall24, 'uploader': User.objects.get(username='student2'), 'type': 'mid', 'year': 2024, 'approved': True, 'downloads': 38},
        {'course': course_objs['DS-101'], 'sem': sem_fall24, 'uploader': User.objects.get(username='student3'), 'type': 'final', 'year': 2024, 'approved': True, 'downloads': 110},

        # Pending Approval Papers (For Testing Approval Queue!)
        {'course': course_objs['DS-701'], 'sem': sem_spring25, 'uploader': User.objects.get(username='student1'), 'type': 'mid', 'year': 2025, 'approved': False, 'downloads': 0},
        {'course': course_objs['DS-702'], 'sem': sem_spring25, 'uploader': User.objects.get(username='student2'), 'type': 'final', 'year': 2025, 'approved': False, 'downloads': 0},
    ]

    for pdata in papers_data:
        title = f"UET Lahore {pdata['course'].code} {pdata['type'].upper()} Paper ({pdata['year']})"
        pdf_bytes = create_sample_pdf_content(title)
        file_name = f"{pdata['course'].code}_{pdata['type']}_{pdata['year']}.pdf"

        paper, p_created = PastPaper.objects.get_or_create(
            course=pdata['course'],
            semester=pdata['sem'],
            exam_type=pdata['type'],
            year=pdata['year'],
            defaults={
                'uploader': pdata['uploader'],
                'is_approved': pdata['approved'],
                'approved_by': admin_user if pdata['approved'] else None,
                'approved_at': timezone.now() if pdata['approved'] else None,
                'download_count': pdata['downloads']
            }
        )
        if p_created:
            paper.file.save(file_name, ContentFile(pdf_bytes), save=True)

    print("  [+] Past Papers created (6 Approved, 2 Pending in Approval Queue)")

    # 8. Sample Paper Upvotes
    approved_papers = PastPaper.objects.filter(is_approved=True)
    all_users = User.objects.all()
    for paper in approved_papers[:4]:
        for u in all_users:
            PaperRating.objects.get_or_create(paper=paper, student=u)

    print("  [+] Sample Paper ratings and upvotes initialized")
    print("==> Database Seeding Completed Successfully!")

if __name__ == '__main__':
    seed_database()
