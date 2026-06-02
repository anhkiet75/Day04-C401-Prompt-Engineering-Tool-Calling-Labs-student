# Day 04 Lab v2 Report — Research Agent

> - **PHẦN A — Giới thiệu agent**: ngắn gọn 1 trang để team khác hiểu nhanh agent có tool gì, làm được gì, thử bằng câu hỏi nào. **Xong trước 16:30**.
> - **PHẦN B — Chi tiết / Bằng chứng**: bảng đầy đủ (v0–v3, failure, eval, chat) dựa trên log thật.

## Team

- Team: Zone 3 - Team 1
- Members:   
Tiền Anh Kiệt - 2A202600961  
Nguyễn Văn Phúc - 2A202600539  
Nguyễn Quang Hoà - 2A202600986  
- Provider/model: OpenRouter (openai/gpt-4o-mini")

---

# PHẦN A — Giới thiệu agent

## A1. Agent này làm được gì

Research agent: tìm tin tức/tweet theo từ khóa hoặc tài khoản cụ thể, đọc nội dung URL, tóm tắt văn bản, tổng hợp thành digest, và gửi lên Telegram khi người dùng xác nhận. Tự hỏi lại khi thiếu thông tin (handle, URL, xác nhận gửi).

## A2. Tool agent có

| Tên tool | Làm được gì | Tool mới nhóm thêm? |
|---|---|---|
| clarify | Hỏi lại người dùng khi thiếu thông tin (handle, URL, xác nhận) | không |
| timeline | Lấy tweet gần đây của một tài khoản Twitter/X theo handle | không |
| social_search | Tìm bài đăng Twitter/X theo từ khóa (Latest hoặc Top) | không |
| lookup | Tìm kiếm web (topic: news/general, timeframe: day/week/month) | không |
| fetch | Đọc nội dung HTML của một URL cụ thể | không |
| format | Trình bày danh sách items thành markdown digest (sections/bullets/thread) | không |
| send | Gửi văn bản lên Telegram — chỉ khi confirmed=true | không |
| policy | Tìm trong tài liệu nội bộ công ty (markdown KB) | không |
| papers | Tìm bài báo khoa học trên arXiv | không |
| paper_text | Tải và trích text từ PDF arXiv | không |
| **summarize** | **Tóm tắt đoạn văn bản thành bullet points — hoàn toàn local, không cần API** | **có** |
| **sentiment** | **Phân tích cảm xúc (positive/negative/neutral) của text hoặc list bài đăng — local** | **có** |
| **extract_links** | **Trích xuất tất cả URL từ HTML đã fetch, resolve relative links — local** | **có** |

## A3. Câu hỏi mẫu để thử

**Core tools:**
1. `Tin tức AI hôm nay có gì nổi bật?`
2. `Tweet mới nhất của Sam Altman là gì?`
3. `Tóm tắt bài này giúp mình: https://openai.com/blog/gpt-5`
4. `Mọi người đang bàn gì về robotics trên Twitter?` (Latest)
5. `Đăng lên Telegram: "Bản tin AI tuần này đã sẵn sàng"` _(agent sẽ hỏi xác nhận trước)_
6. `Tìm paper về RAG mới nhất trên arXiv`

**Tool mới (nhóm tự viết):**
7. `Tóm tắt đoạn văn sau: "Artificial intelligence is transforming every industry..."` → dùng `summarize`
8. `Cảm xúc chung về AI trên Twitter hôm nay là tích cực hay tiêu cực?` → dùng `social_search` + `sentiment`
9. `Đọc bài này và lấy tất cả link bên trong: https://techcrunch.com/ai` → dùng `fetch` + `extract_links`

---

# PHẦN B — Chi tiết / Bằng chứng

## B1. Version Evidence

| Version | Changed Artifact | Hypothesis | case_accuracy before | case_accuracy after | Run File |
|---|---|---|---:|---:|---|
| v0 | baseline (prompt gốc) | Prompt gốc: "never ask, always guess, single step" | — | 0.65 | runs/v0_B_base_openrouter_20260602T124317056458.json |
| v1 | system_prompt.md | Thêm lookup arg convention (query exact, topic explicit) sẽ fix wrong_arg_value | 0.65 | 0.70 | runs/v1_B_base_openrouter_20260602T141330520585.json |
| v2 | system_prompt.md | Thêm clarify rules (handle/URL/send) + timeframe carryover sẽ fix missing_info | 0.70 | 0.80 | runs/v2_B_base_openrouter_20260602T142854678185.json |
| v3 | system_prompt.md | Thêm response_type per clarify case + explicit timeframe mapping sẽ fix remaining 4 | 0.80 | 1.00 | runs/v3_B_base_openrouter_20260602T143226647407.json |

**Metrics đầy đủ v3:** case_accuracy=1.0, tool_routing_accuracy=1.0, argument_accuracy=1.0, multiturn_accuracy=1.0

## B2. Failure Analysis (v0 baseline — 7 FAIL)

| Case ID | Failure Type | Actual Tool Calls | What Failed | Fix (version) |
|---|---|---|---|---|
| R03_web_news_routing | wrong_arg_value | lookup(query="AI news") | query thêm từ "news" thay vì giữ "AI" | v1: thêm rule "copy exact keyword" |
| R08_out_of_scope | out_of_scope | send(text="nguyên hàm x²...") | gọi send để trả lời câu toán học | v2: xóa "always pick one tool" |
| R10_missing_handle | missing_info | timeline(screenname="sama") | đoán handle thay vì hỏi | v2: thêm clarify rule cho handle mờ |
| R11_missing_url | missing_info | fetch(url="https://example.com/article") | đoán URL thay vì hỏi | v2: thêm clarify rule cho URL mờ |
| R12_confirm_before_send | wrong_boundary | send(text="Bản tin này") | gửi ngay không hỏi confirm | v2: thêm clarify rule trước send |
| R13_parallel_web_and_tweets | wrong_arg_value | lookup(query="AI news", topic=None) | query sai + topic=None | v1: lookup arg convention |
| R14_out_of_scope_coding | out_of_scope | send(text="def fibonacci...") | gọi send để trả lời câu code | v2: xóa "always pick one tool" |

**Note:** v2 fix R08/R14 như side effect của việc xóa "proactive" framing. v3 fix R10/R11/R12 bằng cách thêm `response_type` vào clarify rules và mapping "hôm nay"→`timeframe=day`.

## B3. Team Eval Cases (eval_group.json — 10 cases, 10/10 PASS)

| Case ID | Type | What It Tests | Expected Behavior | Result |
|---|---|---|---|---|
| G01_summarize_routing | single | Route đúng sang tool mới `summarize` khi user cung cấp text | summarize(text=...) | PASS |
| G02_lookup_general_not_news | single | topic=general cho câu hỏi kiến thức (không phải tin tức) | lookup(topic="general") | PASS |
| G03_out_of_scope_translation | single | Dịch thuật → không gọi tool | no_tool | PASS |
| G04_top_tweets_search_type | single | "trending" → search_type=Top | social_search(search_type="Top") | PASS |
| G05_fetch_then_summarize_boundary | single | URL đã có → fetch ngay, không summarize chưa có nội dung | fetch(url=...) | PASS |
| G06_missing_handle_then_timeline | multi | Thiếu handle → clarify → user cung cấp → timeline | clarify → timeline(screenname="karpathy") | PASS |
| G07_confirm_before_send_then_send | multi | Muốn send → clarify yes_no → user confirm → send | clarify → send(confirmed=true) | PASS |
| G08_missing_url_then_fetch | multi | Không có URL → clarify → user cung cấp → fetch | clarify → fetch(url=...) | PASS |
| G09_topic_carryover_multiturn | multi | User đổi query nhưng giữ timeframe=day và topic=news từ turn trước | lookup(timeframe="day", topic="news") | PASS |
| G10_unnecessary_tool_out_of_scope_math | single | Tính toán số học → không gọi tool | no_tool | PASS |

Run: `runs/v3_B_group_openrouter_20260602T144422866736.json`

## B4. Live Chat Evidence

Transcript: `transcripts/v3_openrouter_20260602T144639065053.transcript.json`

| Turn | User Request | Tool Calls | Behavior | Outcome |
|---|---|---|---|---|
| 1 | "Tin tức AI hôm nay có gì nổi bật?" | `lookup(query="AI", topic="news", timeframe="day")` | Route đúng, args đúng, trả kết quả tin tức | ✓ |
| 2 | "Xem tweet của người mình hay follow" | `clarify(response_type="text")` → user: "elonmusk" → `timeline(screenname="elonmusk")` | Hỏi handle trước, không đoán | ✓ |
| 3 | "Đăng bản tin này lên Telegram: 'AI là số một'" | `clarify(response_type="yes_no")` → user: "có" → `send(confirmed=true)` | Hỏi confirm trước khi gửi | ✓ |

## B5. Bonus Evidence

| Bonus | Evidence | What Worked | Guardrail |
|---|---|---|---|
| send (Telegram) | transcript turn 3 | Agent gọi clarify(yes_no) trước, chỉ gửi khi confirmed=true | send không được gọi nếu user chưa xác nhận |
| arXiv (papers/paper_text) | tools.yaml, tools/__init__.py | Đăng ký đầy đủ, có thể tìm paper theo từ khóa | — |
| policy | tools/policy/tool.py | Tìm trong company_policy/ markdown KB | Chỉ tìm nội bộ, không leak ra ngoài |
| UI (Streamlit) | starter_v0/app.py | Chat interface với tool call expander, transcript tự lưu | — |
| Tool mới: summarize | tools/summarize/ | Tóm tắt text local, không cần API key | — |
| Tool mới: sentiment | tools/sentiment/ | Phân tích positive/negative/neutral — keyword heuristic, local | — |
| Tool mới: extract_links | tools/extract_links/ | Trích xuất URL từ HTML, resolve relative links, dedup | — |

## B6. Reflection

**Fixes nào thuộc `system_prompt.md`?**
- Tất cả 3 patterns (wrong_arg, missing_clarify, out_of_scope) đều sửa trong prompt vì đây là behavioral rules, không phải tool schema.

**Fixes nào nên thuộc `tools.yaml`?**
- Có thể cải thiện description của `lookup` để gợi ý `topic` rõ hơn (v1 có thể làm vậy thay vì sửa prompt). Description tốt hơn giúp model hiểu convention mà không cần viết dài trong prompt.

**Failure nào cần review thủ công?**
- R10/R11/R12 ở v2: agent đã route đúng vào `clarify` nhưng fail vì thiếu `response_type`. Scorer chấm strict theo args — nếu không đọc log thì không biết agent thực ra đã hiểu đúng intent, chỉ thiếu 1 field.

**Nếu làm tiếp sẽ cải thiện gì?**
- Viết thêm eval case cho `papers` và `paper_text` tool (chưa có case nào test 2 tool này).
- Thêm retry logic khi provider error.
- Streamlit: thêm history persistence qua session reset.
