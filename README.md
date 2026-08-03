# 🌾 DocHarvester - Web-to-Markdown Knowledge Builder

**DocHarvester**는 웹사이트의 공식 문서, 기술 블로그, 아티클을 스크래핑하여 LLM Knowledge Base(Gemini Gem, ChatGPT Custom GPTs, Claude Projects 등) 구축에 최적화된 단일 Markdown(.md) 파일로 수집·정제·통합해 주는 대시보드 웹 애플리케이션입니다.

---

## ✨ 핵심 기능

1. **🌾 직관적인 대시보드 UI (Streamlit)**
   - 대시보드 상단 1번 항목에서 타겟 URL 공통 입력
   - 수집 진행 상태 (Progress Bar & Spinner) 실시간 시각화
   - 수집 성공/실패율 및 총 글자 수 메트릭 카드 제공
   - 3가지 결과 탭: `👁️ Markdown 미리보기`, `📊 수집 상세 로그`, `📥 다운로드 및 내보내기`

2. **🔍 URL 크롤링 가능 여부 사전 진단 (Crawlability Checker)**
   - 스크래핑 실행 전 타겟 URL의 접속 가능 상태 사전 점검
   - `200 OK` 정상 접속, `403/429 Forbidden` (Cloudflare WAF 보안 방화벽), `404 Not Found`, `SSL/TLS 오류`, `비 HTML 형식` 등 불가능 사유 및 해결 팁 안내

3. **🔎 하위 링크 사전 스캔 & 최대 페이지 수 자동 추천 (Sub-links Pre-scanner)**
   - Depth 크롤링 시작 전 동일 도메인/경로 내 하위 링크 개수 사전 조사
   - **`⚡ 최대 페이지 수에 N개 즉시 반영`** 원클릭 자동 설정 지원

4. **🎯 3가지 수집 모드 지원 & 공통 URL 상태 유지**
   - **단일 페이지 (Single Page)**: 상단 타겟 URL 1개 수집
   - **멀티 페이지 (Multi Page)**: 대표 URL + 추가 URL 목록 순차 수집
   - **하위 링크 포함 (Depth Crawling)**: 시작 URL 기준 하위 링크 재귀 탐색 (Depth 1~5 지정)
   - 모드 전환 시에도 상단 입력 URL이 리셋되지 않고 상태 지속 유지

5. **📂 로컬 디렉토리 저장 경로 지정 & 다운로드**
   - 저장할 파일명(.md) 및 **로컬 저장 디렉토리 경로 (Folder Path, 기본값: `./output`)** 설정 가능
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

백엔드 스크래핑, HTML 정제, Markdown 변환, 사전 진단 및 스캔 로직을 검증합니다:

```bash
python3 -m unittest test_harvester.py -v
```

---

## 📁 프로젝트 파일 구조

```
doc_harvester/
├── app.py               # Streamlit 대시보드 메인 UI 애플리케이션
├── harvester.py         # 스크래핑, HTML 정제, MD 변환, 사전진단 백엔드 모듈
├── test_harvester.py    # 백엔드 핵심 기능 유닛 테스트 스위트 (6개 항목)
├── requirements.txt     # 프로젝트 의존성 라이브러리 목록
└── README.md            # 프로젝트 종합 사용 안내서
```
