# AI-Powered Resume Screening System

## Project Overview

The AI-Powered Resume Screening System is a web application that helps recruiters manage job applications and find the most suitable candidates for job openings. It reduces manual work by automatically analyzing resumes, calculating an ATS score, and recommending candidates based on their skills and experience.

Candidates can register, upload their resumes, apply for jobs, and track their application status. Admins can create job postings, manage candidates, search resumes by skills, and make hiring decisions.

---

# Features

## Candidate

* Register and Login
* Update Profile
* Upload Resume (PDF)
* View Available Jobs
* Apply for Jobs
* Track Application Status
* View ATS Score
* Get Recommended Jobs

### Candidate Dashboard

* Available Jobs
* Applied Jobs
* Shortlisted Jobs
* Selected Jobs
* Rejected Jobs

---

## Admin

* Login
* View Candidate List
* Add, Edit, and Delete Job Postings
* Search Candidates by Skills
* View ATS Scores
* Shortlist Candidates
* Recruit Candidates
* Reject Candidates
* View Candidate Resume Details

---

## Resume Parsing

The system uses **pdfplumber** to read uploaded PDF resumes and extract information such as:

* Name
* Email
* Phone Number
* Skills
* Education
* Experience
* Projects
* Certifications

---

## ATS Score

After a resume is uploaded, the system calculates an ATS (Applicant Tracking System) score based on:

* Matching Skills
* Experience
* Education
* Projects
* Certifications

The score helps recruiters identify the best candidates for a job.

---

## Smart Job Recommendation

The system compares the candidate's skills with all available jobs.

For example:

If a candidate applies for a **Java Developer** job but also has skills like **JavaScript**, **React**, and **Node.js**, the system will also recommend:

* JavaScript Developer
* React Developer
* Full Stack Developer
* Node.js Developer

This increases the candidate's chances of getting shortlisted for other matching jobs.

---

# Technology Used

## Frontend

* HTML
* CSS
* Bootstrap
* JavaScript

## Backend

* Python
* FastAPI

## Resume Parser

* pdfplumber

## Database

* MySQL (Stores users, jobs, and applications)
* MongoDB (Stores resume data, extracted skills, and ATS information)

---

# Project Structure

```text
ATS-System/
│
├── backend/
├── frontend/
├── uploads/
├── database/
└── README.md
```

---

# How to Run the Project

### 1. Clone the Repository

```bash
git clone <repository-url>
cd ats-system
```

### 2. Create Virtual Environment

```bash
python -m venv .venv
```

Activate it:

Windows

```bash
.venv\Scripts\activate
```

### 3. Install Required Packages

```bash
pip install -r backend/requirements.txt
```

### 4. Configure the Database

Update the database details in the `.env` file or configuration file with your MySQL and MongoDB credentials.

### 5. Start the Backend

```bash
cd backend
uvicorn app.main:app --reload
```

Open:

```
http://127.0.0.1:8000/docs
```

to view the API documentation.

### 6. Start the Frontend

```bash
cd frontend
python -m http.server 5500
```

Open:

```
http://127.0.0.1:5500
```

---

# Future Improvements

* Email Notifications
* Interview Scheduling
* Resume Comparison
* Skill Gap Analysis
* AI Interview Questions
* Analytics Dashboard
* Resume Version History

---

# Conclusion

This project demonstrates how Artificial Intelligence can simplify the recruitment process by automatically screening resumes, calculating ATS scores, and recommending suitable candidates for different job openings. It provides an easy-to-use platform for both recruiters and candidates while making the hiring process faster and more efficient.

---

