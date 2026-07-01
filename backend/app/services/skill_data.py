"""
Master skill vocabulary + synonym normalization used by both the resume
parser and the recommendation engine, so "JS" on a resume and "JavaScript"
on a job posting are recognized as the same skill.

This is intentionally a curated dictionary rather than an ML/embedding
model (no semantic similarity service) — appropriate scope for a 3-4 week
intern build. docs/ARCHITECTURE.md explains how this could later be swapped
for an embedding-based matcher without changing the API surface.
"""

# Canonical skill -> list of synonyms / common variants that should map to it.
SKILL_SYNONYMS = {
    "JavaScript": ["js", "javascript", "java script"],
    "TypeScript": ["ts", "typescript"],
    "Python": ["python", "py"],
    "Java": ["java"],
    "C++": ["c++", "cpp", "c plus plus"],
    "C#": ["c#", "c sharp", "csharp"],
    "C": ["c programming", " c "],
    "PHP": ["php"],
    "Ruby": ["ruby"],
    "Go": ["golang", "go lang"],
    "Rust": ["rust"],
    "React": ["react", "reactjs", "react.js"],
    "Angular": ["angular", "angularjs"],
    "Vue": ["vue", "vuejs", "vue.js"],
    "Node.js": ["node", "nodejs", "node.js"],
    "Express.js": ["express", "expressjs", "express.js"],
    "Django": ["django"],
    "Flask": ["flask"],
    "FastAPI": ["fastapi", "fast api"],
    "Spring Boot": ["spring boot", "springboot", "spring"],
    "HTML": ["html", "html5"],
    "CSS": ["css", "css3"],
    "Bootstrap": ["bootstrap"],
    "Tailwind CSS": ["tailwind", "tailwindcss"],
    "jQuery": ["jquery"],
    "SQL": ["sql"],
    "MySQL": ["mysql"],
    "PostgreSQL": ["postgresql", "postgres"],
    "MongoDB": ["mongodb", "mongo"],
    "SQLite": ["sqlite"],
    "Redis": ["redis"],
    "AWS": ["aws", "amazon web services"],
    "Azure": ["azure", "microsoft azure"],
    "GCP": ["gcp", "google cloud", "google cloud platform"],
    "Docker": ["docker", "containerization"],
    "Kubernetes": ["kubernetes", "k8s"],
    "Git": ["git"],
    "GitHub": ["github"],
    "GitLab": ["gitlab"],
    "Linux": ["linux", "unix"],
    "REST API": ["rest api", "restful api", "rest", "restful"],
    "GraphQL": ["graphql"],
    "Machine Learning": ["machine learning", "ml"],
    "Deep Learning": ["deep learning", "dl"],
    "Natural Language Processing": ["nlp", "natural language processing"],
    "TensorFlow": ["tensorflow"],
    "PyTorch": ["pytorch"],
    "Pandas": ["pandas"],
    "NumPy": ["numpy"],
    "Scikit-learn": ["scikit-learn", "sklearn"],
    "Data Analysis": ["data analysis", "data analytics"],
    "Power BI": ["power bi", "powerbi"],
    "Tableau": ["tableau"],
    "Excel": ["excel", "ms excel", "microsoft excel"],
    "Selenium": ["selenium"],
    "JUnit": ["junit"],
    "Pytest": ["pytest"],
    "CI/CD": ["ci/cd", "cicd", "continuous integration", "continuous deployment"],
    "Jenkins": ["jenkins"],
    "Agile": ["agile", "scrum"],
    "JIRA": ["jira"],
    "Figma": ["figma"],
    "Android": ["android"],
    "iOS": ["ios"],
    "Swift": ["swift"],
    "Kotlin": ["kotlin"],
    "Flutter": ["flutter"],
    "React Native": ["react native"],
    ".NET": [".net", "dotnet", "asp.net"],
    "Cybersecurity": ["cybersecurity", "cyber security", "infosec"],
    "Networking": ["networking", "computer networks"],
    "Communication": ["communication", "communication skills"],
    "Leadership": ["leadership"],
    "Teamwork": ["teamwork", "team player", "collaboration"],
    "Problem Solving": ["problem solving", "problem-solving"],
    "Time Management": ["time management"],
}

# Flat reverse lookup: variant text -> canonical skill name
_VARIANT_TO_CANONICAL = {}
for canonical, variants in SKILL_SYNONYMS.items():
    for variant in variants:
        _VARIANT_TO_CANONICAL[variant.strip().lower()] = canonical

# Master set used by the resume parser to scan free text for known skills
MASTER_SKILLS = list(SKILL_SYNONYMS.keys())

SOFT_SKILLS = {
    "Communication", "Leadership", "Teamwork", "Problem Solving", "Time Management"
}


def normalize_skill(raw: str) -> str:
    """Map a raw skill string (any casing/variant) to its canonical name."""
    cleaned = raw.strip().lower()
    return _VARIANT_TO_CANONICAL.get(cleaned, raw.strip())


def normalize_skill_list(raw_list: list[str]) -> list[str]:
    """Normalize + de-duplicate a list of raw skill strings, preserving order."""
    seen = set()
    result = []
    for item in raw_list:
        if not item or not item.strip():
            continue
        normalized = normalize_skill(item)
        key = normalized.lower()
        if key not in seen:
            seen.add(key)
            result.append(normalized)
    return result
