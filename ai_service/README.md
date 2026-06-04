# AI Service Model & Data Directory
# 
# These directories are populated when you run the Jupyter notebook:
#   notebooks/AI_Ecommerce_System.ipynb
#
# Section B exports:
#   models/segment_clf.pkl   — XGBoost/RF classifier (customer segment)
#   models/label_enc.pkl     — LabelEncoder for segment names
#   models/scaler.pkl        — StandardScaler
#   models/item_sim.csv      — Item-Item similarity matrix (collaborative filtering)
#   models/user_product.csv  — User-Product purchase matrix
#
# Section C exports:
#   models/product_faiss.index  — FAISS vector index (product embeddings)
#   data/knowledge_base.json    — Product catalog documents
#
# To populate: run the notebook first, then rebuild Docker image.
