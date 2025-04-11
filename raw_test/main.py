import os
import cv2
import insightface
import numpy as np
from numpy.linalg import norm
from insightface.app import FaceAnalysis

def cosine_similarity(a, b):
    return np.dot(a, b) / (norm(a) * norm(b))

# Prepare model on CPU (ctx_id = -1)
app = FaceAnalysis(name='buffalo_l')  # or 'antelopev2' for faster model
app.prepare(ctx_id=-1)  # -1 means CPU only

# Get base directory (where main.py is located)
BASE_DIR = os.path.dirname(os.path.abspath(__file__))

# Full paths to images inside static folder
img1_path = os.path.join(BASE_DIR, 'static', 'myImg1.jpg')
img2_path = os.path.join(BASE_DIR, 'static', 'myImg2.jpg')

# Load images
img1 = cv2.imread(img1_path)
img2 = cv2.imread(img2_path)

# Get face info
faces1 = app.get(img1)
faces2 = app.get(img2)

# Check if faces found
if len(faces1) == 0 or len(faces2) == 0:
    print("Face not detected in one or both images.")
else:
    emb1 = faces1[0].embedding
    emb2 = faces2[0].embedding

    # Compute cosine similarity
    sim = cosine_similarity(emb1, emb2)
    print(f"Cosine Similarity: {sim}")

    # Threshold can be tuned (0.3 to 0.4 is a good range)
    if sim > 0.3:
        print("Same person")
    else:
        print("Different persons")
