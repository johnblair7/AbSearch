from __future__ import annotations

from contextlib import asynccontextmanager
from typing import Optional

from playwright.sync_api import sync_playwright


def fetch_html(url: str, wait_selector: Optional[str] = None, timeout_ms: int = 20000) -> str:
	with sync_playwright() as p:
		browser = p.chromium.launch(headless=True)
		try:
			context = browser.new_context()
			page = context.new_page()
			page.set_default_timeout(timeout_ms)
			page.goto(url)
			if wait_selector:
				try:
					page.wait_for_selector(wait_selector, state="visible", timeout=timeout_ms)
				except Exception:
					pass
			return page.content()
		finally:
			browser.close()
