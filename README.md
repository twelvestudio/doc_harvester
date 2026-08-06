# 🌾 DocHarvester - Web-to-Markdown Knowledge Builder

**DocHarvester**는 웹사이트의 공식 문서, 기술 블로그, 아티클을 스크래핑하여 LLM Knowledge Base(Gemini Gem, ChatGPT Custom GPTs, Claude Projects 등) 구축에 최적화된 단일 Markdown(.md) 파일로 수집·정제·통합해 주는 대시보드 웹 애플리케이션입니다.

---

## ✨ 핵심 기능

1. **🌾 직관적인 대시보드 UI (Streamlit)**
   - 대시보드 상단 1번 항목에서 타겟 URL 공통 입력 (URL 입력 후 엔터 시 즉시 자동 진단)
   - 수집 진행 상태 (Progress Bar & Spinner) 실시간 시각화
   - 수집 성공/실패율 및 총 글자 수 메트릭 카드 제공
   - 3가지 결과 탭: `👁️ Markdown 미리보기`, `📊 수집 상세 로그`, `📥 다운로드 및 내보내기`

2. **🔎 메인 영역 하위 링크 선별 & 패턴 필터 (Sub-link Selector & Exclude Filter)**
   - 메인 화면에 100% 폭의 넓은 인터랙티브 표(`st.data_editor`)를 배치하여 발견된 하위 링크 주소를 한눈에 확인 및 체크박스로 선택/해제
   - `login, terms, privacy, auth, pdf` 등 **자동 제외 키워드 필터**로 원치 않는 페이지 자동 걸러내기
   - 체크박스 선택 수량과 **사이드바 '최대 페이지 수'의 실시간 자동 동기화**
   - `☑️ 전체 선택` / `☐ 전체 해제` 원클릭 버튼 지원

3. **📄 Markdown 구성 옵션 (TOC & 메타데이터 온/오프)**
   - `📋 목차 (Table of Contents) 포함 여부` 선택 가능
   - `🏷️ 페이지 정보 (타이틀, Source URL, Crawl Depth) 헤더 포함 여부` 선택 가능

4. **🛠️ 커스텀 고급 설정 및 최대 상한 페이지 수 (Upper Limit) 조절**
   - 고급 네트워크 설정에서 **최대 상한 페이지 수 제한(10 ~ 1000페이지)**을 자유롭게 설정하여 대용량 크롤링 지원
   - User-Agent Header, 요청 타임아웃, 대기 시간(Delay) 커스텀 조정

5. **🔍 URL 크롤링 가능 여부 사전 진단 (Crawlability Checker)**
   - 스크래핑 실행 전 타겟 URL의 접속 가능 상태 사전 점검
   - `200 OK` 정상 접속, `403/429 Forbidden` (Cloudflare WAF 보안 방화벽), `404 Not Found`, `SSL/TLS 오류`, `비 HTML 형식` 등 불가능 사유 및 해결 팁 안내

6. **🎯 3가지 수집 모드 지원 & 공통 URL 상태 유지**
   - **단일 페이지 (Single Page)**: 상단 타겟 URL 1개 수집
   - **멀티 페이지 (Multi Page)**: 대표 URL + 추가 URL 목록 순차 수집
   - **하위 링크 포함 (Depth Crawling)**: 시작 URL 기준 하위 링크 재귀 탐색 (Depth 1~5 지정)
   - 모드 전환 시에도 상단 입력 URL이 리셋되지 않고 상태 지속 유지

7. **📂 Cross-Platform 네이티브 폴더 선택기 & 다운로드**
   - macOS (Finder / `osascript`), Windows/Linux (Tkinter / Explorer) 네이티브 폴더 선택 창(`📁 변경`) 지원
   - 수집 완료 시 지정한 로컬 디스크 경로에 `.md` 파일 자동 저장 및 브라우저 다운로드 지원

---

## 🚀 설치 및 실행 방법

### 1. 필수 패키지 설치

```bash
pip install -r requirements.txt
```

### 2. Streamlit 대시보드 실행

```bash
streamlit run app.py
```
> 실행 후 브라우저에서 `http://localhost:8501` 접속

---

## 🧪 유닛 테스트 실행 방법

백엔드 스크래핑, HTML 정제, Markdown 변환, 사전 진단 및 하위링크 필터링 로직을 검증합니다:

```bash
python3 -m unittest test_harvester.py -v
```

---

## 📁 프로젝트 파일 구조

```
doc_harvester/
├── app.py               # Streamlit 대시보드 메인 UI 애플리케이션
├── harvester.py         # 스크래핑, HTML 정제, MD 변환, 사전진단 및 하위링크 백엔드 모듈
├── test_harvester.py    # 백엔드 핵심 기능 유닛 테스트 스위트 (7개 항목)
├── requirements.txt     # 프로젝트 의존성 라이브러리 목록
└── README.md            # 프로젝트 종합 사용 안내서
```
