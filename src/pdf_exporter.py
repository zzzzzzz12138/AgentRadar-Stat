from __future__ import annotations

from pathlib import Path
import shutil
import subprocess
from typing import Any

from .utils import project_path


def export_report_pdf(
    html_path: str | Path = "outputs/reports/agent_radar_report.html",
    pdf_path: str | Path = "outputs/reports/agent_radar_report.pdf",
) -> dict[str, Any]:
    """Try to export the showcase HTML report to PDF without blocking the pipeline."""
    source = project_path(str(html_path))
    target = project_path(str(pdf_path))
    render_target = target if target.stem.endswith("_latest") else target.with_name(f"{target.stem}_latest{target.suffix}")
    if not source.exists():
        return {"pdf_generated": False, "report_pdf_path": str(target), "pdf_warning": f"HTML report not found: {source}"}
    target.parent.mkdir(parents=True, exist_ok=True)
    playwright_error = ""
    try:
        from playwright.sync_api import sync_playwright  # type: ignore
    except Exception as exc:  # noqa: BLE001
        playwright_error = str(exc)
    else:
        try:
            with sync_playwright() as playwright:
                browser = playwright.chromium.launch(headless=True)
                page = browser.new_page(viewport={"width": 1440, "height": 1100}, device_scale_factor=1)
                page.goto(source.resolve().as_uri(), wait_until="networkidle")
                page.emulate_media(media="print")
                page.pdf(path=str(render_target), format="A4", print_background=True, margin={"top": "12mm", "right": "10mm", "bottom": "12mm", "left": "10mm"})
                browser.close()
        except Exception as exc:  # noqa: BLE001
            playwright_error = str(exc)
        else:
            return _promote_pdf(render_target, target)

    browser = _find_browser()
    if browser:
        try:
            result = subprocess.run(
                [
                    browser,
                    "--headless",
                    "--disable-gpu",
                    "--no-sandbox",
                    "--print-to-pdf-no-header",
                    "--no-pdf-header-footer",
                    f"--print-to-pdf={render_target}",
                    source.resolve().as_uri(),
                ],
                capture_output=True,
                text=True,
                encoding="utf-8",
                errors="replace",
                timeout=120,
                check=False,
            )
            if render_target.exists() and render_target.stat().st_size > 0 and result.returncode == 0:
                return _promote_pdf(render_target, target)
            browser_error = (result.stderr or result.stdout or f"browser exit code {result.returncode}")[:500]
        except Exception as exc:  # noqa: BLE001
            browser_error = str(exc)
    else:
        browser_error = "No Edge or Chrome executable found."

    return {
        "pdf_generated": False,
        "report_pdf_path": str(target),
        "pdf_warning": (
            "PDF export failed. Install Playwright with "
            "`python -m pip install playwright` and `python -m playwright install chromium`, "
            "or install Microsoft Edge/Google Chrome for headless PDF export. "
            f"Playwright error: {playwright_error or 'not attempted'}; browser fallback: {browser_error}"
        ),
    }


def _find_browser() -> str | None:
    candidates = [
        shutil.which("msedge"),
        shutil.which("chrome"),
        shutil.which("google-chrome"),
        r"C:\Program Files (x86)\Microsoft\Edge\Application\msedge.exe",
        r"C:\Program Files\Microsoft\Edge\Application\msedge.exe",
        r"C:\Program Files\Google\Chrome\Application\chrome.exe",
        r"C:\Program Files (x86)\Google\Chrome\Application\chrome.exe",
    ]
    for candidate in candidates:
        if candidate and Path(candidate).exists():
            return str(candidate)
    return None


def _promote_pdf(render_target: Path, target: Path) -> dict[str, Any]:
    """Move a freshly rendered PDF into the canonical path when it is not locked."""
    if render_target == target:
        return {"pdf_generated": True, "report_pdf_path": str(target), "pdf_warning": ""}
    try:
        shutil.copyfile(render_target, target)
    except OSError as exc:
        return {
            "pdf_generated": True,
            "report_pdf_path": str(render_target),
            "pdf_warning": (
                f"PDF generated at {render_target}, but the canonical file {target} "
                f"could not be replaced because it is locked by another process: {exc}"
            ),
        }
    return {"pdf_generated": True, "report_pdf_path": str(target), "pdf_warning": ""}
