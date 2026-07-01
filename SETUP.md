# ⚙️ Setup & Troubleshooting Guide

Full step-by-step installation, first-run login, and error fixes for
**LinkedIn Auto Poster**.

---

## 1. Update Ubuntu & install system packages

```bash
sudo apt update && sudo apt upgrade -y
sudo apt install -y curl jq python3 python3-pip python3-venv git nano wget
```

Verify everything installed correctly:

```bash
python3 --version
pip3 --version
curl --version
jq --version
```

## 2. Install & verify PinchTab

PinchTab is the local browser-profile manager this project automates
against. Install it per its own instructions, then verify:

```bash
which pinchtab
pinchtab --version
```

If you see `command not found`, add it to your PATH:

```bash
export PATH="$HOME/.local/bin:$PATH"
echo 'export PATH="$HOME/.local/bin:$PATH"' >> ~/.bashrc
source ~/.bashrc
which pinchtab
```

## 3. Create the project folder & virtual environment

```bash
mkdir -p ~/linkedin-poster
cd ~/linkedin-poster
python3 -m venv venv
source venv/bin/activate
```

## 4. Install the Python dependency

```bash
pip install requests
```

Verify:

```bash
pip list | grep requests
```

## 5. Start the PinchTab server

Open a **second terminal** and keep it running for the entire session:

```bash
pinchtab
# OR
./pinchtab
```

## 6. Create a profile for each LinkedIn account (one-time)

Run these against the PinchTab API (default `http://127.0.0.1:9867`):

```bash
# 1. Create the profile
curl -X POST http://127.0.0.1:9867/profiles \
     -H "Content-Type: application/json" \
     -d '{"name": "light-linkedin"}'

# 2. Confirm it was created
curl http://127.0.0.1:9867/profiles | jq

# 3. Open it in a real (visible) browser window for the one-time login
pinchtab open light-linkedin

# 4. Log in to LinkedIn manually inside that window, then close the
#    browser normally so the session (cookies) is written to disk.
```

Repeat for every account (`speed-linkedin`, `rahul-linkedin`,
`company-linkedin`, etc.) and add the matching entry to `PROFILE_MAP`
in `auto_post.py`.

## 7. Verify session persistence

```bash
pinchtab open light-linkedin
```

You should land on LinkedIn **already logged in**. Close the window
normally — do not force-kill it, or the session may not save.

## 8. Run the automation

```bash
source venv/bin/activate
python3 auto_post.py
```

```
🚀 Multi-Profile LinkedIn System

Enter profile name (Atharva/Sneha/Rahul/Company): Atharva
Enter the content you want to post:
> Excited to share my journey into AI automation!
```

---

## 🩺 Troubleshooting

### Error: `pinchtab: command not found`
**Cause:** PinchTab binary lives in `~/.local/bin`, which isn't on the default PATH.
**Fix:**
```bash
export PATH="$HOME/.local/bin:$PATH"
echo 'export PATH="$HOME/.local/bin:$PATH"' >> ~/.bashrc
source ~/.bashrc
```

### Error: `externally-managed-environment` when running pip
**Cause:** System Python blocks `pip install` outside a virtual environment.
**Fix:** Always activate the venv first:
```bash
source venv/bin/activate
pip3 install requests
```

### Error: `Connection refused` on port 9867
**Cause:** The PinchTab server isn't running.
**Fix:** Open a new terminal and run:
```bash
pinchtab
```

### Error: `404` on `/tabs/{id}/navigate`
**Cause:** The tab referenced was already closed or the instance was recycled.
**Fix:** Re-run the script — it will start a fresh instance/tab automatically.

### Error: LinkedIn redirects to the login page
**Cause:** Session cookies expired after long inactivity.
**Fix:** Repeat the one-time manual login: start the instance, open the
login page, log in manually, then stop the instance to re-save the session.

### Error: Post button click has no effect
**Cause:** LinkedIn updated its DOM/shadow-DOM structure.
**Fix:** The script already retries through 5 independent click
strategies (snapshot ref, shadow-DOM pierce, React fiber, keyboard
shortcut, selector fallback). If all 5 fail, LinkedIn's markup has
likely changed enough to need a selector update in `click_post()`.

### Error: Content not typed into the post box
**Cause:** The contenteditable box hadn't rendered yet when the script tried to type.
**Fix:** The script already polls for the editor for up to ~5 seconds
(`while (!editor && tries < 25)`); if it still fails, increase the
`tries` limit or the per-attempt delay in `type_content()`.

---

## ➕ Adding a new account

1. `curl -X POST http://127.0.0.1:9867/profiles -d '{"name": "new-linkedin"}'`
2. `curl http://127.0.0.1:9867/profiles | jq` (confirm it exists)
3. `pinchtab open new-linkedin` → log in manually → close normally
4. Add `"newkey": "new-linkedin"` to `PROFILE_MAP` in `auto_post.py`

No code changes beyond the map entry are required — the same script
handles every account.
