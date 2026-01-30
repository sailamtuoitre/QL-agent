from fastapi.testclient import TestClient
from main import app
import pandas as pd
from io import BytesIO

client = TestClient(app)

def test_upload_valid_csv():
    data = {
        "date": ["2023-01-01", "2023-01-02"],
        "item": ["Burger", "Fries"],
        "quantity": [10, 20],
        "price": [5.0, 3.0],
        "total": [50.0, 60.0],
        "category": ["Food", "Food"]
    }
    df = pd.DataFrame(data)
    csv_content = df.to_csv(index=False)
    
    files = {"file": ("test.csv", csv_content.encode('utf-8'), "text/csv")}
    response = client.post("/api/v1/ingest/upload", files=files)
    
    assert response.status_code == 201
    json_resp = response.json()
    assert json_resp["status"] == "uploaded"
    assert json_resp["record_count"] == 2

def test_upload_invalid_column_csv():
    # Missing 'price'
    data = {
        "date": ["2023-01-01"],
        "item": ["Burger"],
        "quantity": [10]
    }
    df = pd.DataFrame(data)
    csv_content = df.to_csv(index=False)
    
    files = {"file": ("test_invalid.csv", csv_content.encode('utf-8'), "text/csv")}
    response = client.post("/api/v1/ingest/upload", files=files)
    
    assert response.status_code == 400
    assert "detail" in response.json()

def test_upload_invalid_type_csv():
    # Price is string "free" which should fail float validation
    data = {
        "date": ["2023-01-01"],
        "item": ["Burger"],
        "quantity": [10],
        "price": ["free"] 
    }
    df = pd.DataFrame(data)
    csv_content = df.to_csv(index=False)
    
    files = {"file": ("test_invalid_type.csv", csv_content.encode('utf-8'), "text/csv")}
    response = client.post("/api/v1/ingest/upload", files=files)
    
    assert response.status_code == 400

def test_upload_invalid_extension():
    files = {"file": ("test.txt", b"content", "text/plain")}
    response = client.post("/api/v1/ingest/upload", files=files)
    
    assert response.status_code == 400
    assert "File extension not allowed" in response.json()["detail"]
