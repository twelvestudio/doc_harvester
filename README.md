# 🌾 DocHarvester - Web-to-Markdown Knowledge Builder

DocHarvester는 웹사이트의 공식 문서, 기술 블로그, 아티클을 스크래핑하여 LLM Knowledge Base(Gemini Gem, ChatGPT Custom GPTs, Claude Projects 등) 구축에 최적화된 단일 Markdown(.md) 파일로 변환 및 통합해 주는 Streamlit 대시보드 애플리케이션입니다.

---

## ✨ 주요 기능

1. **🌾 직관적인 대시보드 UI (Streamlit)**:
   - 깔끔한 대시보드 헤더 및 사이드바 옵션 조작
   - 수집 진행 상태 (Progress Bar & Spinner) 실시간 시각화
   - 수집 결과 메트릭 카드로 수집 개수 및 글자 수 한눈에 파악

2. **🎯 3가지 수집 모드 지원**:
   - **단일 페이지 (Single Page)**: 입력한 1개 URL의 본문 수집
   - **멀티 페이지 (Multi Page)**: 여러 줄로 입력된 URL 리스트 순차 수집
   - **하위 링크 포함 (Depth Crawling)**: 시작 URL 기준 동일 도메인/경로 내 하위 링크 자동 탐색 (Depth 1~5 지정 가능)

3. **🧹 스마트 본문 정제 및 HTML-to-Markdown 변환**:
   - `<main>`, `<article>` 핵심 본문 영역 자동 탐지
   - `<script>`, `<style>`, `<nav>`, `<footer>` 등 불필요 요소 제거
   - `html2text` 엔진으로 깔끔한 Markdown 구문 변환

4. **👁️ 미리보기 & 다운로드**:
   - Markdown 렌더링 뷰 및 원본 코드 뷰 지원
   - **'Download Markdown'** 버튼으로 클릭 한 번으로 `.md` 파일 저장 (기본 파일명: `AI-Product-Studio-Handbook.md`)

---

## 🚀 설치 및 실행 방법

### 1. 필수 라이브러리 설치

```bash
pip install -r requirements.txt
```

### 2. Streamlit 대시보드 앱 실행

```bash
streamlit run app.py
```
> 브라우저 창이 자동으로 열리며 `http://localhost:8501` 접속이 가능합니다.

---

## 🧪 유닛 테스트 실행 방법

핵심 백엔드 스크래퍼 및 HTML 정제/변환 로직의 동작 상태를 검증할 수 있습니다.

```bash
python3 -m unittest test_harvester.py -v
```

---

## 📁 프로젝트 파일 구조

```
doc_harvester/
├── app.py               # Streamlit 대시보드 메인 UI 애플리케이션
├── harvester.py         # 스크래핑, HTML 정제, MD 변환 핵심 백엔드 모듈
├── test_harvester.py    # 백엔드 핵심 기능 유닛 테스트 스위트
├── requirements.txt     # 프로젝트 의존성 라이브러리 목록
└── README.md            # 프로젝트 사용 안내서
```
