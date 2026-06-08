from fastapi import FastAPI, Request, HTTPException
from pydantic import BaseModel
import json, os, requests, re, joblib, asyncio
from sqlalchemy import create_engine
import pandas as pd
import numpy as np
from neo4j import GraphDatabase
import tensorflow as tf
import faiss
from sentence_transformers import SentenceTransformer
from contextlib import asynccontextmanager
from fastapi.middleware.cors import CORSMiddleware

# Define Request Models
class ChatRequest(BaseModel):
    query: str
    user_id: int = 0
    mode: str = "predict"

class RecommendRequest(BaseModel):
    user_id: int = 0
    top_n: int = 4

class TrackRequest(BaseModel):
    user_id: int
    product_id: str
    category: str
    action: str  # 'click', 'view', 'add_to_cart', 'purchase'

# Global Assets
assets = {
    "docs": [],
    "eng": None,
    "neo4j_driver": None,
    "faiss_index": None,
    "emb_model": None,
    "model_best": None,
    "le": None
}

# Config
PG_PROD    = "postgresql+psycopg2://postgres:password@postgres_db:5432/ms_product"
OLLAMA_URL = os.getenv("OLLAMA_URL", "http://host.docker.internal:11434/api/generate")
OLLAMA_MODEL = os.getenv("OLLAMA_MODEL", "hf.co/phamhai/Llama-3.2-3B-Instruct-Frog-Q4_K_M-GGUF:Q4_K_M")
NEO4J_URI  = os.getenv("NEO4J_URI", "bolt://neo4j:7687")
NEO4J_USER = os.getenv("NEO4J_USER", "neo4j")
NEO4J_PWD  = os.getenv("NEO4J_PASSWORD", "password")

@asynccontextmanager
async def lifespan(app: FastAPI):
    try:
        assets["eng"] = create_engine(PG_PROD)
        df_p = pd.read_sql("SELECT p.*, c.name as category_name FROM product_service_product p JOIN product_service_category c ON p.category_id = c.id", assets["eng"])
        assets["docs"] = df_p.to_dict("records")
        assets["neo4j_driver"] = GraphDatabase.driver(NEO4J_URI, auth=(NEO4J_USER, NEO4J_PWD))
        
        assets["emb_model"] = SentenceTransformer('paraphrase-multilingual-MiniLM-L12-v2')
        if assets["docs"]:
            texts = [f"{d['brand']} {d['name']} {d.get('category_name', '')}. {d.get('description', '')}" for d in assets["docs"]]
            embeddings = assets["emb_model"].encode(texts, show_progress_bar=False).astype('float32')
            faiss.normalize_L2(embeddings)
            
            dimension = embeddings.shape[1]
            index = faiss.IndexFlatIP(dimension)
            index.add(embeddings)
            assets["faiss_index"] = index
            print(f"✅ FAISS & RAG dynamically built with {len(texts)} products from Database.")
            
        MODEL_PATH = '/app/models/model_best.keras'
        LE_PATH = '/app/models/category_le.pkl'
        if os.path.exists(MODEL_PATH):
            assets["model_best"] = tf.keras.models.load_model(MODEL_PATH)
            assets["le"] = joblib.load(LE_PATH)
            print("✅ LSTM Model loaded.")
    except Exception as e:
        print(f"❌ AI Startup Error: {e}")
    yield
    if assets["neo4j_driver"]: assets["neo4j_driver"].close()

app = FastAPI(lifespan=lifespan, title="MegaStore AI FastAPI Service")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

def predict_interest(user_id):
    if not assets["model_best"] or not assets["neo4j_driver"] or not user_id: return None
    try:
        with assets["neo4j_driver"].session() as session:
            res = session.run("MATCH (u:User {id: $uid})-[r]->(p:Product)-[:BELONGS_TO]->(c:Category) RETURN c.name as cat_name ORDER BY r.timestamp DESC LIMIT 3", uid=int(user_id))
            cats = [r['cat_name'] for r in res]
            if len(cats) < 3: return None
            ids = assets["le"].transform(cats[::-1])
            p = assets["model_best"].predict(np.array([ids]), verbose=0)
            return assets["le"].inverse_transform([np.argmax(p)])[0]
    except: return None

def get_rag_results(query, k=4):
    query_lower = query.lower()
    
    # Identify Target Category
    target_cat = None
    if any(kw in query_lower for kw in ["laptop", "máy tính", "computer", "macbook", "pc"]):
        target_cat = "Computer"
    elif any(kw in query_lower for kw in ["điện thoại", "phone", "iphone", "samsung", "mobile", "đt"]):
        target_cat = "Mobile"
    elif any(kw in query_lower for kw in ["giày", "shoes", "sneaker", "giay"]):
        target_cat = "Shoes"
    elif any(kw in query_lower for kw in ["quần áo", "áo", "quần", "clothes", "shirt", "jeans", "jacket", "hoodie", "thời trang"]):
        target_cat = "Clothes"
    elif any(kw in query_lower for kw in ["đồng hồ", "watch", "dong ho"]):
        target_cat = "Watches"
    elif any(kw in query_lower for kw in ["mỹ phẩm", "cosmetics", "son", "kem", "perfume", "nước hoa"]):
        target_cat = "Cosmetics"
    elif any(kw in query_lower for kw in ["nội thất", "bàn", "ghế", "furniture", "sofa", "chair", "table"]):
        target_cat = "Furniture"
    elif any(kw in query_lower for kw in ["bếp", "kitchenware", "nồi", "dao", "kettle", "mixer"]):
        target_cat = "Kitchenware"
    elif any(kw in query_lower for kw in ["sách", "book", "truyện"]):
        target_cat = "Books"
    elif any(kw in query_lower for kw in ["thể thao", "sportswear", "gym", "yoga"]):
        target_cat = "Sportswear"
    elif any(kw in query_lower for kw in ["phụ kiện", "accessories", "kính", "ví", "wallet", "backpack"]):
        target_cat = "Accessories"

    # Identify Price Intent
    sort_mode = None 
    if any(kw in query_lower for kw in ["rẻ", "thấp", "cheap", "giá tốt"]):
        sort_mode = 1
    elif any(kw in query_lower for kw in ["đắt", "cao", "expensive", "premium", "mạnh nhất"]):
        sort_mode = -1

    # Filter all docs by category first for guaranteed accuracy
    filtered_docs = assets["docs"]
    if target_cat:
        filtered_docs = [d for d in assets["docs"] if d['category_name'] == target_cat]

    if sort_mode == 1:
        filtered_docs.sort(key=lambda x: x['price'])
        return filtered_docs[:k]
    elif sort_mode == -1:
        filtered_docs.sort(key=lambda x: x['price'], reverse=True)
        return filtered_docs[:k]

    # Standard Semantic Search
    if assets["faiss_index"]:
        q_emb = assets["emb_model"].encode([query]).astype('float32')
        faiss.normalize_L2(q_emb)
        _, ids = assets["faiss_index"].search(q_emb, 20)
        candidates = [assets["docs"][i] for i in ids[0] if i < len(assets["docs"])]
        if target_cat:
            candidates = [c for c in candidates if c['category_name'] == target_cat]
        return candidates[:k]
    
    return filtered_docs[:k]

def get_graph_ctx(query):
    if not assets["neo4j_driver"]: return ""
    try:
        with assets["neo4j_driver"].session() as session:
            res = session.run("MATCH (p:Product)-[:BELONGS_TO]->(c:Category) WHERE toLower(p.name) CONTAINS toLower($q) RETURN p.name as n, c.name as c LIMIT 2", q=query[:10])
            return "\n".join([f"- {r['n']} (Danh mục: {r['c']})" for r in res])
    except: return ""

def ask_ollama(prompt):
    try:
        r = requests.post(OLLAMA_URL, json={"model": OLLAMA_MODEL, "prompt": prompt, "stream": False}, timeout=60)
        return r.json().get("response")
    except: return None

@app.post("/chat")
async def chat(req: ChatRequest):
    p_cat = predict_interest(req.user_id)
    products = get_rag_results(req.query)
    graph = get_graph_ctx(req.query)
    
    prompt = f"BẠN LÀ MEGASTORE AI. NHIỆM VỤ: TƯ VẤN SẢN PHẨM CHÍNH XÁC.\n"
    prompt += f"KHÁCH HỎI: '{req.query}'\n"
    
    if products:
        p_str = "\n".join([f"- {p['name']} ({p['brand']}) [GIÁ: ${p['price']}]: {p['category_name']}" for p in products])
        prompt += f"DANH SÁCH SẢN PHẨM PHÙ HỢP TRONG KHO (từ FAISS RAG):\n{p_str}\n"

    if graph:
        prompt += f"\nTHÔNG TIN SẢN PHẨM THÊM TỪ ĐỒ THỊ (từ Neo4j):\n{graph}\n"

    if p_cat:
        prompt += f"\nGỢI Ý SỞ THÍCH KHÁCH HÀNG (Dự đoán từ Neo4j + Bi-LSTM): {p_cat}\n"

    prompt += "\n⚠️ QUY TẮC:\n"
    prompt += "1. CHỈ ĐƯỢC tư vấn sản phẩm có trong danh sách trên (từ kho FAISS hoặc đồ thị Neo4j).\n"
    prompt += "2. Nếu khách hỏi rẻ nhất/đắt nhất, hãy chỉ đích danh máy có giá thấp nhất/cao nhất trong danh sách.\n"
    prompt += "3. Ưu tiên gợi ý sản phẩm thuộc danh mục khách hàng đang quan tâm nhất (nếu có thông tin gợi ý sở thích).\n"
    prompt += "4. Trả lời ngắn gọn, tự nhiên, chuyên nghiệp bằng Tiếng Việt."

    answer = ask_ollama(prompt) or "AI đang bận, vui lòng thử lại."
    return {
        "answer": answer,
        "products": products,
        "predicted_category": p_cat
    }

@app.post("/recommend")
async def recommend(req: RecommendRequest):
    cat = predict_interest(req.user_id) or "Computer"
    recs = [d['name'] for d in assets["docs"] if d['category_name'] == cat][:req.top_n]
    return {"recommendations": recs}

@app.post("/segment")
async def segment(req: RecommendRequest):
    return {"segment": "VIP", "monetary": 5000, "user_id": req.user_id}

@app.post("/track")
async def track_action(req: TrackRequest):
    if not assets["neo4j_driver"] or not req.user_id or not req.product_id:
        return {"status": "ignored"}
    try:
        rel_type = req.action.upper()
        if rel_type not in ["VIEW", "CLICK", "ADD_TO_CART", "PURCHASE"]:
            raise HTTPException(status_code=400, detail="Invalid action type")
            
        with assets["neo4j_driver"].session() as session:
            session.run("""
                MERGE (c:Category {name: $cat_name})
                MERGE (p:Product {id: $prod_id})
                MERGE (p)-[:BELONGS_TO]->(c)
                MERGE (u:User {id: $user_id})
                MERGE (u)-[r:""" + rel_type + """]->(p)
                SET r.timestamp = datetime().epochMillis
            """, cat_name=req.category, prod_id=req.product_id, user_id=int(req.user_id))
        return {"status": "success", "action": rel_type}
    except Exception as e:
        print(f"❌ Neo4j Track Action Error: {e}")
        return {"status": "error", "message": str(e)}

@app.get("/health")
async def health():
    return {"status": "healthy", "assets_loaded": len(assets["docs"]) > 0}
