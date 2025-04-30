import spacy
import nltk
from transformers import pipeline
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.metrics.pairwise import cosine_similarity
import PyPDF2
from docx import Document
import re
from difflib import SequenceMatcher

class ResumeMatcher:
    def __init__(self):
        self.nlp = spacy.load('en_core_web_md')
        nltk.download('punkt')
        nltk.download('stopwords')
        self.stop_words = set(nltk.corpus.stopwords.words('english'))
        self.classifier = pipeline("zero-shot-classification")
        self.vectorizer = TfidfVectorizer(stop_words='english')
        
        self.skill_patterns = {
            'programming': [
                r'python|django|flask|fastapi',
                r'java(?:script)?|typescript|node\.?js|express\.?js|react\.?js|vue\.?js|angular',
                r'c\+\+|c#|\.net|asp\.net',
                r'sql|mysql|postgresql|mongodb|oracle|sqlite',
                r'html5?|css3?|sass|less|bootstrap',
                r'docker|kubernetes|aws|azure|gcp|cloud',
                r'git|github|bitbucket|svn'
            ],
            'data_science': [
                r'machine[\s-]?learning|deep[\s-]?learning|neural[\s-]?networks?',
                r'tensorflow|pytorch|keras|scikit[\s-]?learn',
                r'data[\s-]?science|data[\s-]?analytics|big[\s-]?data',
                r'ai|artificial[\s-]?intelligence|nlp|natural[\s-]?language[\s-]?processing'
            ],
            'soft_skills': [
                r'project[\s-]?management|agile|scrum|kanban',
                r'leadership|team[\s-]?management|mentoring',
                r'communication|collaboration|problem[\s-]?solving'
            ]
        }

    def parse_resume(self, file_path):
        """Extract text from PDF or DOCX resume"""
        text = ""
        try:
            if file_path.lower().endswith('.pdf'):
                with open(file_path, 'rb') as file:
                    reader = PyPDF2.PdfReader(file)
                    for page in reader.pages:
                        text += page.extract_text()
            elif file_path.lower().endswith('.docx'):
                doc = Document(file_path)
                for para in doc.paragraphs:
                    text += para.text + "\n"
            return text.strip()
        except Exception as e:
            print(f"Error parsing file: {str(e)}")
            return ""

    def normalize_skill(self, skill):
        """Normalize skill names to handle variations"""
        skill = skill.lower().strip()
        replacements = {
            'javascript': 'js',
            'typescript': 'ts',
            'react.js': 'react',
            'node.js': 'node',
            'vue.js': 'vue',
            'express.js': 'express'
        }
        return replacements.get(skill, skill)

    def extract_skills(self, text):
        """Extract skills from text using improved pattern matching and NER"""
        text = text.lower()
        skills = set()
        
        for category, patterns in self.skill_patterns.items():
            for pattern in patterns:
                matches = re.finditer(pattern, text, re.IGNORECASE)
                for match in matches:
                    skill = self.normalize_skill(match.group())
                    skills.add(skill)
        
        doc = self.nlp(text)
        for ent in doc.ents:
            if ent.label_ in ['PRODUCT', 'ORG'] and len(ent.text) > 2:
                skill = self.normalize_skill(ent.text)
                skills.add(skill)
        
        return list(skills)

    def calculate_skill_similarity(self, skill1, skill2):
        """Calculate similarity between two skills using sequence matcher"""
        return SequenceMatcher(None, skill1.lower(), skill2.lower()).ratio()

    def find_matching_skills(self, resume_skills, job_skills, threshold=0.85):
        """Find matching skills with fuzzy matching"""
        matched = set()
        for job_skill in job_skills:
            for resume_skill in resume_skills:
                if self.calculate_skill_similarity(job_skill, resume_skill) >= threshold:
                    matched.add(job_skill)
                    break
        return matched

    def extract_experience(self, text):
        """Extract years of experience and relevant positions with improved accuracy"""
        experience = {
            'years': 0,
            'positions': []
        }
        
        year_patterns = [
            r'(\d+)[\+]?\s+years?(?:\s+of)?\s+experience',
            r'(?:work|professional|industry)\s+experience\s*(?:of|for)?\s*(\d+)[\+]?\s+years?',
            r'(\d+)[\+]?\s+years?(?:\s+of)?\s+(?:work|professional|industry)\s+experience'
        ]
        
        years = []
        for pattern in year_patterns:
            matches = re.findall(pattern, text, re.IGNORECASE)
            years.extend([int(y) for y in matches])
        
        if years:
            experience['years'] = max(years)
        
        job_titles = self.classifier(
            text,
            candidate_labels=[
                "software engineer", "senior software engineer", "full stack developer",
                "data scientist", "machine learning engineer", "data engineer",
                "project manager", "product manager", "technical lead",
                "frontend developer", "backend developer", "devops engineer"
            ]
        )
        experience['positions'] = [
            title for title, score in zip(job_titles['labels'], job_titles['scores'])
            if score > 0.3 
        ][:3]  
        
        return experience

    def calculate_match(self, resume_text, job_description):
        """Calculate matching score between resume and job description with improved accuracy"""
        resume_skills = self.extract_skills(resume_text)
        job_skills = self.extract_skills(job_description)
        
        matched_skills = self.find_matching_skills(resume_skills, job_skills)
        
        if job_skills:
            skill_match = len(matched_skills) / len(set(job_skills))
        else:
            skill_match = 0
            
        text_vectors = self.vectorizer.fit_transform([resume_text, job_description])
        similarity = cosine_similarity(text_vectors[0:1], text_vectors[1:2])[0][0]
        
        experience_info = self.extract_experience(resume_text)
        
        exp_years = min(experience_info['years'], 10) / 10  
        
        final_score = (0.5 * skill_match + 0.3 * similarity + 0.2 * exp_years) * 100
        
        return {
            'score': round(final_score, 2),
            'matched_skills': list(matched_skills),
            'missing_skills': list(set(job_skills) - matched_skills),
            'experience': experience_info,
            'skill_match_percentage': round(skill_match * 100, 2),
            'text_similarity_percentage': round(similarity * 100, 2),
            'experience_score': round(exp_years * 100, 2)
        }
