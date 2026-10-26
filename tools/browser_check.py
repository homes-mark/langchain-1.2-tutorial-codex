"""Optional local Chrome/Edge CDP smoke check. No remote websites/model APIs.

Requires installed Chrome/Edge and websockets (in tutorial lock). Starts headless.
Windows restricted sandboxes may require permission for local browser processes.
"""
import base64
import json
import os
from pathlib import Path
import subprocess
import time
from urllib.request import ProxyHandler, build_opener

from websockets.sync.client import connect

ROOT = Path(__file__).resolve().parents[1]
OUT = ROOT / "validation"
OUT.mkdir(exist_ok=True)
chrome = next((p for p in [
    Path(os.environ.get("PROGRAMFILES", "C:/Program Files")) / "Google/Chrome/Application/chrome.exe",
    Path(os.environ.get("PROGRAMFILES(X86)", "C:/Program Files (x86)")) / "Microsoft/Edge/Application/msedge.exe",
] if p.exists()), None)
if chrome is None:
    raise SystemExit("This optional QA script needs a locally installed Chrome/Edge on Windows.")
profile = ROOT / ".tmp" / f"browser-{int(time.time())}"
profile.mkdir(parents=True)
process = subprocess.Popen([str(chrome), "--headless=new", "--no-first-run", "--no-default-browser-check",
                            "--disable-background-networking", "--disable-component-update",
                            "--disable-extensions", "--disable-sync", "--remote-debugging-port=0",
                            f"--user-data-dir={profile}", "about:blank"],
                           stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL,
                           creationflags=getattr(subprocess, "CREATE_NO_WINDOW", 0))
events = []
try:
    port_file = profile / "DevToolsActivePort"
    for _ in range(100):
        if port_file.exists():
            break
        time.sleep(.1)
    port = int(port_file.read_text().splitlines()[0])
    opener = build_opener(ProxyHandler({}))
    targets = json.load(opener.open(f"http://127.0.0.1:{port}/json", timeout=5))
    target = next(t for t in targets if t["type"] == "page")
    with connect(target["webSocketDebuggerUrl"], proxy=None, open_timeout=5, max_size=8_000_000) as ws:
        counter = 0

        def call(method, params=None):
            global counter
            counter += 1
            ws.send(json.dumps({"id": counter, "method": method, "params": params or {}}))
            while True:
                response = json.loads(ws.recv(timeout=15))
                if response.get("id") == counter:
                    if "error" in response:
                        raise RuntimeError(response["error"])
                    return response.get("result", {})
                events.append(response)

        def js(expression):
            result = call("Runtime.evaluate", {"expression": expression, "returnByValue": True, "awaitPromise": True})
            if "exceptionDetails" in result:
                raise AssertionError(result["exceptionDetails"])
            return result.get("result", {}).get("value")

        def loaded(slug):
            for _ in range(100):
                if js(f"document.readyState === 'complete' && document.body?.dataset.slug === {json.dumps(slug)}"):
                    return
                time.sleep(.05)
            raise AssertionError(f"Navigation timeout: {slug}")

        def goto(slug, query=""):
            call("Page.navigate", {"url": (ROOT / f"{slug}.html").as_uri() + query})
            loaded(slug)

        def screenshot(name):
            js("window.scrollTo(0, 0)")
            data = call("Page.captureScreenshot", {"format": "png", "captureBeyondViewport": False})
            (OUT / name).write_bytes(base64.b64decode(data["data"]))

        call("Page.enable")
        call("Runtime.enable")
        call("Network.enable")
        call("Network.emulateNetworkConditions", {"offline": True, "latency": 0, "downloadThroughput": 0, "uploadThroughput": 0})
        call("Emulation.setDeviceMetricsOverride", {"width":1440,"height":1000,"deviceScaleFactor":1,"mobile":False})
        goto("index", "?done=")
        assert js("document.querySelectorAll('.course-nav a').length") == 22
        assert js("document.querySelector('.highlight span') !== null")
        assert js("getComputedStyle(document.querySelector('.sidebar')).position") == "fixed"
        screenshot("desktop-home.png")
        js("document.querySelector('#page-complete').click()")
        assert js("document.querySelector('#progress-text').textContent") == "1 / 22"
        js("document.querySelector('.course-nav a[data-page=\"01-setup\"]').click()")
        loaded("01-setup")
        assert js("document.querySelector('#progress-text').textContent") == "1 / 22"
        js("document.querySelector('#page-complete').click()")
        call("Page.reload")
        loaded("01-setup")
        assert js("document.querySelector('#page-complete').checked")
        js("document.querySelector('#nav-search').value='RAG'; document.querySelector('#nav-search').dispatchEvent(new Event('input'))")
        assert js("[...document.querySelectorAll('.course-nav a:not([hidden])')].every(a=>a.textContent.toLowerCase().includes('rag'))")
        # Test import using an actual File object and the input's change handler.
        js("""(async()=>{
          const dt=new DataTransfer();
          dt.items.add(new File([JSON.stringify({schema:'langchain12-cn-progress-v1',completed:['07-agents']})], 'progress.json',{type:'application/json'}));
          const input=document.querySelector('#import-progress');input.files=dt.files;input.dispatchEvent(new Event('change'));
          await new Promise(r=>setTimeout(r,100));
        })()""")
        assert js("document.querySelector('#progress-text').textContent") == "1 / 22"
        assert js("document.querySelector('.course-nav a[data-page=\"07-agents\"]').classList.contains('done')")
        download_dir = profile / "downloads"
        download_dir.mkdir()
        call("Browser.setDownloadBehavior", {"behavior":"allow", "downloadPath":str(download_dir)})
        js("document.querySelector('#export-progress').click()")
        export_path = download_dir / "langchain12-progress.json"
        for _ in range(30):
            if export_path.exists(): break
            time.sleep(.1)
        assert json.loads(export_path.read_text())["completed"] == ["07-agents"]
        # All page renderings in actual file:// + offline network mode.
        catalog = json.loads((ROOT / "assets/catalog.json").read_text(encoding="utf-8"))
        checked = []
        for page in catalog:
            goto(page["slug"])
            assert js("document.querySelectorAll('h1').length === 1 && document.querySelector('.highlight') !== null")
            assert js("document.documentElement.scrollWidth <= innerWidth + 1"), page["slug"]
            checked.append(page["slug"])
        goto("19-project-5")
        screenshot("desktop-project.png")
        call("Emulation.setDeviceMetricsOverride", {"width":390,"height":844,"deviceScaleFactor":1,"mobile":True})
        for page in catalog:
            goto(page["slug"])
            assert js("document.documentElement.scrollWidth <= innerWidth + 1"), f"mobile overflow: {page['slug']}"
        goto("index")
        assert js("getComputedStyle(document.querySelector('.sidebar')).display") == "none"
        js("document.querySelector('#menu-toggle').click()")
        assert js("document.querySelector('#menu-toggle').getAttribute('aria-expanded')") == "true"
        js("document.querySelector('#menu-toggle').click()")
        screenshot("mobile-home.png")
        # Deny persistent storage to test the documented fallback.
        blocker = call("Page.addScriptToEvaluateOnNewDocument", {"source": "Object.defineProperty(window,'localStorage',{get(){throw new Error('storage blocked')}})"})
        goto("index", "?done=")
        assert js("document.querySelector('#progress-note').textContent.includes('限制本地存储')")
        js("document.querySelector('#page-complete').click();document.querySelector('.course-nav a[data-page=\"07-agents\"]').click()")
        loaded("07-agents")
        assert js("document.querySelector('#progress-text').textContent") == "1 / 22"
        call("Page.removeScriptToEvaluateOnNewDocument", {"identifier": blocker["identifier"]})
        requests = [e["params"]["request"]["url"] for e in events if e.get("method") == "Network.requestWillBeSent"]
        remote = [url for url in requests if url.startswith(("https://", "http://"))]
        errors = [e for e in events if e.get("method") == "Runtime.exceptionThrown"]
        assert not remote, remote
        assert not errors, errors
        report = {"status":"passed", "browser":str(chrome), "network":"offline emulation; file:// pages",
                  "desktop_viewport":[1440,1000], "mobile_viewport":[390,844], "pages_each_viewport":len(checked),
                  "checks":["all 22 pages render offline", "no page overflow in both viewports", "chapter navigation",
                            "static syntax highlighting", "completion/reload", "search", "progress file import/export",
                            "mobile menu", "storage denied navigation fallback", "no remote page resource requests", "no JS exceptions"],
                  "remote_requests":remote, "javascript_errors":errors,
                  "limitations":["Chrome on Windows only; browser policies differ.", "No real model API calls."]}
        (OUT / "browser-report.json").write_text(json.dumps(report,ensure_ascii=False,indent=2),encoding="utf-8")
        print(json.dumps(report,ensure_ascii=False,indent=2))
finally:
    process.terminate()
    try:
        process.wait(timeout=10)
    except subprocess.TimeoutExpired:
        process.kill()
