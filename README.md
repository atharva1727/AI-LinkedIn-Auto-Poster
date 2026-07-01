# AI-LinkedIn-Auto-Poster
Automated LinkedIn content publishing system using Python and JavaScript with profile management, session handling, workflow automation and multi-account support.


<div align="center">

# 🚀 LinkedIn Auto Poster

### AI + Automation System for Multi-Account LinkedIn Content Publishing

<img src="https://github.com/atharva1727/AI-LinkedIn-Auto-Poster/blob/main/Gemini_Generated_Image_80jjgw80jjgw80jj%20(1).png" alt="LinkedIn Auto Poster Banner" width="100%"/>

[![Python](https://img.shields.io/badge/Python-3.9%2B-3776AB?style=flat-square&logo=python&logoColor=white)](https://www.python.org/)
[![Selenium](https://img.shields.io/badge/Selenium-Automation-43B02A?style=flat-square&logo=selenium&logoColor=white)](https://www.selenium.dev/)
[![Streamlit](https://img.shields.io/badge/Streamlit-Dashboard-FF4B4B?style=flat-square&logo=streamlit&logoColor=white)](https://streamlit.io/)
[![License](https://img.shields.io/badge/License-MIT-yellow?style=flat-square)](#-license)
[![Made by](https://img.shields.io/badge/Made%20by-Atharva%20Shevate-0A66C2?style=flat-square&logo=linkedin&logoColor=white)](https://linkedin.com/in/atharva-shevate-082b602a7)

*A Python-powered automation platform that manages multiple LinkedIn profiles, persists login sessions, and publishes posts — turning a repetitive manual workflow into a single click.*

</div>

---

## 📖 Overview

**LinkedIn Auto Poster** automates content publishing across multiple LinkedIn accounts from a single terminal command. Each account is mapped to a **persistent browser profile** that stores its login session on disk, so the user logs in **once per account, ever** — every run after that reuses the saved session automatically. A Python script then drives the browser to open the post composer, type the content, and submit it.

Built to solve a simple but real problem: **manually posting to LinkedIn — especially across several accounts — is repetitive and time-consuming.**

---

## ✨ Key Features

| Feature | Description |
|---|---|
| 👤 **Multi-Profile Management** | Each LinkedIn account gets its own isolated, persistent browser profile |
| 🔐 **Persistent Sessions** | Cookies & login state are saved to disk — no repeated logins |
| 🤖 **Automated Posting** | Script opens the composer, types content, and clicks *Post* automatically |
| 🧭 **Shadow-DOM Aware** | Multi-strategy click logic reliably finds LinkedIn's Post button even inside shadow roots |
| ⚡ **Multi-Account Support** | Just type the profile name at runtime to switch accounts instantly |

---

## 🖼️ Screenshots

<p align="center">
  <img src="assets/screenshots/automation-run.png" width="48%" alt="Automation Running"/>
  <img src="assets/screenshots/post-success.png" width="48%" alt="Post Published Successfully"/>
</p>

<p align="center"><i>Automation in action (instance logs + browser session) · Post published successfully</i></p>

---

## 🛠️ Tech Stack

**Languages:** Python · JavaScript · HTML · CSS
**Core Libraries:** Selenium · WebDriver Manager · Requests
**Tools:** Git · GitHub

## 🔄 How It Works

```
 Enter Profile Name → Load Saved Session → Open Post Composer → Type Content → Click Post ✅
```

1. Run the script and enter a profile name (e.g. `Atharva`, `Sneha`, `Company`)
2. The matching persistent browser profile is launched, already logged in
3. LinkedIn's post box is opened and the content is typed in automatically
4. A multi-strategy click routine locates and clicks the **Post** button — even through shadow DOM
5. Success is confirmed directly in the terminal

---

## ⚡ Quick Start

```bash
# 1. Clone the repository
git clone https://github.com/atharva1727/linkedin-auto-poster.git
cd linkedin-auto-poster

# 2. Create & activate a virtual environment
python -m venv venv
source venv/bin/activate      # Windows: venv\Scripts\activate

# 3. Install dependencies
pip install -r requirements.txt

# 4. Run the app
python auto_post.py
```

On first run, enter the profile name — you'll be prompted to log in once, and the session will be reused for every run after that.

---

## 🔒 Security Note

Session/cookie data is stored locally and should **never** be committed to version control. Add your `data/` or session folders to `.gitignore`, and use automation responsibly within LinkedIn's Terms of Service.

---

## 🔮 Future Enhancements

AI-generated captions · Hashtag generation · Scheduled posting · Analytics dashboard · Image & video post support · Multi-platform support

---

## 👤 Author

**Atharva Shevate** — AI Engineer Intern @ IOTIOT.IN · Pune, Maharashtra

[![LinkedIn](https://img.shields.io/badge/LinkedIn-0A66C2?style=flat-square&logo=linkedin&logoColor=white)](https://linkedin.com/in/atharva-shevate-082b602a7)
[![GitHub](https://img.shields.io/badge/GitHub-181717?style=flat-square&logo=github&logoColor=white)](https://github.com/atharva1727)
[![Portfolio](https://img.shields.io/badge/Portfolio-FF5722?style=flat-square&logo=googlechrome&logoColor=white)](https://atharva1727.github.io/Atharva--Portfolio)

## 📄 License

Licensed under the **MIT License**.

<div align="center">

⭐ **If you found this useful, consider starring the repo!**

</div>
