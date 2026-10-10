# UET Lahore - Institute of Data Science Portal

A production-grade, full-stack server-rendered web portal for the Institute of Data Science at **University of Engineering and Technology (UET) Lahore**. Built using **Python, Django, Bootstrap 5**, and **SQLite (Postgres-ready schema)**.

---

## 🌟 Key Features

1. **Role-Aware Navigation & Custom Authentication**:
   - Extended Django user model (`StudentProfile`) linking student Roll Numbers (e.g. `2023-DS-15`), Section assignments (`DS-1A` to `DS-7A`), Batch Years, and Semester numbers.
   - Support for **Student/Alumni Senior Mentors** (account creations are held in a pending queue for admin approval).
   - **Student Administrator Privilege**: Dedicated administrative controls allowing student admins and faculty to oversee approval queues and manage section schedules seamlessly.

2. **Past Papers Library (No Login Required to Upload/Download)**:
   - Filterable and searchable past examination paper database (Filter by Course, Exam Type, Semester, or Keywords).
   - **Guest Submissions**: Anyone can upload past midterm & final exam papers without logging in.
   - Past Paper Uploads with strict client & server-side **PDF validation** (enforces `.pdf` format & max 10MB size limit).
   - **Approval Queue**: Submissions automatically enter a pending approval queue for review before appearing in the public repository.
   - One-vote per student **Upvoting System** (requires login) and total download counters.

3. **Weekly Section Timetables**:
   - Interactive weekly timetable view auto-selecting the student's assigned section.
   - Section switcher enabling browsing for all department sections (DS-1A to DS-7A).
   - Clean weekly card grid showing class times, designated lecture halls/labs, and instructor names.

4. **UET GPA & CGPA Calculator**:
   - **Semester GPA (SGPA) Calculator**: Interactive tool featuring dynamic course row addition/removal, preset credit hours, and UET grade dropdown selections.
   - **Cumulative GPA (CGPA) Calculator**: Computes overall GPA by combining current semester results with prior completed credit hours and CGPA.
   - **UET Grading Scale Reference**: Includes a sidebar scale detailing UET grade values (A+ = 4.00, A = 4.00, A- = 3.70, B+ = 3.30, etc.) and marks range.

5. **Senior Mentors & Guidance Hub**:
   - **Senior Registration**: Seniors/alumni can register as mentors. Accounts are created in a pending state (`is_approved=False`) requiring admin activation.
   - **Advice Feed**: Verified guidance posts written by approved seniors concerning Career advice, Course tips, FYPs, and Internships. All guidance posts require admin approval before being shown.
   - **Reach Out / Queries**: Guest or logged-in users can submit queries/questions to all mentors or target a specific mentor from the directory.
   - **Mentor Portal**: A dedicated mentor dashboard where approved seniors can view queries, post replies, and check their posts.

6. **Customized Django Admin Site**:
   - Customized department administration styling (`UET Data Science Department Portal`).
   - One-click bulk action approvals and rejections (`approve_selected_papers` & `reject_selected_papers`).
   - Timetable entry, section, and mentor profile management.

7. **Custom Error Pages & Design System**:
   - Academic Navy (`#0F172A`), Teal (`#0D9488`), and Amber theme palette with glassmorphism cards and smooth interactions.
   - Custom styled 404 Page Not Found and 500 Server Error pages matching the department theme.

---

## 🛠️ Technology Stack

- **Backend**: Python 3.12, Django 5.x
- **Database**: SQLite (configured for local dev with Postgres-compatible models)
- **Frontend**: Django Templates + Bootstrap 5 + FontAwesome 6 + Custom CSS & JS
- **Storage**: Django FileStorage for PDF documents (`media/past_papers/`)

---

## 🚀 Quickstart & Installation Instructions

### 1. Prerequisites
Ensure you have Python 3.10+ installed on your environment.

### 2. Clone / Open Directory & Setup Virtual Environment
```bash
# Navigate to project root directory
cd "d:\ds verse uet"

# Create a virtual environment
python -m venv .venv

# Activate virtual environment
# On Windows PowerShell:
.venv\Scripts\Activate.ps1
# On Linux/macOS:
source .venv/bin/activate
```

### 3. Install Dependencies
```bash
pip install -r requirements.txt
```

### 4. Run Migrations & Populate Seed Data
```bash
# Apply database migrations
python manage.py migrate

# Seed database with realistic UET DS courses, sections, timetables, accounts, and sample PDF past papers
python seed_data.py
```

### 5. Launch Local Development Server
```bash
python manage.py runserver
```

Open your browser and navigate to: **`http://127.0.0.1:8000/`**

---

## 🔑 Pre-seeded Accounts & Credentials

| Role | Username | Password | Details |
|---|---|---|---|
| **Department Admin / Faculty** | `admin` | `admin123` | Full Django Admin & Approval Queue Access (Dr. Aliyan Shahid) |
| **Student (Semester 5)** | `student1` | `pass123` | Roll #: `2023-DS-12`, Section: `DS-5A` |
| **Student (Semester 3)** | `student2` | `pass123` | Roll #: `2024-DS-08`, Section: `DS-3A` |
| **Student (Semester 1)** | `student3` | `pass123` | Roll #: `2025-DS-01`, Section: `DS-1A` |

---

## 🧪 Running Automated Tests

Execute the unit test suite covering uploads, PDF validation, user registration, upvoting, GPA calculator loading, query submissions, and administrative approval permissions:

```bash
python manage.py test
```

---

## 📁 Directory Architecture

```
d:/ds verse uet/
├── apps/
│   ├── accounts/          # User authentication & StudentProfile models/views
│   ├── papers/            # Course, PastPaper, PaperRating models, library & GPA calculator
│   ├── seniors/           # SeniorPost & SeniorQuery models, guidance hub & mentor dashboard
│   └── timetable/         # Semester, Section, TimetableEntry models & weekly grid
├── media/
│   └── past_papers/       # PDF storage directory
├── static/
│   ├── css/custom.css     # Department Navy & Teal design system
│   ├── js/main.js         # Interactive JS & AJAX upvoting
│   └── img/               # Brand logo (uet_ds_logo.png) & favicons (favicon.ico/png)
├── templates/             # HTML templates (landing, dashboard, papers, seniors, gpa, 404, 500)
├── uet_ds_portal/         # Settings & root URL configuration
├── manage.py
├── seed_data.py           # Automated database populator
├── requirements.txt
└── README.md
```
