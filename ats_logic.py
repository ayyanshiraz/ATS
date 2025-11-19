import os
import pandas as pd
import docx2txt
from pdfminer.high_level import extract_text
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.metrics.pairwise import cosine_similarity

class ATSScanner:
    def __init__(self):
        self.resumes = []      # List of text content
        self.filenames = []    # List of filenames
        self.vectorizer = TfidfVectorizer(stop_words='english')

    def clean_text(self, text):
        """Simple text cleaning to remove newlines and extra spaces."""
        if not text: return ""
        return ' '.join(text.replace('\n', ' ').split())

    def extract_text_from_pdf(self, file_path):
        """Extracts text from PDF using pdfminer.six"""
        try:
            return extract_text(file_path)
        except Exception as e:
            print(f"Error reading PDF {file_path}: {e}")
            return ""

    def extract_text_from_docx(self, file_path):
        """Extracts text from DOCX using docx2txt"""
        try:
            return docx2txt.process(file_path)
        except Exception as e:
            print(f"Error reading DOCX {file_path}: {e}")
            return ""

    def load_resumes(self, file_paths, progress_callback=None):
        """
        Loads and extracts text from a list of file paths.
        Updates the progress bar if a callback is provided.
        """
        self.resumes = []
        self.filenames = []
        
        total = len(file_paths)
        for index, file_path in enumerate(file_paths):
            text = ""
            if file_path.lower().endswith('.pdf'):
                text = self.extract_text_from_pdf(file_path)
            elif file_path.lower().endswith('.docx'):
                text = self.extract_text_from_docx(file_path)
            
            if text:
                self.resumes.append(self.clean_text(text))
                self.filenames.append(os.path.basename(file_path))
            
            # Update progress bar in the UI
            if progress_callback:
                progress_callback((index + 1) / total)

        return len(self.resumes)

    def get_top_candidates(self, job_description, top_n=3, threshold=15.0):
        """
        Compares loaded resumes to the JD and returns the top N candidates.
        
        Args:
            job_description (str): The text of the job description.
            top_n (int): Number of top candidates to return.
            threshold (float): Minimum percentage (0-100) required to be considered a match.
        """
        if not self.resumes:
            return pd.DataFrame()

        # 1. Vectorize: Combine JD + All Resumes into one matrix
        # The Job Description is always at index 0
        documents = [self.clean_text(job_description)] + self.resumes
        
        try:
            tfidf_matrix = self.vectorizer.fit_transform(documents)
        except ValueError:
            # Happens if documents are empty or contain only stop words
            return pd.DataFrame()

        # 2. Calculate Cosine Similarity
        # We compare the first vector (JD) against all others (Resumes)
        jd_vector = tfidf_matrix[0]
        cosine_similarities = cosine_similarity(jd_vector, tfidf_matrix[1:]).flatten()

        # 3. Create Initial DataFrame
        df = pd.DataFrame({
            'Candidate': self.filenames,
            'Score': cosine_similarities
        })

        # 4. Convert Score to Percentage (0-100)
        df['Match %'] = (df['Score'] * 100).round(2)
        
        # 5. FILTER: Remove candidates below the threshold
        # This is the key step that allows the app to say "No match found"
        df = df[df['Match %'] >= float(threshold)]

        # 6. Sort descending (Best matches first)
        df = df.sort_values(by='Score', ascending=False).reset_index(drop=True)

        # 7. Return only the top N results requested by user
        return df.head(int(top_n))