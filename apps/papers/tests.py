import os
import datetime
from django.test import TestCase, Client
from django.urls import reverse
from django.contrib.auth.models import User
from django.core.files.uploadedfile import SimpleUploadedFile

from apps.papers.models import Course, PastPaper, PaperRating
from apps.timetable.models import Semester, Section, TimetableEntry
from apps.accounts.models import StudentProfile

class UETPortalTestCase(TestCase):
    def setUp(self):
        self.client = Client()
        
        # Create Semester
        self.semester = Semester.objects.create(
            name="Fall 2025 Test",
            start_date=datetime.date(2025, 9, 1),
            end_date=datetime.date(2026, 1, 15),
            is_current=True
        )
        
        # Create Section
        self.section = Section.objects.create(
            name="DS-5A",
            semester=self.semester,
            batch_year=2023
        )

        # Create Course
        self.course = Course.objects.create(
            code="DS-501",
            title="Machine Learning",
            credit_hours=3,
            semester_number=5
        )

        # Create Admin user
        self.admin_user = User.objects.create_superuser(
            username="admin_test",
            email="admin@uet.edu.pk",
            password="password123"
        )

        # Create Student user
        self.student_user = User.objects.create_user(
            username="student_test",
            email="student@uet.edu.pk",
            password="password123",
            first_name="Ali",
            last_name="Raza"
        )
        self.profile = StudentProfile.objects.create(
            user=self.student_user,
            roll_number="2023-DS-99",
            section=self.section,
            semester_number=5,
            batch_year=2023
        )

        # Create Sample PDF
        pdf_content = b"%PDF-1.4 test document content"
        self.pdf_file = SimpleUploadedFile("test_paper.pdf", pdf_content, content_type="application/pdf")
        self.txt_file = SimpleUploadedFile("test_paper.txt", b"plain text content", content_type="text/plain")

    def test_landing_page_status(self):
        response = self.client.get(reverse('papers:landing'))
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, "UET Department of")

    def test_pdf_upload_validation(self):
        self.client.login(username="student_test", password="password123")
        
        # Test valid PDF upload
        response = self.client.post(reverse('papers:paper_upload'), {
            'course': self.course.id,
            'semester': self.semester.id,
            'exam_type': 'mid',
            'year': 2025,
            'file': self.pdf_file
        })
        self.assertEqual(response.status_code, 302)
        
        # Check paper created with pending status
        paper = PastPaper.objects.get(course=self.course)
        self.assertFalse(paper.is_approved)
        self.assertEqual(paper.uploader, self.student_user)

    def test_non_pdf_rejection(self):
        self.client.login(username="student_test", password="password123")
        response = self.client.post(reverse('papers:paper_upload'), {
            'course': self.course.id,
            'semester': self.semester.id,
            'exam_type': 'mid',
            'year': 2025,
            'file': self.txt_file
        })
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, "Invalid file format")

    def test_paper_approval_and_upvoting(self):
        # Create unapproved paper
        paper = PastPaper.objects.create(
            course=self.course,
            semester=self.semester,
            uploader=self.student_user,
            exam_type="mid",
            year=2025,
            file=self.pdf_file,
            is_approved=False
        )

        # Admin approves paper
        self.client.login(username="admin_test", password="password123")
        approve_url = reverse('papers:process_paper', kwargs={'pk': paper.pk, 'action': 'approve'})
        response = self.client.post(approve_url)
        self.assertEqual(response.status_code, 302)

        paper.refresh_from_db()
        self.assertTrue(paper.is_approved)

        # Student upvotes paper
        self.client.login(username="student_test", password="password123")
        upvote_url = reverse('papers:paper_upvote', kwargs={'pk': paper.pk})
        self.client.post(upvote_url)

        self.assertEqual(paper.upvotes_count(), 1)

    def test_gpa_calculator_renders(self):
        response = self.client.get(reverse('papers:gpa_calculator'))
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, "GPA & CGPA Calculator")

    def test_senior_mentor_signup_and_approval(self):
        # 1. Senior signs up (mentor registration)
        response = self.client.post(reverse('seniors:signup'), {
            'username': 'senior_mentor_test',
            'first_name': 'Hassan',
            'last_name': 'Tariq',
            'email': 'hassan@uet.edu.pk',
            'password': 'password123',
            'confirm_password': 'password123',
            'roll_number': '2021-DS-99',
            'batch_year': 2021,
            'expertise': 'Computer Vision, ML',
            'linkedin_url': 'https://linkedin.com/in/hassan',
            'bio': 'Senior BS DS student at UET.'
        })
        self.assertEqual(response.status_code, 302) # redirects to seniors:hub

        # Verify database record exists with is_approved=False
        user = User.objects.get(username='senior_mentor_test')
        profile = user.profile
        self.assertEqual(profile.role, 'senior')
        self.assertFalse(profile.is_approved)

        # 2. Admin approves the senior mentor account
        self.client.login(username="admin_test", password="password123")
        approve_url = reverse('seniors:process_approval', kwargs={'target_type': 'mentor', 'pk': profile.pk, 'action': 'approve'})
        response = self.client.post(approve_url)
        self.assertEqual(response.status_code, 302)

        profile.refresh_from_db()
        self.assertTrue(profile.is_approved)

    def test_guest_query_submission(self):
        # Guest user (not logged in) sends query
        response = self.client.post(reverse('seniors:submit_query'), {
            'sender_name': 'Anonymous Student',
            'sender_email': 'guest@student.uet.edu.pk',
            'subject': 'Help regarding database query optimization',
            'message': 'Can anyone explain how to write optimized SQL joins?'
        })
        self.assertEqual(response.status_code, 302)

        from apps.seniors.models import SeniorQuery
        query = SeniorQuery.objects.get(subject='Help regarding database query optimization')
        self.assertEqual(query.sender_name, 'Anonymous Student')
        self.assertIsNone(query.sender_user)
        self.assertFalse(query.is_answered)

