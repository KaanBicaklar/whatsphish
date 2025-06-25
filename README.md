# 🕵️‍♂️ WhatsPhish - WhatsApp Phishing with Selenium

**WhatsPhish** is an automated phishing framework that uses **Selenium WebDriver** to send customized messages via **WhatsApp Web**, designed for social engineering simulations, awareness campaigns, or red team engagements.

> ⚠️ For **authorized security testing and educational purposes only**.

---

## 🚀 Features

- Automates login and message delivery on WhatsApp Web
- Reads targets and messages from a CSV file (`test.csv`)
- Logs sent messages to `result.csv`
- Supports resume from the last unsent user in case of a crash
- Simple SSL certificate generation support (`cert.pem`, `key.pem`)

---

## 🛠 Requirements

- Python 3.x
- `selenium` package
- Chrome + matching `chromedriver`
- `openssl` (for optional certificate generation)

Install dependencies:

```bash
pip install selenium
