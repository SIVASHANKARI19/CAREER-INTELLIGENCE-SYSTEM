import datetime
from typing import Dict, Any

def analyze_linkedin_mock(student_id: int) -> Dict[str, Any]:
    return {
        "student_id": student_id,
        "headline": "Aspiring Full Stack Engineer | CS Senior @ NIT | Open to SDE Roles 2025",
        "summary": "Passionate software engineer skilled in building scalable web apps with React and FastAPI. Proven track record through internships and open-source contributions.",
        "extracted_skills": ["Software Engineering", "Full Stack Development", "Python", "React.js", "RESTful APIs", "Database Design", "Agile Methodologies"],
        "extracted_experience": [
            {
                "title": "Software Engineering Intern",
                "company": "TechNova Solutions",
                "location": "Remote",
                "duration": "May 2024 - Aug 2024",
                "description": "Architected async REST APIs and improved dashboard responsiveness."
            }
        ],
        "extracted_education": [
            {
                "institution": "National Institute of Technology",
                "degree": "Bachelor of Technology - Computer Science & Engineering",
                "period": "2021 - 2025"
            }
        ],
        "extracted_certificates": [
            {
                "name": "AWS Certified Cloud Practitioner",
                "issued_by": "Amazon Web Services",
                "issue_date": "May 2024"
            }
        ],
        "analyzed_at": datetime.datetime.utcnow().isoformat()
    }
