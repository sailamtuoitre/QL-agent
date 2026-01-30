# AI Agent Phân Tích Doanh Thu Nhà Hàng - Kiến Trúc Hệ Thống

## 1. Tổng Quan Hệ Thống
**Mục tiêu:** Xây dựng một hệ thống AI Agent chuẩn Production, thiết kế theo hướng module hóa, có khả năng tiếp nhận dữ liệu doanh thu nhà hàng thô (Excel/CSV), xử lý hiệu quả, thực hiện phân tích, tạo biểu đồ trực quan, và sử dụng LLM để viết báo cáo kinh doanh toàn diện.

**Triết lý Cốt lõi:** "Production-First but Resource-Aware" (Ưu tiên chuẩn Production nhưng tối ưu tài nguyên). Hệ thống được thiết kế sẵn sàng cho môi trường doanh nghiệp (Bảo mật, Khả năng mở rộng, Khả năng giám sát) đồng thời hỗ trợ chế độ "Dev-Lite" nhẹ nhàng để phát triển trên các máy tính cấu hình thấp.

## 2. Kiến Trúc: Lai & Module Hóa

### Sơ đồ Cấp cao
```text
[Frontend (Next.js)] <---> [API Gateway (FastAPI)] <---> [Async Workers (Celery)]
       |                            |                           |
       v                            v                           v
[Giao diện Người dùng]        [Bộ Điều Phối]              [Bộ Máy Dữ Liệu]
(Dashboards/Chat)           (LangGraph Agent)           (Pandas/Parquet)
                                    |
                                    v
                            [Tầng Thông Minh]
                        (LLM + Vector DB + Memory)
```

### Chế độ Dev (Lite) vs. Production (Enterprise)

| Thành phần | **Local Dev (Chế độ Tiết kiệm)** | **Production (Chế độ Doanh nghiệp)** |
| :--- | :--- | :--- |
| **Backend** | Native Process (`uvicorn main:app`) | Docker Container (Gunicorn) |
| **Frontend** | Native Process (`npm run dev`) | Docker Container (Next.js Standalone) |
| **Vector DB** | **ChromaDB Embedded** (Chạy trong process, file-based) | ChromaDB Server (Http Client-Server) |
| **Queue/Cache**| **Redis Tối giản** (1 Docker Container) | Managed Redis Cluster / High-Availability |
| **Giám sát**| **SaaS Cloud** (LangSmith/Langfuse Free Tier) | Self-hosted Prometheus + Grafana |
| **Xác thực** | OAuth2 (JWT) | OAuth2 (JWT) + Tích hợp IDP |

## 3. Các Quyết Định Kiến Trúc Chính

### A. Tech Stack (Python Backend + TypeScript Frontend)
*   **Backend:** **Python 3.10+**, **FastAPI** (API), **LangGraph** (Logic Agent).
*   **Frontend:** **TypeScript**, **Next.js** (React Framework), **Tailwind CSS**.
*   **Chiến lược Dữ liệu:** 
    *   **Tiếp nhận:** Excel/CSV $\to$ **Apache Parquet** (Lưu trữ hiệu năng cao).
    *   **Truyền tải:** JSON cho biểu đồ phía frontend.
*   **AI Engine:** 
    *   **LLM:** OpenAI / Anthropic.
    *   **Memory:** ChromaDB (Vector Search cho lịch sử/tri thức).

### B. Tiêu chuẩn Bảo mật & Production
*   **Xác thực:** OAuth2 dựa trên JWT với Kiểm soát truy cập theo vai trò (RBAC).
*   **Mã hóa:** TLS cho đường truyền, AES cho các file Parquet nhạy cảm (tùy chọn).
*   **Khả năng chịu lỗi:** Circuit Breakers cho các cuộc gọi LLM, Logic thử lại (Exponential Backoff) cho các API bên ngoài.
*   **Đa khách hàng (Multi-tenancy):** Cô lập dữ liệu logic (Tenant ID trong DB/Files) để hỗ trợ nhiều chuỗi nhà hàng.

### C. Luồng Agentic (LangGraph)
Agent được mô hình hóa như một Máy Trạng Thái (State Machine), không phải chuỗi tuyến tính:
1.  **Router:** Phân loại ý định (Truy vấn vs. Biểu đồ vs. Báo cáo).
2.  **Tools:** Pandas Analyst, Plotly Visualizer, Retriever.
3.  **Critique/Guardrails:** Xác thực định dạng đầu ra và kiểm tra ảo giác.
4.  **Memory:** Lưu trữ ngữ cảnh hội thoại và phản hồi của người dùng.

### D. Tầng Thông Minh: Chiến lược Đa LLM (All-in)
Để đảm bảo sự linh hoạt và hiệu quả chi phí, hệ thống hỗ trợ thay thế các nhà cung cấp LLM:
1.  **OpenAI (Production):** Chất lượng cao, API trả phí (GPT-4o).
2.  **Gemini (Free Tier):** Gói miễn phí của Google để phát triển/kiểm thử. (Đánh đổi: Cần code adapter, rủi ro prompt không nhất quán).
3.  **Mock (Dev/Offline):** Chế độ giả lập cục bộ trả về các phản hồi tĩnh mẫu. (Đánh đổi: Không có trí thông minh thực).
*Cấu hình qua `.env`: `LLM_PROVIDER=OPENAI|GEMINI|MOCK`*

### E. Kiến trúc Kiểm soát Chi phí (Tối ưu Thông minh)
Để đảm bảo tính bền vững và chi phí hợp lý, hệ thống triển khai lớp phòng thủ chi phí đa tầng:
1.  **Tầng 1: Deterministic Engine (Chi phí 0):** 
    *   Các câu hỏi về số liệu cụ thể (Tổng, Đếm, Trung bình) được trả lời bằng Pandas/SQL. (Đánh đổi: NLU kém linh hoạt hơn).
2.  **Tầng 2: Semantic Caching (Chi phí 0):** 
    *   ChromaDB kiểm tra các truy vấn tương tự trong quá khứ. Tỷ lệ trùng > 0.9 trả về phản hồi đã lưu đệm. (Đánh đổi: Rủi ro dữ liệu cũ).
3.  **Tầng 3: Optimized Context:** 
    *   Chỉ các số liệu đã tổng hợp và tóm tắt thống kê được gửi đến LLM, giảm lượng token tải lên ~95%. (Đánh đổi: Mất độ chi tiết).
4.  **Tầng 4: Adaptive Routing:** 
    *   Tác vụ đơn giản -> Gemini Free / Llama 3 (Groq).
    *   Suy luận phức tạp -> GPT-4o.

## 4. Cấu Trúc Dự Án

```text
.
├── backend/                  # DỊCH VỤ PYTHON (Bộ Não)
│   ├── app/
│   │   ├── api/              # Endpoints (v1/auth, v1/ingest, v1/chat)
│   │   ├── core/             # Cấu hình (Dev/Prod switch), Bảo mật
│   │   ├── agent/            # Các Node & Tool của LangGraph
│   │   ├── services/         # Logic Nghiệp vụ (ETL, Analysis, LLM Factory)
│   │   ├── db/               # ChromaDB (Embedded/Server) & Redis
│   │   └── workers/          # Celery Tasks
│   ├── data/                 # Hồ dữ liệu (bỏ qua trong git)
│   ├── tests/                # Pytest
│   ├── requirements.txt
│   └── main.py
│
├── frontend/                 # DỊCH VỤ TYPESCRIPT (Bộ Điều Khiển)
│   ├── src/
│   │   ├── app/              # Next.js Pages
│   │   ├── components/       # UI (Charts, Chat)
│   │   └── services/         # Tích hợp API
│   ├── package.json
│   └── tsconfig.json
│
├── docker-compose.dev.yml    # Hạ tầng tối giản (Chỉ Redis)
└── SYSTEM_ARCHITECTURE.md    # Tài liệu này
```

## 5. Lộ Trình Thực Thi

### Phase 1: Nền tảng & Hạ tầng (Đã hoàn thành)
*   Khởi tạo cấu trúc dự án, core FastAPI, và hạ tầng Redis tối thiểu.

### Phase 2: Core Data Pipeline & Hỗ trợ Đa LLM (Trọng tâm hiện tại)
*   **Mục tiêu:** Xử lý Upload File, Chuyển đổi Parquet, và xây dựng nền tảng Tầng Thông Minh.
*   **Quản lý:** Sử dụng `bd` để theo dõi tiến độ.
*   **Nhiệm vụ:**
    1.  **Ingestion API (`POST /upload`):** Validate loại file, lưu file thô xuống đĩa.
    2.  **Async Worker (Celery):** Chuyển đổi Excel/CSV $\to$ Parquet dưới nền.
    3.  **Data Validation:** Xây dựng Pydantic models để kiểm tra schema.
    4.  **LLM Service Factory:** Xây dựng `LLMFactory` để chuyển đổi giữa OpenAI, Gemini, và Mock services.
    5.  **Semantic Cache:** Thiết lập ChromaDB để cache truy vấn.

### Phase 3: Agent & Trí Thông Minh
*   **Mục tiêu:** Xây dựng LangGraph Agent.
*   **Nhiệm vụ:**
    *   Xây dựng Analyst Tools (Pandas).
    *   Xây dựng Visualization Tools (Plotly JSON).
    *   Kết nối LLM (OpenAI) & Bộ nhớ (ChromaDB Embedded).

### Phase 4: Frontend & Hoàn thiện Production
*   **Mục tiêu:** Giao diện người dùng và Bảo mật.
*   **Nhiệm vụ:**
    *   Xây dựng Dashboard Next.js.
    *   Tích hợp UI Biểu đồ & Chat.
    *   Tích hợp JWT Auth & RBAC.
    *   Hoàn thiện Logging/Tracing (LangSmith).

## 6. Hướng dẫn Lập trình viên (Quick Start)
1.  **Khởi động Hạ tầng:** `docker-compose -f docker-compose.dev.yml up -d` (Chạy Redis).
2.  **Khởi động Backend:** `cd backend && uvicorn main:app --reload`.
3.  **Khởi động Frontend:** `cd frontend && npm run dev`.

## 7. Quản lý Dự án (Project Management)
Sử dụng công cụ `bd` (beads) để theo dõi issue.
*   `bd show`: Xem danh sách task.
*   `bd update <id> --status in_progress`: Nhận việc.
*   `bd close <id>`: Hoàn thành việc.
