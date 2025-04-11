import os
import cv2
import insightface
import numpy as np
from numpy.linalg import norm
from insightface.app import FaceAnalysis

def cosine_similarity(a, b):
    return np.dot(a, b) / (norm(a) * norm(b))

# Initialize model
app = FaceAnalysis(name='buffalo_l')
app.prepare(ctx_id=-1)  # Use CPU

# Get base directory (same folder as this script)
BASE_DIR = os.path.dirname(os.path.abspath(__file__))

# Construct full path to the image
img_path = os.path.join(BASE_DIR, 'static', 'sameImg1.jpg')  # Adjust filename if needed

# Load the image
img = cv2.imread(img_path)

# Detect faces
faces = app.get(img)

# Check if enough faces are found
if len(faces) < 2:
    print("Not enough faces detected.")
else:
    # Loop through all combinations and compare
    for i in range(len(faces)):
        for j in range(i + 1, len(faces)):
            emb1 = faces[i].embedding
            emb2 = faces[j].embedding
            sim = cosine_similarity(emb1, emb2)
            print(f"Similarity between face {i+1} and face {j+1}: {sim}")

            if sim > 0.3:
                print(" → Same person")
            else:
                print(" → Different persons")
