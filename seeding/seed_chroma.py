# seeding/seed_chroma.py
import os
import sys
import chromadb
import pandas as pd
import torch
from sentence_transformers import SentenceTransformer
from chromadb.api.types import EmbeddingFunction, Documents, Embeddings

BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.append(BASE_DIR)

from config import config

DATA_DIR = config["paths"]["data_dir"]
CHROMA_DIR = config["paths"]["chroma_dir"]
COLLECTION_NAME = config["rag"]["collection_name"]
MODEL_NAME = config["rag"]["embedding_model"]

class QwenEmbeddingFunction(EmbeddingFunction):
    def __init__(self, model_name: str):
        self.model = SentenceTransformer(
            model_name, 
            model_kwargs={"torch_dtype": torch.float32}
        )

    def __call__(self, input: Documents) -> Embeddings:
        return self.model.encode(input, normalize_embeddings=True).tolist()

def init_chroma():
    print(f"--- Initializing ChromaDB: {CHROMA_DIR} ---")
    os.makedirs(os.path.dirname(CHROMA_DIR), exist_ok=True)
        
    client = chromadb.PersistentClient(path=CHROMA_DIR)
    
    print(f"Loading embedding model: {MODEL_NAME} ...")
    embedding_fn = QwenEmbeddingFunction(MODEL_NAME)
    
    collection = client.get_or_create_collection(
        name=COLLECTION_NAME, 
        embedding_function=embedding_fn
    )
    
    if collection.count() > 0:
        print(f"✅ ChromaDB already contains {collection.count()} items. Skipping initialization.")
        return
    
    documents = []
    metadatas = []
    ids = []
    
    try:
        df_clinics = pd.read_csv(os.path.join(DATA_DIR, "clinics.csv"))
        for _, row in df_clinics.iterrows():
            text = f"Clinic Name: {row['clinic_name']}. Address: {row['address']}. Operating Hours: {row['operating_hours']}. Cancellation Policy: {row['cancellation_policy']}. Emergency Instructions: {row['emergency_instructions']}."
            documents.append(text)
            metadatas.append({"type": "clinic", "id": row['clinic_id']})
            ids.append(f"clinic_{row['clinic_id']}")
            
        df_doctors = pd.read_csv(os.path.join(DATA_DIR, "doctors.csv"))
        for _, row in df_doctors.iterrows():
            text = f"Doctor ID: {row['doctor_id']}. Doctor Name: {row['full_name']}. Clinic ID: {row['clinic_id']}. Specialty: {row['specialty']}. Languages: {row['languages_spoken']}. Fee: ${row['consultation_fee_usd']}. Bio: {row['bio']}."
            documents.append(text)
            metadatas.append({"type": "doctor", "id": row['doctor_id'], "clinic_id": row['clinic_id']})
            ids.append(f"doctor_{row['doctor_id']}")

        df_treatments = pd.read_csv(os.path.join(DATA_DIR, "treatments.csv"))
        for _, row in df_treatments.iterrows():
            text = f"Treatment ID: {row['treatment_id']}. Treatment Name: {row['treatment_name']}. Category: {row['category']}. Duration: {row['duration_minutes']} mins. Price: ${row['price_usd']}. Instructions: {row['pre_treatment_instructions']}."
            documents.append(text)
            metadatas.append({"type": "treatment", "id": row['treatment_id']})
            ids.append(f"treatment_{row['treatment_id']}")
            
        if documents:
            collection.add(
                documents=documents,
                metadatas=metadatas,
                ids=ids
            )
            print(f"✅ Successfully added {len(documents)} items to ChromaDB.")
            
    except Exception as e:
        print(f"❌ Failed to process data: {str(e)}")
        
    print("--- ChromaDB initialization completed ---\n")

if __name__ == "__main__":
    init_chroma()