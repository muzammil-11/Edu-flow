"""
FAISS Vector Store for program-applicant matching.
Uses TF-IDF embeddings to match applicant profiles against program descriptions.
"""
import faiss
import numpy as np
from sklearn.feature_extraction.text import TfidfVectorizer
import os

# Program descriptions with requirements and keywords
PROGRAM_DATA = {
    "Computer Science": {
        "description": "Computer Science program focusing on software engineering, algorithms, data structures, artificial intelligence, machine learning, cybersecurity, and computer systems. Strong analytical and mathematical skills required.",
        "min_gpa": 3.0,
        "preferred_gpa": 3.5,
        "keywords": "programming coding software algorithms data AI machine learning technology innovation research math analytical problem-solving",
        "preferred_tests": ["SAT", "GRE"],
        "min_test_score": 1300,
    },
    "Engineering": {
        "description": "Engineering program covering mechanical, electrical, civil, and systems engineering. Emphasis on design, physics, mathematics, and hands-on problem solving.",
        "min_gpa": 3.0,
        "preferred_gpa": 3.5,
        "keywords": "engineering design physics mathematics systems mechanical electrical civil innovation build problem-solving hands-on technical",
        "preferred_tests": ["SAT", "GRE"],
        "min_test_score": 1300,
    },
    "Business Administration": {
        "description": "Business Administration program with focus on management, finance, marketing, entrepreneurship, leadership, and organizational behavior.",
        "min_gpa": 2.8,
        "preferred_gpa": 3.3,
        "keywords": "business management finance marketing leadership entrepreneurship strategy organization commerce economics team communication",
        "preferred_tests": ["GMAT", "GRE", "SAT"],
        "min_test_score": 600,
    },
    "Medicine": {
        "description": "Medical program covering anatomy, physiology, biochemistry, clinical practice, patient care, diagnostics, and research methodologies. Rigorous academic standards.",
        "min_gpa": 3.5,
        "preferred_gpa": 3.8,
        "keywords": "medicine healthcare biology chemistry anatomy physiology clinical patient care research diagnostics health science dedication service",
        "preferred_tests": ["MCAT"],
        "min_test_score": 500,
    },
    "Law": {
        "description": "Law program focusing on constitutional law, criminal justice, corporate law, ethics, argumentation, critical thinking, and legal research.",
        "min_gpa": 3.0,
        "preferred_gpa": 3.5,
        "keywords": "law legal justice ethics argumentation critical thinking research policy governance rights advocacy writing analytical",
        "preferred_tests": ["LSAT"],
        "min_test_score": 155,
    },
    "Arts & Humanities": {
        "description": "Arts and Humanities program covering literature, philosophy, history, creative arts, cultural studies, and critical analysis.",
        "min_gpa": 2.8,
        "preferred_gpa": 3.2,
        "keywords": "arts humanities literature philosophy history creative culture writing expression analysis critique society communication",
        "preferred_tests": ["SAT", "GRE"],
        "min_test_score": 1200,
    },
}


class ProgramVectorStore:
    """FAISS-backed vector store for program-applicant matching."""

    def __init__(self):
        self.vectorizer = TfidfVectorizer(max_features=500, stop_words="english")
        self.index = None
        self.program_names = []
        self._build_index()

    def _build_index(self):
        """Build FAISS index from program descriptions."""
        corpus = []
        self.program_names = []

        for name, data in PROGRAM_DATA.items():
            # Combine description and keywords for richer representation
            text = f"{data['description']} {data['keywords']}"
            corpus.append(text)
            self.program_names.append(name)

        # Fit TF-IDF and transform
        tfidf_matrix = self.vectorizer.fit_transform(corpus)
        vectors = tfidf_matrix.toarray().astype("float32")

        # Normalize for cosine similarity
        faiss.normalize_L2(vectors)

        # Build FAISS index (Inner Product = cosine similarity on normalized vectors)
        dimension = vectors.shape[1]
        self.index = faiss.IndexFlatIP(dimension)
        self.index.add(vectors)

        print(f"[VectorStore] Built FAISS index with {len(self.program_names)} programs, dim={dimension}")

    def _build_applicant_text(self, submitted_data: dict) -> str:
        """Build a text representation of an applicant's profile."""
        parts = [
            submitted_data.get("program", ""),
            submitted_data.get("essay", ""),
            f"GPA {submitted_data.get('gpa', '')}",
            submitted_data.get("test_scores", ""),
        ]
        return " ".join(p for p in parts if p)

    def match_applicant(self, submitted_data: dict, top_k: int = 3) -> list[dict]:
        """
        Match an applicant against program descriptions.
        Returns list of {program, similarity_score, program_data}.
        """
        applicant_text = self._build_applicant_text(submitted_data)

        # Transform applicant text
        query_vector = self.vectorizer.transform([applicant_text]).toarray().astype("float32")
        faiss.normalize_L2(query_vector)

        # Search FAISS
        scores, indices = self.index.search(query_vector, top_k)

        results = []
        for score, idx in zip(scores[0], indices[0]):
            if idx < 0:
                continue
            program_name = self.program_names[idx]
            results.append({
                "program": program_name,
                "similarity_score": float(score),
                "program_data": PROGRAM_DATA[program_name],
            })

        return results

    def get_program_requirements(self, program: str) -> dict:
        """Get requirements for a specific program."""
        return PROGRAM_DATA.get(program, {})

    def compute_eligibility_score(self, submitted_data: dict) -> dict:
        """
        Compute a comprehensive eligibility score using vector similarity + rules.
        Returns {score, reasons, matches, meets_requirements, requires_review}.
        """
        program = submitted_data.get("program", "")
        gpa = float(submitted_data.get("gpa", 0))
        essay = submitted_data.get("essay", "")
        test_scores_str = submitted_data.get("test_scores", "")

        # 1. Vector similarity matching
        matches = self.match_applicant(submitted_data, top_k=3)

        # Find the target program match
        target_match = next((m for m in matches if m["program"] == program), None)
        target_similarity = target_match["similarity_score"] if target_match else 0.0

        # 2. Program-specific requirements
        program_req = self.get_program_requirements(program)
        min_gpa = program_req.get("min_gpa", 3.0)
        preferred_gpa = program_req.get("preferred_gpa", 3.5)

        # 3. Scoring breakdown
        reasons = []

        # GPA score (40% weight)
        if gpa >= preferred_gpa:
            gpa_score = 40.0
            reasons.append(f"GPA {gpa} exceeds preferred threshold ({preferred_gpa}) for {program}")
        elif gpa >= min_gpa:
            gpa_score = 25.0 + (gpa - min_gpa) / (preferred_gpa - min_gpa) * 15.0
            reasons.append(f"GPA {gpa} meets minimum requirement ({min_gpa}) for {program}")
        else:
            gpa_score = max(0, gpa / min_gpa * 20.0)
            reasons.append(f"GPA {gpa} below minimum requirement ({min_gpa}) for {program}")

        # Vector similarity score (30% weight)
        similarity_score = target_similarity * 30.0
        if target_similarity > 0.3:
            reasons.append(f"Strong profile-program alignment (similarity: {target_similarity:.2f})")
        elif target_similarity > 0.1:
            reasons.append(f"Moderate profile-program alignment (similarity: {target_similarity:.2f})")
        else:
            reasons.append(f"Weak profile-program alignment (similarity: {target_similarity:.2f})")

        # Essay presence (15% weight)
        essay_score = 0.0
        if essay and len(essay) > 50:
            essay_score = 15.0
            reasons.append("Personal statement provided and substantial")
        elif essay:
            essay_score = 8.0
            reasons.append("Personal statement provided but brief")
        else:
            reasons.append("No personal statement provided")

        # Test scores (15% weight)
        test_score_val = 0.0
        if test_scores_str:
            import re
            numbers = re.findall(r"\d+", test_scores_str)
            if numbers:
                test_score_val = 15.0
                reasons.append(f"Test scores provided: {test_scores_str}")
            else:
                test_score_val = 5.0
                reasons.append("Test scores mentioned but unclear")
        else:
            reasons.append("No test scores provided")

        # Total score
        total_score = gpa_score + similarity_score + essay_score + test_score_val
        total_score = min(100.0, max(0.0, total_score))

        # Determine eligibility
        meets_requirements = gpa >= min_gpa and total_score >= 50.0

        # Human review conditions
        requires_review = False
        review_reason = None
        if min_gpa - 0.2 <= gpa < min_gpa:
            requires_review = True
            review_reason = f"GPA {gpa} slightly below {program} minimum ({min_gpa}) - manual review recommended"
        elif gpa >= min_gpa and gpa < min_gpa + 0.2:
            requires_review = True
            review_reason = f"Borderline GPA {gpa} for {program} (min: {min_gpa}) - manual review recommended"
        elif 45.0 <= total_score < 55.0:
            requires_review = True
            review_reason = f"Borderline eligibility score ({total_score:.1f}/100) - manual review recommended"

        # Top alternative programs
        alt_programs = [m["program"] for m in matches if m["program"] != program][:2]
        if alt_programs:
            reasons.append(f"Also strong match for: {', '.join(alt_programs)}")

        return {
            "score": round(total_score, 1),
            "reasons": reasons,
            "matches": matches,
            "meets_requirements": meets_requirements,
            "requires_review": requires_review,
            "review_reason": review_reason,
            "gpa_score": round(gpa_score, 1),
            "similarity_score": round(similarity_score, 1),
            "essay_score": round(essay_score, 1),
            "test_score": round(test_score_val, 1),
        }


# Singleton instance
vector_store = ProgramVectorStore()
