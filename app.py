import os
import sys
import time
import subprocess
import streamlit as st
from harvester import DocHarvester, DEFAULT_USER_AGENT


def select_folder_dialog(initial_dir: str = "./") -> str:
    """Open macOS native Finder folder selection dialog via osascript, or fallback to Tkinter."""
    # 1. macOS native Finder folder chooser via osascript
    if sys.platform == "darwin":
        try:
            cmd = 'POSIX path of (choose folder with prompt "DocHarvester - 저장 디렉토리 폴더 선택")'
            res = subprocess.run(
                ["osascript", "-e", cmd], capture_output=True, text=True, timeout=60
            )
            if res.returncode == 0 and res.stdout.strip():
                return res.stdout.strip().rstrip("/")
        except Exception:
            pass

    # 2. Fallback to Tkinter for Windows/Linux or fallback
    try:
        import tkinter as tk
        from tkinter import filedialog

        root = tk.Tk()
        root.withdraw()
        root.attributes("-topmost", True)
        init_path = (
            os.path.abspath(initial_dir)
            if os.path.exists(initial_dir)
            else os.path.expanduser("~")
        )
        folder_selected = filedialog.askdirectory(
            initialdir=init_path, title="DocHarvester - 저장 디렉토리 폴더 선택"
        )
        root.destroy()
        return folder_selected.rstrip("/") if folder_selected else ""
    except Exception:
        return ""


def auto_diagnose_url():
    url = st.session_state.get("target_url_input_key", "").strip()
    st.session_state.target_url = url
    if url:
        harvester_diag = DocHarvester(user_agent=DEFAULT_USER_AGENT, timeout=15)
        st.session_state.diag_result = harvester_diag.check_crawlability(url)


# -----------------------------------------------------------------------------
# Streamlit Page Config & Custom Styling
# -----------------------------------------------------------------------------
st.set_page_config(
    page_title="DocHarvester - Web-to-Markdown Knowledge Builder",
    page_icon="🌾",
    layout="wide",
    initial_sidebar_state="expanded",
)

# Custom CSS for rich dashboard UI
st.markdown(
    """
<style>
    /* Metric Card Styling */
    .metric-card {
        background-color: #f8f9fa;
        border: 1px solid #e9ecef;
        border-radius: 8px;
        padding: 16px;
        text-align: center;
        box-shadow: 0 2px 4px rgba(0,0,0,0.02);
    }
    .metric-value {
        font-size: 28px;
        font-weight: 700;
        color: #1e293b;
    }
    .metric-label {
        font-size: 13px;
        color: #64748b;
        text-transform: uppercase;
        letter-spacing: 0.5px;
    }
    
    /* Header Gradient Banner */
    .main-header {
        background: linear-gradient(135deg, #1e293b 0%, #0f172a 100%);
        color: white;
        padding: 24px;
        border-radius: 12px;
        margin-bottom: 24px;
    }
    .main-header h1 {
        color: #f8fafc !important;
        margin: 0;
        font-size: 2.2rem;
    }
    .main-header p {
        color: #94a3b8 !important;
        margin-top: 8px;
        margin-bottom: 0;
        font-size: 1.05rem;
    }

    /* Prevent sidebar button text from wrapping */
    section[data-testid="stSidebar"] button p {
        white-space: nowrap !important;
        font-size: 0.9rem !important;
    }
</style>
""",
    unsafe_allow_html=True,
)


# -----------------------------------------------------------------------------
# App State Initialization
# -----------------------------------------------------------------------------
if "harvest_results" not in st.session_state:
    st.session_state.harvest_results = None
if "combined_markdown" not in st.session_state:
    st.session_state.combined_markdown = ""
if "is_harvesting" not in st.session_state:
    st.session_state.is_harvesting = False
if "diag_result" not in st.session_state:
    st.session_state.diag_result = None
if "prescan_result" not in st.session_state:
    st.session_state.prescan_result = None
if "custom_max_pages" not in st.session_state:
    st.session_state.custom_max_pages = 20
if "target_url" not in st.session_state:
    st.session_state.target_url = ""
if "additional_urls_text" not in st.session_state:
    st.session_state.additional_urls_text = ""
if "output_dir" not in st.session_state:
    st.session_state.output_dir = "./output"
if "saved_file_path" not in st.session_state:
    st.session_state.saved_file_path = ""
if "include_toc" not in st.session_state:
    st.session_state.include_toc = True
if "include_metadata" not in st.session_state:
    st.session_state.include_metadata = True


# -----------------------------------------------------------------------------
# Main Header Banner
# -----------------------------------------------------------------------------
st.markdown(
    """
<div class="main-header">
    <h1>🌾 DocHarvester - Web-to-Markdown Knowledge Builder</h1>
    <p>웹사이트의 공식 문서 및 아티클을 스크래핑하여 LLM Knowledge Base(Gemini, ChatGPT, Claude) 구축에 최적화된 단일 Markdown(.md) 문서로 수집 및 변환합니다.</p>
</div>
""",
    unsafe_allow_html=True,
)


# -----------------------------------------------------------------------------
# Sidebar Options Panel
# -----------------------------------------------------------------------------
with st.sidebar:
    st.header("⚙️ 수집 및 설정 옵션")

    # Harvester instance for diagnosis
    harvester_diag = DocHarvester(user_agent=DEFAULT_USER_AGENT, timeout=15)

    # STEP 1: Top Shared URL Input (with auto-diagnose on Enter)
    st.subheader("1. 🔗 웹사이트 URL 입력")
    target_url_input = st.text_input(
        "타겟 URL (대표 주소)",
        value=st.session_state.target_url,
        placeholder="https://docs.example.com/guide/",
        help="URL 입력 후 엔터(Enter)를 누르면 크롤링 가능 여부가 즉시 진단됩니다.",
        key="target_url_input_key",
        on_change=auto_diagnose_url,
    )
    st.session_state.target_url = target_url_input.strip()

    # Diagnostics Button at Top
    if st.session_state.target_url:
        if st.button("🔍 크롤링 가능 여부 재진단", use_container_width=True):
            with st.spinner("웹사이트 접속 및 가능 여부 확인 중..."):
                st.session_state.diag_result = harvester_diag.check_crawlability(
                    st.session_state.target_url
                )

    # Render Diagnosis Results
    if st.session_state.diag_result:
        diag = st.session_state.diag_result
        if diag["is_scrapable"]:
            st.success(
                f"**{diag['reason']}**\n- 📌 제목: {diag['title']}\n- 📄 형식: {diag['content_type']}"
            )
        else:
            st.error(
                f"**🔴 크롤링 불가능/제한됨**\n- ⚠️ 사유: {diag['reason']}\n- 💡 팁: User-Agent 헤더 변경 또는 접근 가능한 공개 URL인지 확인하세요."
            )

    st.divider()

    # STEP 2: Scope Mode Selection
    st.subheader("2. 🎯 수집 범위 선택")
    scope_option = st.radio(
        "수집 방식 선택",
        options=[
            "단일 페이지 (Single Page)",
            "멀티 페이지 (Multi Page)",
            "하위 링크 포함 (Depth Crawling)",
        ],
        index=0,
        help="단일 URL, 여러 URL 목록, 또는 동일 도메인 내 하위 링크 탐색 수집 중 선택하세요.",
    )

    urls_to_crawl = []
    max_depth = 1
    max_pages = st.session_state.custom_max_pages

    if scope_option == "단일 페이지 (Single Page)":
        if st.session_state.target_url:
            urls_to_crawl = [st.session_state.target_url]
        else:
            st.caption("💡 상단 1번 항목에서 타겟 URL을 입력하세요.")

    elif scope_option == "멀티 페이지 (Multi Page)":
        multi_text = st.text_area(
            "추가 타겟 URL 목록 (한 줄에 하나씩)",
            value=st.session_state.additional_urls_text,
            placeholder="https://docs.example.com/page2\nhttps://docs.example.com/page3",
            height=120,
            help="상단 대표 URL 이외에 추가로 수집할 URL들을 한 줄에 1개씩 입력하세요.",
        )
        st.session_state.additional_urls_text = multi_text

        # Combine target_url and additional_text
        raw_list = []
        if st.session_state.target_url:
            raw_list.append(st.session_state.target_url)
        if multi_text.strip():
            raw_list.extend([u.strip() for u in multi_text.splitlines() if u.strip()])
        urls_to_crawl = list(dict.fromkeys(raw_list))  # deduplicate preserving order

    elif scope_option == "하위 링크 포함 (Depth Crawling)":
        if st.session_state.target_url:
            urls_to_crawl = [st.session_state.target_url]
        else:
            st.caption("💡 상단 1번 항목에서 시작 URL을 입력하세요.")

        col_d1, col_d2 = st.columns(2)
        with col_d1:
            max_depth = st.number_input(
                "탐색 깊이 (Depth)", min_value=1, max_value=5, value=1, step=1
            )
        with col_d2:
            max_pages = st.number_input(
                "최대 페이지 수",
                min_value=1,
                max_value=100,
                value=int(st.session_state.custom_max_pages),
                step=5,
            )
            st.session_state.custom_max_pages = max_pages

        if st.session_state.target_url:
            if st.button("🔎 하위링크 사전스캔", use_container_width=True):
                with st.spinner("하위 링크 개수 조사 중..."):
                    st.session_state.prescan_result = (
                        harvester_diag.quick_scan_sublinks(st.session_state.target_url)
                    )

        # Render Sublink Pre-scan Results
        if st.session_state.prescan_result:
            pscan = st.session_state.prescan_result
            if pscan["error"]:
                st.warning(f"⚠️ 하위 링크 스캔 실패: {pscan['error']}")
            else:
                st.info(
                    f"📊 **발견된 하위 링크**: **{pscan['total_count']}개** (`{pscan['base_domain']}`)"
                )
                if pscan["total_count"] > 0:
                    if st.button(
                        f"⚡ 최대 페이지 수에 {pscan['total_count']}개 즉시 반영",
                        use_container_width=True,
                    ):
                        st.session_state.custom_max_pages = min(max(int(pscan["total_count"]), 1), 100)
                        st.rerun()

    st.divider()

    # 3. Output Settings
    st.subheader("3. 📄 출력 파일 및 저장 경로 설정")

    output_filename = st.text_input(
        "저장할 파일명 (.md)",
        value="AI-Product-Studio-Handbook.md",
        help="다운로드 및 통합 생성될 Markdown 파일 이름을 지정합니다.",
    )
    if not output_filename.endswith(".md"):
        output_filename += ".md"

    col_path_text, col_path_btn = st.columns([2.6, 1.4])
    with col_path_text:
        st.markdown(f"📂 **현재 저장 폴더**:\n`{st.session_state.output_dir}`")
    with col_path_btn:
        st.write(" ")
        if st.button(
            "📁 변경",
            help="Finder / 파일 탐색기를 열어 저장할 폴더를 직접 선택합니다.",
            use_container_width=True,
        ):
            chosen = select_folder_dialog(st.session_state.output_dir)
            if chosen:
                st.session_state.output_dir = chosen
                st.rerun()

    st.markdown("**📄 Markdown 구성 옵션**")
    include_toc = st.checkbox("📋 목차 (Table of Contents) 포함", value=st.session_state.include_toc)
    include_metadata = st.checkbox("🏷️ 페이지 정보 (타이틀, Source URL, Depth) 메타데이터 포함", value=st.session_state.include_metadata)
    st.session_state.include_toc = include_toc
    st.session_state.include_metadata = include_metadata

    st.divider()

    # 4. Advanced Settings Accordion
    with st.expander("🛠️ 고급 네트워크 설정", expanded=False):
        custom_ua = st.text_input("User-Agent Header", value=DEFAULT_USER_AGENT)
        req_timeout = st.slider(
            "요청 타임아웃 (초)", min_value=5, max_value=60, value=15
        )
        req_delay = st.slider(
            "요청 간 대기 시간 (초)", min_value=0.0, max_value=3.0, value=0.5, step=0.1
        )

    st.divider()

    # 5. Run Execution Button
    run_button = st.button(
        "🌾 Harvest Docs (수집 시작)", type="primary", use_container_width=True
    )


# -----------------------------------------------------------------------------
# Main Content Area & Scraper Execution
# -----------------------------------------------------------------------------

# Handle Execution
if run_button:
    if not urls_to_crawl:
        st.error("⚠️ 수집할 URL을 입력해주세요.")
    else:
        st.session_state.is_harvesting = True
        harvester = DocHarvester(
            user_agent=custom_ua, timeout=req_timeout, delay=req_delay
        )

        progress_bar = st.progress(0)
        status_text = st.empty()

        with st.spinner("🌾 웹문서를 스크래핑하고 정제하는 중입니다..."):
            start_time = time.time()

            def update_progress(current, total, msg):
                progress = min(max(current / max(total, 1), 0.0), 1.0)
                progress_bar.progress(progress)
                status_text.info(f"⏳ {msg}")

            if scope_option == "단일 페이지 (Single Page)":
                update_progress(1, 1, f"단일 페이지 수집 중: {urls_to_crawl[0]}")
                results = [harvester.harvest_single(urls_to_crawl[0])]
                progress_bar.progress(1.0)
                status_text.success("✅ 단일 페이지 수집 완료!")

            elif scope_option == "멀티 페이지 (Multi Page)":
                results = harvester.harvest_multi(
                    urls_to_crawl, progress_callback=update_progress
                )
                status_text.success(f"✅ 총 {len(results)}개 페이지 멀티 수집 완료!")

            elif scope_option == "하위 링크 포함 (Depth Crawling)":
                results = harvester.harvest_depth(
                    start_url=urls_to_crawl[0],
                    max_depth=max_depth,
                    max_pages=max_pages,
                    progress_callback=update_progress,
                )
                status_text.success(
                    f"✅ Depth {max_depth} 탐색 완료! (총 {len(results)}개 페이지 수집)"
                )

            elapsed_time = time.time() - start_time

            # Build combined markdown
            doc_title = (
                output_filename.rsplit(".", 1)[0]
                .replace("-", " ")
                .replace("_", " ")
                .title()
            )
            combined_md = DocHarvester.build_combined_markdown(
                results,
                document_title=doc_title,
                include_toc=st.session_state.include_toc,
                include_metadata=st.session_state.include_metadata,
            )

            # Auto-save to specified local directory
            save_directory = os.path.abspath(st.session_state.output_dir)
            os.makedirs(save_directory, exist_ok=True)
            full_saved_path = os.path.join(save_directory, output_filename)

            with open(full_saved_path, "w", encoding="utf-8") as f:
                f.write(combined_md)

            # Store in session state
            st.session_state.harvest_results = results
            st.session_state.combined_markdown = combined_md
            st.session_state.saved_file_path = full_saved_path
            st.session_state.is_harvesting = False

            st.toast(
                f"🎉 수집 완료 및 파일 저장 성공! ({elapsed_time:.1f}초 소요)",
                icon="🎉",
            )

# -----------------------------------------------------------------------------
# Results Display Dashboard
# -----------------------------------------------------------------------------
if st.session_state.harvest_results:
    results = st.session_state.harvest_results
    combined_md = st.session_state.combined_markdown

    st.subheader("📊 수집 현황 메트릭")

    total_pages = len(results)
    success_pages = sum(1 for r in results if r["status"] == "Success")
    failed_pages = total_pages - success_pages
    total_chars = len(combined_md)

    col1, col2, col3, col4 = st.columns(4)
    with col1:
        st.metric("총 요청 URL", f"{total_pages}개")
    with col2:
        st.metric(
            "수집 성공 페이지",
            f"{success_pages}개",
            delta=f"{success_pages/total_pages*100:.0f}%" if total_pages else None,
        )
    with col3:
        st.metric("수집 실패 페이지", f"{failed_pages}개", delta_color="inverse")
    with col4:
        st.metric("총 글자 수 (Chars)", f"{total_chars:,}자")

    st.markdown("---")

    # Tabs for Preview, Download, and Detailed Logs
    tab_preview, tab_logs, tab_export = st.tabs(
        ["👁️ Markdown 미리보기", "📊 수집 상세 로그", "📥 다운로드 및 내보내기"]
    )

    # --- TAB 1: PREVIEW ---
    with tab_preview:
        st.subheader("📖 통합 Markdown 문서 미리보기")

        view_mode = st.radio(
            "보기 모드",
            ["렌더링 뷰 (Rendered)", "원본 코드 뷰 (Raw Source)"],
            horizontal=True,
        )

        if view_mode == "렌더링 뷰 (Rendered)":
            st.markdown(combined_md, unsafe_allow_html=True)
        else:
            st.code(combined_md, language="markdown")

    # --- TAB 2: LOGS ---
    with tab_logs:
        st.subheader("📋 수집 페이지 결과 데이터")

        if results:
            # Format display records using native Python dictionaries
            display_records = []
            for r in results:
                record = {
                    "status": r.get("status"),
                    "depth": r.get("depth", "-"),
                    "title": r.get("title"),
                    "url": r.get("url"),
                    "char_count": r.get("char_count"),
                    "status_code": r.get("status_code"),
                    "error": r.get("error") or "-",
                }
                display_records.append(record)

            try:
                st.dataframe(
                    display_records,
                    column_config={
                        "status": st.column_config.TextColumn(
                            "상태", help="Success / Failed"
                        ),
                        "depth": st.column_config.TextColumn("Depth"),
                        "title": st.column_config.TextColumn("페이지 제목"),
                        "url": st.column_config.LinkColumn("URL"),
                        "char_count": st.column_config.NumberColumn(
                            "글자 수", format="%d 자"
                        ),
                        "status_code": st.column_config.NumberColumn("HTTP Status"),
                        "error": st.column_config.TextColumn("에러 메시지"),
                    },
                    use_container_width=True,
                    hide_index=True,
                )
            except Exception:
                st.table(display_records)

    # --- TAB 3: DOWNLOAD ---
    with tab_export:
        st.subheader("📥 Markdown 파일 저장 및 다운로드")
        if st.session_state.saved_file_path:
            st.success(
                f"💾 **로컬 디스크에 자동으로 저장되었습니다**:\n`{st.session_state.saved_file_path}`"
            )

        st.info(
            f"💡 생성된 **`{output_filename}`** 파일은 웹 브라우저에서 직접 다운로드받거나 위의 로컬 디스크 저장 경로에서 바로 확인하여 LLM Knowledge Base로 활용하실 수 있습니다."
        )

        st.download_button(
            label=f"📥 {output_filename} 다운로드",
            data=combined_md,
            file_name=output_filename,
            mime="text/markdown",
            type="primary",
            use_container_width=True,
        )

else:
    if not st.session_state.is_harvesting:
        st.info(
            "👈 좌측 사이드바에서 타겟 URL을 입력하고 **'🌾 Harvest Docs (수집 시작)'** 버튼을 눌러 스크래핑을 시작하세요."
        )
