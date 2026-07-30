import datetime
from typing import Dict, Any

def generate_roadmap_mock(student_id: int) -> Dict[str, Any]:
    return {
        "student_id": student_id,
        "weekly_plan": [
            {
                "week": 1,
                "focus": "System Design Foundations & Scalability",
                "tasks": [
                    "Study load balancers, database sharding, and caching strategies.",
                    "Design a rate limiter microservice in FastAPI.",
                    "Solve 5 LeetCode Medium System Design questions."
                ]
            },
            {
                "week": 2,
                "focus": "Containerization with Docker & Multi-stage Builds",
                "tasks": [
                    "Dockerize React frontend and FastAPI backend with Docker Compose.",
                    "Configure environment variables and volume persistence.",
                    "Push container images to Docker Hub."
                ]
            },
            {
                "week": 3,
                "focus": "Performance Optimization & Redis Integration",
                "tasks": [
                    "Add Redis cache layer to backend API responses.",
                    "Implement refresh token invalidation via Redis store.",
                    "Benchmark API response latency before and after caching."
                ]
            },
            {
                "week": 4,
                "focus": "CI/CD & Cloud Deployment (AWS/Vercel)",
                "tasks": [
                    "Write GitHub Actions workflow for automated testing & linting.",
                    "Deploy frontend to Vercel/Netlify with live backend API endpoints.",
                    "Conduct mock technical interview practice."
                ]
            }
        ],
        "monthly_plan": [
            {"month": 1, "goal": "Master System Architecture & Containerization"},
            {"month": 2, "goal": "Build Enterprise Capstone Project & Cloud Deployment"},
            {"month": 3, "goal": "Intensive Interview Prep (DSA + Behavioral + System Design)"}
        ],
        "recommended_projects": [
            {
                "title": "Real-time Collaborative Code Editor",
                "tech_stack": ["WebSockets", "React", "Node.js/FastAPI", "Redis"],
                "difficulty": "Advanced",
                "impact": "High - Demonstrates real-time state synchronization & WebSockets."
            },
            {
                "title": "Cloud Resume & Portfolio Tracker with Analytics",
                "tech_stack": ["React", "FastAPI", "PostgreSQL", "AWS S3"],
                "difficulty": "Intermediate",
                "impact": "Medium - Proves cloud storage & auth workflow skills."
            }
        ],
        "recommended_courses": [
            {"name": "Grokking the System Design Interview", "platform": "DesignGurus", "link": "https://designgurus.org"},
            {"name": "Docker & Kubernetes: The Practical Guide", "platform": "Udemy", "link": "https://udemy.com"},
            {"name": "FastAPI Masterclass - Modern Python Web APIs", "platform": "Coursera", "link": "https://coursera.org"}
        ],
        "interview_questions": [
            {
                "question": "How would you handle high database write traffic without slowing down user responses?",
                "topic": "System Design",
                "suggested_answer": "Use an asynchronous message queue (e.g. RabbitMQ/Kafka) to decouple client write requests from background DB persistence workers."
            },
            {
                "question": "Explain the difference between SQL indexing and database partitioning.",
                "topic": "Databases",
                "suggested_answer": "Indexing speeds up row lookups via B-Tree/Hash data structures; partitioning splits huge tables into separate logical files based on key ranges."
            }
        ],
        "resources": [
            {"title": "System Design Primer GitHub Repo", "type": "Repository", "link": "https://github.com/donnemartin/system-design-primer"},
            {"title": "FastAPI Official Documentation", "type": "Docs", "link": "https://fastapi.tiangolo.com"}
        ],
        "generated_at": datetime.datetime.utcnow().isoformat()
    }
