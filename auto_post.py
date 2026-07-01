#!/usr/bin/env python3
"""
LinkedIn Auto Poster — Multi-Profile LinkedIn Posting System
--------------------------------------------------------------
Automates publishing a post to LinkedIn using PinchTab's persistent
browser-profile API. Each LinkedIn account (Atharva / Sneha / Rahul /
Company, etc.) is mapped to one PinchTab profile that stores its own
cookies/login session on disk, so you only ever log in once per account.

How it works (matches the recorded flow):
  1. Ask for a profile name at runtime.
  2. Start (or reuse) the PinchTab browser instance for that profile.
  3. Open a new tab and navigate to the LinkedIn feed.
  4. Run JS inside the tab to click "Start a post" and open the composer.
  5. Type the post content using document.execCommand('insertText', ...)
     so LinkedIn's React state updates correctly.
  6. Click the Post/Submit button using a 5-strategy fallback chain,
     because LinkedIn renders that button deep inside shadow DOM and
     its structure changes often.

Requirements:
  - Python 3.9+
  - `requests` library
  - PinchTab installed & running locally (`pinchtab` command, default
    server on http://127.0.0.1:9867)

Author: Atharva Shevate
"""

import sys
import time
import json
import requests

# ----------------------------------------------------------------------
# Configuration
# ----------------------------------------------------------------------

PINCHTAB_BASE_URL = "http://127.0.0.1:9867"

# Map friendly account names to the PinchTab profile name you created.
# Add a new entry here every time you register a new LinkedIn account.
PROFILE_MAP = {
    "atharva": "light-linkedin",
    "sneha": "speed-linkedin",
    "rahul": "rahul-linkedin",
    "company": "company-linkedin",
}

LINKEDIN_FEED_URL = "https://www.linkedin.com/feed/"

REQUEST_TIMEOUT = 30


# ----------------------------------------------------------------------
# Low-level PinchTab API helper
# ----------------------------------------------------------------------

def api(method: str, path: str, payload: dict | None = None):
    """Thin wrapper around PinchTab's local REST API."""
    url = f"{PINCHTAB_BASE_URL}{path}"
    try:
        response = requests.request(
            method, url, json=payload, timeout=REQUEST_TIMEOUT
        )
        response.raise_for_status()
        if response.content:
            return response.json()
        return {}
    except requests.exceptions.ConnectionError:
        print("❌ Could not reach PinchTab. Is the server running? "
              "Start it with: pinchtab")
        sys.exit(1)
    except requests.exceptions.HTTPError as exc:
        print(f"❌ PinchTab API error on {method} {path}: {exc}")
        raise


# ----------------------------------------------------------------------
# Profile / instance management
# ----------------------------------------------------------------------

def resolve_profile_id(profile_name: str) -> str:
    """Looks up the PinchTab profile record that matches a friendly name."""
    profiles = api("GET", "/profiles")
    for profile in profiles.get("profiles", profiles if isinstance(profiles, list) else []):
        if profile.get("name") == profile_name:
            return profile.get("id")
    raise ValueError(
        f"No PinchTab profile named '{profile_name}' was found. "
        f"Create it first — see the Installation Guide."
    )


def start_instance(profile_id: str) -> dict:
    """Starts (or reuses) a persistent browser instance for a profile."""
    print("🧩 Starting instance process...")
    instance = api("POST", f"/profiles/{profile_id}/start")
    print(f"✅ Reusing instance: {instance.get('id', instance.get('instanceId'))}")
    return instance


def stop_instance(profile_id: str) -> None:
    """Stops the running instance for a profile (used to save the session)."""
    api("POST", f"/profiles/{profile_id}/stop")


def open_linkedin_tab(instance: dict) -> str:
    """Opens a fresh tab and navigates it to the LinkedIn feed."""
    tab = api("POST", f"/instances/{instance['id']}/tabs")
    tab_id = tab["id"]
    print(f"🗂️  Tab opened: {tab_id}")
    api("POST", f"/tabs/{tab_id}/navigate", {"url": LINKEDIN_FEED_URL})
    print("🌐 Opening LinkedIn...")
    time.sleep(3)
    return tab_id


def run_js(tab_id: str, script: str):
    """Executes JavaScript inside the given tab and returns the result."""
    result = api("POST", f"/tabs/{tab_id}/evaluate", {"expression": script})
    return result.get("result")


# ----------------------------------------------------------------------
# Post composer automation
# ----------------------------------------------------------------------

def open_post_box(tab_id: str) -> None:
    """Clicks the 'Start a post' button to open the composer."""
    print("📝 Opening post box...")
    script = """
    (() => {
        const candidates = Array.from(document.querySelectorAll('button, span, div'));
        const btn = candidates.find(el =>
            (el.innerText || '').trim().toLowerCase().startsWith('start a post')
        );
        if (btn) { btn.click(); return "post_box: clicked"; }
        return "post_box: not_found";
    })()
    """
    result = run_js(tab_id, script)
    print(result or "post_box: clicked")
    time.sleep(2)


def type_content(tab_id: str, content: str) -> None:
    """
    Types the post content into LinkedIn's contenteditable box.

    Uses document.execCommand('insertText', ...) instead of setting
    innerText/value directly, because LinkedIn's editor is a React
    component — execCommand fires the native input event React listens
    for, so the internal state is updated correctly.
    """
    print("⌨️  Typing content...")
    safe_content = json.dumps(content)  # safely escape for embedding in JS
    script = f"""
    (() => {{
        function getEditor() {{
            return document.querySelector('div.ql-editor[contenteditable="true"]')
                || document.querySelector('div[role="textbox"][contenteditable="true"]');
        }}
        let editor = null, tries = 0;
        while (!editor && tries < 25) {{
            editor = getEditor();
            if (!editor) {{ const s = Date.now(); while(Date.now()-s<200){{}} }}
            tries++;
        }}
        if (!editor) return "editor_not_found";
        editor.focus();
        document.execCommand('insertText', false, {safe_content});
        return "typed_success";
    }})()
    """
    result = run_js(tab_id, script)
    print("Typing:", result)
    time.sleep(4)


def click_post(tab_id: str) -> bool:
    """
    Clicks LinkedIn's Post/Submit button using a 5-strategy fallback
    chain. LinkedIn renders the button deep inside shadow DOM and
    changes its markup often, so a single selector is unreliable.
    """
    print("📤 Clicking Post button...")
    time.sleep(3)

    # --- Strategy 1: PinchTab accessibility snapshot + ref click -------
    print("🔍 Strategy 1: PinchTab snapshot ref click...")
    try:
        raw = api("GET", f"/tabs/{tab_id}/snapshot")
        snap = raw if isinstance(raw, dict) else {"children": raw if isinstance(raw, list) else []}

        def find_ref(node, depth=0):
            if not isinstance(node, dict) or depth > 30:
                return None
            name = (node.get("name") or "").strip().lower()
            label = (node.get("aria-label") or "").strip().lower()
            if name == "post" or label == "post":
                return node.get("ref")
            for child in node.get("children", []) or []:
                found = find_ref(child, depth + 1)
                if found:
                    return found
            return None

        ref = find_ref(snap)
        if ref:
            api("POST", f"/tabs/{tab_id}/click", {"ref": ref})
            print("✅ Posted via PinchTab snapshot ref click!")
            return True
        print("   Not found in snapshot.")
    except Exception as exc:
        print(f"   Strategy 1 failed: {exc}")

    # --- Strategy 2: Deep shadow-DOM search -----------------------------
    print("🔍 Strategy 2: Deep shadow DOM search...")
    shadow_search_script = """
    (() => {
        function deepQuery(root) {
            const found = [];
            const walk = (node) => {
                if (!node) return;
                if (node.querySelectorAll) {
                    node.querySelectorAll('button, [role="button"]').forEach(el => found.push(el));
                }
                const children = node.shadowRoot ? [node.shadowRoot, ...node.children]
                    : (node.children ? Array.from(node.children) : []);
                children.forEach(walk);
            };
            walk(root);
            return found;
        }
        const buttons = deepQuery(document.body);
        const target = buttons.find(b => {
            const txt = (b.innerText || b.getAttribute('aria-label') || '').trim().toLowerCase();
            return txt === 'post';
        });
        if (target) { target.click(); return "clicked_shadow_pierce"; }
        return "not_found";
    })()
    """
    result = run_js(tab_id, shadow_search_script)
    if result == "clicked_shadow_pierce":
        print("   Result: clicked_shadow_pierce")
        print("✅ Posted via shadow DOM pierce!")
        return True

    # --- Strategy 3: React Fiber internal onClick invocation -----------
    print("🔍 Strategy 3: React Fiber onClick invocation...")
    fiber_script = """
    (() => {
        function findPostBtn(root) {
            const all = root.querySelectorAll('button, [role="button"]');
            return Array.from(all).find(el => {
                const txt = (el.innerText || el.getAttribute('aria-label') || '').trim().toLowerCase();
                return txt === 'post';
            });
        }
        let btn = findPostBtn(document);
        if (!btn) return "not_found";
        const fiberKey = Object.keys(btn).find(k =>
            k.startsWith("__reactFiber") || k.startsWith("__reactInternalInstance")
        );
        if (fiberKey) {
            let fiber = btn[fiberKey];
            let depth = 0;
            while (fiber && depth < 20) {
                if (fiber.memoizedProps && fiber.memoizedProps.onClick) {
                    fiber.memoizedProps.onClick({
                        preventDefault: () => {},
                        stopPropagation: () => {}
                    });
                    return "react_fiber_clicked";
                }
                fiber = fiber.return;
                depth++;
            }
        }
        btn.click();
        return "plain_click";
    })()
    """
    result = run_js(tab_id, fiber_script)
    print(f"   Result: {result}")
    if result and result != "not_found":
        time.sleep(4)
        print("✅ Posted via React fiber!")
        return True

    # --- Strategy 4: Keyboard-driven submit (Ctrl+Enter) ----------------
    print("🔍 Strategy 4: Keyboard shortcut submit (Ctrl+Enter)...")
    try:
        api("POST", f"/tabs/{tab_id}/key", {"key": "Enter", "modifiers": ["Control"]})
        time.sleep(3)
        print("✅ Submitted via keyboard shortcut!")
        return True
    except Exception as exc:
        print(f"   Strategy 4 failed: {exc}")

    # --- Strategy 5: Generic selector list fallback ---------------------
    print("🔍 Strategy 5: Generic selector fallback...")
    fallback_script = """
    (() => {
        const selectors = [
            'button.share-actions__primary-action',
            'button[data-control-name="share.post"]',
            'button[aria-label="Post"]'
        ];
        for (const sel of selectors) {
            const el = document.querySelector(sel);
            if (el) { el.click(); return "fallback_clicked:" + sel; }
        }
        return "not_found";
    })()
    """
    result = run_js(tab_id, fallback_script)
    if result and result.startswith("fallback_clicked"):
        print(f"✅ Posted via fallback selector ({result})!")
        return True

    print("❌ All strategies failed.")
    return False


# ----------------------------------------------------------------------
# Orchestration
# ----------------------------------------------------------------------

def run(profile_key: str, content: str) -> bool:
    profile_key = profile_key.strip().lower()
    if profile_key not in PROFILE_MAP:
        print(f"❌ Unknown profile '{profile_key}'. "
              f"Available: {', '.join(PROFILE_MAP)}")
        return False

    pinchtab_profile_name = PROFILE_MAP[profile_key]
    profile_id = resolve_profile_id(pinchtab_profile_name)

    instance = start_instance(profile_id)
    tab_id = open_linkedin_tab(instance)

    open_post_box(tab_id)
    type_content(tab_id, content)
    success = click_post(tab_id)

    if success:
        print("\n✅ POST PUBLISHED SUCCESSFULLY ✅\n")
    else:
        print("\n❌ POST FAILED — see strategy logs above.\n")

    return success


def main():
    print("🚀 Multi-Profile LinkedIn System\n")
    profile_key = input(
        f"Enter profile name ({'/'.join(k.title() for k in PROFILE_MAP)}): "
    ).strip()

    content = input("Enter the content you want to post:\n> ").strip()
    if not content:
        print("❌ Post content cannot be empty.")
        sys.exit(1)

    run(profile_key, content)


if __name__ == "__main__":
    main()
