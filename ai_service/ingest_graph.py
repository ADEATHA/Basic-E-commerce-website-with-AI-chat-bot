import pandas as pd
from neo4j import GraphDatabase
import os

class Neo4jIngestor:
    def __init__(self, uri, user, password):
        self.driver = GraphDatabase.driver(uri, auth=(user, password))

    def close(self):
        self.driver.close()

    def ingest_data(self, csv_path):
        df = pd.read_csv(csv_path)
        
        with self.driver.session() as session:
            # 1. Clear existing data (optional, but good for clean start)
            print("Clearing existing data...")
            session.run("MATCH (n) DETACH DELETE n")
            
            # 2. Create constraints
            print("Creating constraints...")
            session.run("CREATE CONSTRAINT IF NOT EXISTS FOR (u:User) REQUIRE u.id IS UNIQUE")
            session.run("CREATE CONSTRAINT IF NOT EXISTS FOR (p:Product) REQUIRE p.id IS UNIQUE")
            session.run("CREATE CONSTRAINT IF NOT EXISTS FOR (c:Category) REQUIRE c.name IS UNIQUE")
            
            # 3. Create Categories
            print("Creating Category nodes...")
            categories = df['category'].unique()
            for cat in categories:
                session.run("MERGE (c:Category {name: $name})", name=cat)
            
            # 4. Create Products and Link to Categories
            print("Creating Product nodes...")
            products = df[['product_id', 'category']].drop_duplicates()
            for _, row in products.iterrows():
                session.run("""
                    MERGE (p:Product {id: $id})
                    WITH p
                    MATCH (c:Category {name: $cat_name})
                    MERGE (p)-[:BELONGS_TO]->(c)
                """, id=row['product_id'], cat_name=row['category'])
            
            # 5. Create Users and Behaviors
            print("Creating User nodes and behavioral relationships...")
            # We'll batch this for performance
            batch_size = 500
            for i in range(0, len(df), batch_size):
                batch = df.iloc[i:i+batch_size]
                session.execute_write(self._create_behaviors, batch)
                print(f"Ingested {min(i+batch_size, len(df))} / {len(df)} events")

    @staticmethod
    def _create_behaviors(tx, batch):
        for _, row in batch.iterrows():
            rel_type = row['action'].upper()
            tx.run(f"""
                MERGE (u:User {{id: $user_id}})
                WITH u
                MATCH (p:Product {{id: $product_id}})
                MERGE (u)-[:{rel_type} {{timestamp: $ts}}]->(p)
            """, user_id=int(row['user_id']), product_id=row['product_id'], ts=row['timestamp'])

if __name__ == "__main__":
    # Environments from docker-compose or defaults
    URI = os.getenv("NEO4J_URI", "bolt://localhost:7687")
    USER = os.getenv("NEO4J_USER", "neo4j")
    PWD = os.getenv("NEO4J_PASSWORD", "password")
    
    csv_file = "ai_service/data/data_user500.csv"
    if not os.path.exists(csv_file):
        csv_file = "data/data_user500.csv"
        
    ingestor = Neo4jIngestor(URI, USER, PWD)
    try:
        ingestor.ingest_data(csv_file)
        print("Graph ingestion complete!")
    except Exception as e:
        print(f"Error during ingestion: {e}")
        print("Note: Ensure Neo4j is running and accessible.")
    finally:
        ingestor.close()
