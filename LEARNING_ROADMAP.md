# Multi-Agent Research Assistant — Learning Roadmap

> **Mục tiêu:** Xây dựng hệ thống phân tích cổ phiếu tự động sử dụng multi-agent AI.
> **Người học:** Python cơ bản, chưa có kinh nghiệm LLM.
> **Định hướng:** Hiểu rõ kiến trúc từng lớp, dùng làm CV project.

---

## Giai đoạn 0 — Git & Project Setup (3–5 ngày)

> **Mục tiêu:** Biết dùng Git đúng cách ngay từ đầu. Mọi thứ bạn code từ Giai đoạn 1 trở đi đều được track bằng Git.
> **Triết lý:** Học Git qua thực hành trong project thật, không học lý thuyết suông.

### Tại sao Git quan trọng với CV project?

- Nhà tuyển dụng sẽ xem **GitHub của bạn** — commit history thể hiện quá trình tư duy
- Git workflow là thứ **mọi team đều dùng** — không biết là tự loại mình
- Bảo vệ code: không bao giờ mất code do xóa nhầm nữa

---

### Kiến thức cần học

- [ ] **Git cơ bản:** `init`, `add`, `commit`, `status`, `log`, `diff`
- [ ] **Branching:** `branch`, `checkout`, `merge` — làm việc không ảnh hưởng code chính
- [ ] **Remote:** `clone`, `push`, `pull`, kết nối với GitHub
- [ ] **Thực hành tốt:** `.gitignore`, commit message conventions, khi nào nên commit
- [ ] **Xử lý tình huống thực tế:** merge conflict, undo commit, stash

---

### Thứ phải làm (theo thứ tự)

#### Bước 1 — Setup Git & GitHub
- [ ] Cài Git, cấu hình `user.name` và `user.email`
- [ ] Tạo tài khoản GitHub (nếu chưa có)
- [ ] Tạo repo `multi-agent-research-assistant` trên GitHub
- [ ] `git init` trong thư mục project, kết nối với remote repo
- [ ] Tạo `.gitignore` ngay — **bắt buộc** phải có `.env` trong này

**Output:** Repo trên GitHub, commit đầu tiên là file `LEARNING_ROADMAP.md` này.

---

#### Bước 2 — Git Workflow thực tế
- [ ] Hiểu workflow: `main` branch là code ổn định, mỗi bài học là 1 branch mới
- [ ] Thực hành: tạo branch `phase1/lesson1`, code, commit, merge về `main`
- [ ] Viết commit message đúng cách (xem convention bên dưới)
- [ ] Dùng `git log --oneline` để xem lịch sử đẹp

**Output:** Biết tạo branch cho từng bài, merge về main sau khi xong.

---

#### Bước 3 — Tình huống thực tế
- [ ] **Lỡ commit nhầm file:** `git reset HEAD~1`
- [ ] **Muốn tạm cất code đang dở:** `git stash` và `git stash pop`
- [ ] **Xem code thay đổi gì:** `git diff`
- [ ] **Merge conflict:** hiểu tại sao xảy ra, tự resolve bằng tay

**Output:** Không còn sợ Git, biết xử lý tình huống hay gặp.

---

### Commit message convention (dùng xuyên suốt project)

```
<type>: <mô tả ngắn>

Types:
  feat     → thêm tính năng mới
  fix      → sửa bug
  learn    → code trong quá trình học
  refactor → cải thiện code không thêm tính năng
  docs     → cập nhật tài liệu
  chore    → setup, config, không liên quan code

Ví dụ:
  learn: implement basic Claude API call (lesson 1)
  feat: add stock price tool to chatbot
  fix: handle API timeout in financial data agent
  docs: update architecture diagram
```

---

### Git Workflow xuyên suốt project

```
Bắt đầu bài học mới:
  git checkout -b phase1/lesson2-tool-use

Trong lúc học (commit thường xuyên):
  git add <file>
  git commit -m "learn: hiểu tool use flow, implement basic example"

Hoàn thành bài:
  git checkout main
  git merge phase1/lesson2-tool-use
  git push origin main
```

> **Quy tắc vàng:** Commit mỗi khi code chạy được một thứ gì đó, dù nhỏ.
> Đừng đợi đến khi "xong hết" mới commit — đó không phải cách làm việc thực tế.

---

### Câu hỏi kiểm tra cuối Giai đoạn 0

1. Tại sao không commit file `.env` lên GitHub?
2. `git merge` và `git rebase` khác nhau thế nào? (biết khái niệm là đủ)
3. Khi nào dùng `git stash`?
4. Nhìn vào `git log` của project này, bạn thấy được gì?

---

## Kiến trúc tổng thể (Big Picture)

```
Người dùng hỏi
      │
      ▼
┌─────────────────────────────────────────┐
│           Orchestrator Agent            │  ← LangGraph điều phối
│         (não của hệ thống)              │
└──────┬──────────┬──────────┬────────────┘
       │          │          │
       ▼          ▼          ▼
┌──────────┐ ┌─────────┐ ┌──────────────┐
│   Web    │ │   RAG   │ │   Analysis   │
│  Agent   │ │  Agent  │ │    Agent     │
│(thu thập)│ │(đọc PDF)│ │  (phân tích) │
└──────────┘ └─────────┘ └──────────────┘
       │          │          │
       └──────────┴──────────┘
                  │
                  ▼
       ┌─────────────────┐
       │  Report Agent   │  ← Tổng hợp báo cáo cuối
       └─────────────────┘
                  │
                  ▼
          Báo cáo cho người dùng
```

**Tech stack:**
| Layer | Công nghệ | Vai trò |
|---|---|---|
| LLM | Claude API (Anthropic) | Não xử lý ngôn ngữ |
| Orchestration | LangGraph | Điều phối các agent |
| Vector DB | ChromaDB | Lưu & tìm kiếm báo cáo PDF |
| Stock Data | Alpha Vantage API | Dữ liệu giá cổ phiếu thực |
| PDF Parser | PyMuPDF | Đọc báo cáo tài chính |
| Backend (optional) | FastAPI | Expose API ra ngoài |

---

## Giai đoạn 1 — Nền tảng LLM (2–3 tuần)

> **Mục tiêu:** Hiểu LLM hoạt động thế nào, xây chatbot đơn giản có gọi API thực.

### Kiến thức cần học

- [ ] **Python bổ sung:** `pip`, virtual environment, `.env` file, `requests` library
- [ ] **LLM là gì:** Prompt, completion, token, temperature
- [ ] **Claude API:** Cách gọi, cấu trúc message, API key
- [ ] **Tool Use / Function Calling:** Cơ chế LLM gọi external function — **đây là nền tảng của multi-agent**
- [ ] **Conversation History:** Cách LLM nhớ ngữ cảnh hội thoại

### Thứ phải làm (theo thứ tự)

#### Bài 1 — Hello LLM
- [ ] Tạo tài khoản Anthropic, lấy API key
- [ ] Cài `anthropic` SDK: `pip install anthropic`
- [ ] Gửi message đầu tiên tới Claude, nhận response
- [ ] Hiểu cấu trúc: `role: user` / `role: assistant`

**Output:** Script Python in ra câu trả lời từ Claude.

---

#### Bài 2 — Tool Use (Function Calling)
- [ ] Hiểu tại sao LLM cần tool (nó không biết giờ hiện tại, không tự lấy data được)
- [ ] Định nghĩa 1 tool đơn giản: `get_stock_price(symbol)`
- [ ] Đọc hiểu vòng lặp tool-use: User → LLM → Tool Call → Tool Result → LLM → Response
- [ ] Implement vòng lặp đó bằng tay (không dùng framework)

**Output:** LLM tự quyết định khi nào gọi `get_stock_price`, bạn xử lý kết quả.

---

#### Bài 3 — Kết nối Alpha Vantage API
- [ ] Đăng ký Alpha Vantage, lấy free API key
- [ ] Gọi API lấy giá cổ phiếu thực (NVIDIA: `NVDA`)
- [ ] Parse JSON response
- [ ] Kết nối với tool từ Bài 2

**Output:** LLM gọi API thật và trả lời bằng dữ liệu thực.

---

#### Bài 4 — Chatbot hoàn chỉnh
- [ ] Thêm conversation history (lưu danh sách messages)
- [ ] Vòng lặp chat trên terminal
- [ ] Xử lý lỗi cơ bản (API timeout, symbol không tồn tại)

**Output:** Chatbot chạy được, hỏi được nhiều câu liên tiếp, nhớ context.

---

### Cấu trúc thư mục Giai đoạn 1

```
phase1/
├── .env                  # API keys (KHÔNG commit lên git)
├── requirements.txt      # anthropic, requests, python-dotenv
├── lesson1_hello_llm.py
├── lesson2_tool_use.py
├── lesson3_stock_api.py
└── lesson4_chatbot.py
```

---

### Câu hỏi kiểm tra cuối Giai đoạn 1

Sau khi xong, bạn phải trả lời được:
1. Token là gì? Tại sao giới hạn token quan trọng?
2. Tool Use khác gì với việc bạn tự gọi function trong code?
3. Tại sao cần lưu conversation history?
4. LLM có thể tự quyết định *không* gọi tool không? Khi nào?

---

## Giai đoạn 2 — RAG & Vector Database (3–4 tuần)

> **Mục tiêu:** Cho LLM "đọc" báo cáo tài chính PDF và trả lời câu hỏi dựa trên nội dung thực.

### Kiến thức cần học

- [ ] **Embedding là gì:** Vector representation của text
- [ ] **Semantic search:** Tìm kiếm theo nghĩa, không phải từ khóa
- [ ] **Chunking strategy:** Tại sao phải cắt nhỏ văn bản, cắt thế nào
- [ ] **ChromaDB:** Lưu và query vector locally
- [ ] **RAG pattern:** Retrieve → Augment → Generate

### Thứ phải làm (theo thứ tự)

#### Bài 5 — Đọc và xử lý PDF
- [ ] Cài PyMuPDF: `pip install pymupdf`
- [ ] Đọc báo cáo tài chính NVIDIA (download từ investor.nvidia.com)
- [ ] Extract text theo từng trang
- [ ] Implement chunking: cắt thành đoạn ~500 tokens, có overlap

**Output:** List các chunks text từ PDF.

---

#### Bài 6 — Embedding & ChromaDB
- [ ] Hiểu embedding là gì (dùng ví dụ cụ thể)
- [ ] Dùng Claude hoặc sentence-transformers tạo embedding cho chunks
- [ ] Lưu vào ChromaDB
- [ ] Query thử: *"doanh thu NVIDIA quý 3"* → trả về top 3 chunks liên quan

**Output:** Có thể tìm đoạn văn liên quan từ PDF bằng câu hỏi tự nhiên.

---

#### Bài 7 — RAG Pipeline
- [ ] Kết hợp: Query → Retrieve chunks → Đưa vào prompt → LLM trả lời
- [ ] So sánh câu trả lời khi có và không có RAG
- [ ] Xử lý trường hợp không tìm thấy thông tin liên quan

**Output:** Q&A system trả lời về nội dung báo cáo tài chính.

---

#### Bài 8 — RAG Agent
- [ ] Đóng gói RAG thành 1 tool: `query_financial_report(question)`
- [ ] Kết hợp với chatbot từ Giai đoạn 1
- [ ] LLM tự quyết định dùng stock API hay query PDF tùy câu hỏi

**Output:** Chatbot biết cả giá cổ phiếu thực lẫn nội dung báo cáo.

---

### Cấu trúc thư mục Giai đoạn 2

```
phase2/
├── data/
│   └── nvidia_annual_report_2024.pdf
├── chroma_db/            # ChromaDB lưu local
├── lesson5_pdf_parser.py
├── lesson6_embeddings.py
├── lesson7_rag_pipeline.py
└── lesson8_rag_agent.py
```

---

### Câu hỏi kiểm tra cuối Giai đoạn 2

1. Tại sao không đưa cả PDF vào prompt thay vì dùng RAG?
2. Chunk size ảnh hưởng gì đến chất lượng retrieval?
3. Semantic search khác keyword search thế nào? Cho ví dụ cụ thể.
4. Hallucination trong RAG xảy ra khi nào?

---

## Giai đoạn 3 — Multi-Agent với LangGraph (3–4 tuần)

> **Mục tiêu:** Xây hệ thống hoàn chỉnh, nhiều agent hợp tác, tạo báo cáo phân tích đầy đủ.

### Kiến thức cần học

- [ ] **LangGraph cơ bản:** Node, Edge, State, Graph
- [ ] **Agent patterns:** ReAct, Planner-Executor
- [ ] **Agent communication:** Cách agents chia sẻ state
- [ ] **Error handling trong multi-agent:** Retry, fallback
- [ ] **Prompt engineering:** System prompt cho từng agent

### Thứ phải làm (theo thứ tự)

#### Bài 9 — LangGraph cơ bản
- [ ] Hiểu khái niệm Graph: nodes là các bước xử lý, edges là luồng dữ liệu
- [ ] Xây graph đơn giản 3 nodes: Input → Process → Output
- [ ] Hiểu State: object chứa toàn bộ thông tin chạy qua graph

**Output:** Graph đơn giản chạy được, hiểu cơ chế.

---

#### Bài 10 — Các Agent chuyên biệt
- [ ] **Web Research Agent:** Tìm kiếm tin tức về cổ phiếu (dùng Tavily API hoặc DuckDuckGo)
- [ ] **Financial Data Agent:** Lấy giá, chỉ số tài chính từ Alpha Vantage
- [ ] **RAG Agent:** Query báo cáo tài chính (từ Giai đoạn 2)
- [ ] **Analysis Agent:** Tổng hợp dữ liệu, phân tích xu hướng

**Output:** 4 agents hoạt động độc lập.

---

#### Bài 11 — Orchestrator
- [ ] Orchestrator nhận câu hỏi người dùng
- [ ] Quyết định agent nào cần chạy, theo thứ tự nào
- [ ] Thu thập kết quả từ các agents
- [ ] Truyền cho Report Agent

**Output:** Orchestrator điều phối được luồng xử lý.

---

#### Bài 12 — Report Agent & Hoàn thiện
- [ ] Report Agent tổng hợp tất cả thông tin thành báo cáo có cấu trúc
- [ ] Format: Tóm tắt → Dữ liệu → Phân tích → Khuyến nghị
- [ ] Thêm error handling cho toàn hệ thống
- [ ] Test với nhiều câu hỏi khác nhau

**Output:** Hệ thống hoàn chỉnh.

---

### Cấu trúc thư mục Giai đoạn 3

```
phase3/
├── agents/
│   ├── web_research_agent.py
│   ├── financial_data_agent.py
│   ├── rag_agent.py
│   ├── analysis_agent.py
│   └── report_agent.py
├── graph/
│   ├── state.py          # Định nghĩa State
│   └── orchestrator.py   # LangGraph graph chính
└── main.py               # Entry point
```

---

### Câu hỏi kiểm tra cuối Giai đoạn 3

1. State trong LangGraph là gì? Tại sao cần nó?
2. Khi 1 agent fail, hệ thống xử lý thế nào?
3. Tại sao tách thành nhiều agent thay vì 1 agent làm tất cả?
4. Làm sao biết agent đang "hallucinate" thay vì phân tích thực?

---

## Giai đoạn 4 — Engineering & Deployment (2–3 tuần)

> **Mục tiêu:** Đóng gói hệ thống, deploy được, thêm observability. Đây là thứ phân biệt "code chạy trên máy tôi" với "sản phẩm thực sự".

> **Lưu ý:** Chỉ học những gì phù hợp với project này. Kafka, k8s, VRAM optimization là kỹ năng riêng biệt cần kinh nghiệm thực tế mới hiểu đúng — ghi vào "Học tiếp sau".

### Kiến thức cần học

- [ ] **Docker cơ bản:** Image, Container, Dockerfile, docker-compose
- [ ] **Environment management:** `.env`, secrets, config cho các môi trường khác nhau
- [ ] **Logging & Observability:** Structured logging, theo dõi agent nào chạy, mất bao lâu
- [ ] **System Design cơ bản:** Cách vẽ và giải thích kiến trúc (quan trọng cho phỏng vấn)
- [ ] **MLOps cơ bản:** Versioning prompt, tracking experiment, monitor output quality

### Thứ phải làm (theo thứ tự)

#### Bài 13 — Docker hóa ứng dụng
- [ ] Viết `Dockerfile` cho project
- [ ] Viết `docker-compose.yml` gộp app + ChromaDB
- [ ] Chạy toàn bộ hệ thống bằng 1 lệnh: `docker-compose up`
- [ ] Hiểu tại sao Docker quan trọng (reproducible environment)

**Output:** Người khác clone repo về, chạy được ngay không cần cài gì thêm.

---

#### Bài 14 — Logging & Monitoring
- [ ] Thêm structured logging vào từng agent (dùng `structlog` hoặc `loguru`)
- [ ] Log: agent nào chạy, input/output, thời gian, token dùng
- [ ] Tạo dashboard đơn giản bằng file log (không cần Grafana/Prometheus)
- [ ] Hiểu tại sao observability quan trọng trong AI system

**Output:** Nhìn vào log biết ngay hệ thống đang làm gì, tốn bao nhiêu tiền API.

---

#### Bài 15 — System Design & README
- [ ] Vẽ kiến trúc hệ thống (dùng draw.io hoặc Mermaid trong Markdown)
- [ ] Viết `README.md` chuyên nghiệp: problem, architecture, how to run, demo
- [ ] Chuẩn bị giải thích kiến trúc trong 5 phút (dùng cho phỏng vấn)

**Output:** GitHub repo đẹp, có thể demo và giải thích cho nhà tuyển dụng.

---

### Cấu trúc thư mục Giai đoạn 4

```
phase4/
├── Dockerfile
├── docker-compose.yml
├── .env.example
└── docs/
    └── architecture.md   # Sơ đồ kiến trúc + giải thích
```

---

### Câu hỏi kiểm tra cuối Giai đoạn 4

1. Docker image khác Docker container thế nào?
2. Tại sao không hardcode API key trong code?
3. Nếu hệ thống trả lời sai, bạn debug bắt đầu từ đâu?
4. Giải thích kiến trúc project này trong 5 phút cho người không biết AI.

---

## Học tiếp sau (sau khi xong project này)

> Những kỹ năng dưới đây có giá trị cao nhưng cần nền tảng thực tế mới học hiệu quả. Đừng cố học ngay — sẽ khó hiểu và dễ nản.

| Kỹ năng | Khi nào nên học | Tại sao chưa cần |
|---|---|---|
| **Apache Kafka** | Khi làm hệ thống có >1000 events/giây | Project này không có streaming real-time thực sự |
| **Kubernetes (k8s)** | Khi đã dùng Docker thành thạo 6+ tháng | k8s giải quyết vấn đề scale, chưa cần ở mức này |
| **VRAM Optimization** | Khi self-host open-source model (Llama, Mistral) | Project dùng Claude API, không cần GPU management |
| **MinIO** | Khi cần object storage distributed | Local storage + S3 đủ dùng cho level này |
| **Streaming processing** | Khi làm real-time data pipeline | Cần Kafka + Spark/Flink làm nền |
| **MLOps nâng cao** | Sau khi có model training pipeline | MLflow, Kubeflow cần context thực tế |

---

## Cấu trúc thư mục cuối cùng của project

```
Multi-Agent Research Assistant/
├── LEARNING_ROADMAP.md   ← File này
├── README.md             ← Mô tả project cho CV/GitHub
├── phase1/               ← Giai đoạn 1: LLM basics
├── phase2/               ← Giai đoạn 2: RAG & Vector DB
├── phase3/               ← Giai đoạn 3: Multi-Agent
├── phase4/               ← Giai đoạn 4: Engineering & Deploy
└── final/                ← Version hoàn chỉnh để demo
    ├── agents/
    ├── graph/
    ├── data/
    ├── chroma_db/
    ├── docs/
    ├── Dockerfile
    ├── docker-compose.yml
    ├── .env.example
    ├── requirements.txt
    └── main.py
```

---

## Checklist tiến độ tổng quan

### Giai đoạn 0 — Git & Setup
- [ ] Bước 1: Setup Git & GitHub, tạo repo, commit đầu tiên
- [ ] Bước 2: Git workflow thực tế (branch per lesson)
- [ ] Bước 3: Xử lý tình huống thực tế

### Giai đoạn 1 — LLM Basics
- [ ] Bài 1: Hello LLM
- [ ] Bài 2: Tool Use
- [ ] Bài 3: Alpha Vantage API
- [ ] Bài 4: Chatbot hoàn chỉnh

### Giai đoạn 2 — RAG & Vector DB
- [ ] Bài 5: Đọc PDF
- [ ] Bài 6: Embedding & ChromaDB
- [ ] Bài 7: RAG Pipeline
- [ ] Bài 8: RAG Agent

### Giai đoạn 3 — Multi-Agent
- [ ] Bài 9: LangGraph cơ bản
- [ ] Bài 10: Các Agent chuyên biệt
- [ ] Bài 11: Orchestrator
- [ ] Bài 12: Report Agent & Hoàn thiện

### Giai đoạn 4 — Engineering & Deploy
- [ ] Bài 13: Docker hóa ứng dụng
- [ ] Bài 14: Logging & Monitoring
- [ ] Bài 15: System Design & README

---

*Cập nhật lần cuối: 2026-06-12*
