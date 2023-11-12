import tkinter as tk
from tkinter import ttk
from tkinter import messagebox
import psycopg2
from tkinter import filedialog
from PyPDF2 import PdfFileReader
import os
from PyPDF2 import PdfFileReader
from pdf2image import convert_from_path
import re
import pytesseract
pytesseract.pytesseract.tesseract_cmd = r'C:\Program Files\Tesseract-OCR\tesseract.exe'

def db_connect():
    hostname = 'localhost'
    database = 'demo'
    username = 'postgres'
    pwd = '12345'
    port_id = 5432

    try:
        conn = psycopg2.connect(
            host=hostname,
            dbname=database,
            user=username,
            password=pwd,
            port=port_id)
        return conn
    except Exception as error:
        print(error)
        return None

def login(username, password, user_type):
    conn = db_connect()
    if conn is not None:
        cursor = conn.cursor()
        query = f"SELECT * FROM kullanicilar WHERE kullanici_adi = '{username}' AND sifre = '{password}' AND kullanici_turu = '{user_type}'"
        cursor.execute(query)
        user = cursor.fetchone()
        cursor.close()
        conn.close()

        if user:
            if user_type == 'Yönetici':
                admin_panel()
            elif user_type == 'Öğrenci':
                student_panel()
            elif user_type == 'Hoca':
                teacher_panel(username)
        else:
            print("Giriş başarısız, lütfen bilgilerinizi kontrol edin.")


remaining_time_minutes = 0  # Dakika cinsinden süre
remaining_time_seconds = 0  # Saniye cinsinden süre

def check_time():
    global remaining_time_minutes, remaining_time_seconds
    if remaining_time_minutes > 0 or remaining_time_seconds > 0:
        if remaining_time_seconds == 0:
            remaining_time_minutes -= 1
            remaining_time_seconds = 59
        else:
            remaining_time_seconds -= 1

        root.after(1000, check_time) 

        if student_window is not None:
            student_window.title(f"Öğrenci Paneli - Kalan Süre: {remaining_time_minutes} dakika {remaining_time_seconds} saniye")
    else:
        if student_window is not None:
            student_window.destroy()
            print("Süre doldu, öğrenci paneli kapatıldı.")
            
            

def admin_panel():
    admin_window = tk.Toplevel(root)
    admin_window.title("Yönetici Paneli")
    admin_window.geometry("400x300")  
   
    title_label = tk.Label(admin_window, text="Yönetici Paneli", font=("Helvetica", 10, "bold"), bg="yellow")
    title_label.pack()
    
    label = tk.Label(admin_window, text="Süre Ayarı (dakika):",bg="yellow")
    label.pack()
    entry = tk.Entry(admin_window)
    entry.pack()
    admin_window.config(bg="yellow") 
    def set_time():
        global remaining_time_minutes
        remaining_time_minutes = int(entry.get())
        print(f"Süre ayarlandı: {remaining_time_minutes} dakika")

    button = tk.Button(admin_window, text="Süre Ayarla", command=set_time)
    button.pack()
    

    request_limit_label = tk.Label(admin_window, text="Ders Başı Talep Sınırlaması",bg="yellow")
    request_limit_label.pack()
    request_limit_entry = tk.Entry(admin_window)
    request_limit_entry.pack()

    def set_request_limit():
        global admin_request_limit_per_course
        admin_request_limit_per_course = int(request_limit_entry.get())
        print(f"Yönetici tarafından belirlenen ders başına talep sınırlaması: {admin_request_limit_per_course}")
        

    request_limit_button = tk.Button(admin_window, text="Sınırlamayı Kaydet", command=set_request_limit)
    request_limit_button.pack()
    

    character_limit_label = tk.Label(admin_window, text="Mesaj Karakter Sınırını Belirle",bg="yellow")
    character_limit_label.pack()
    character_limit_entry = tk.Entry(admin_window)
    character_limit_entry.pack()

    def set_character_limit():
        global character_limit
        character_limit = int(character_limit_entry.get())
        print(f"Mesaj karakter sınırı: {character_limit}")
        
    character_limit_button = tk.Button(admin_window, text="Mesaj Karakter Sınırlaması :", command=set_character_limit)
    character_limit_button.pack()
    
    
    def list_users():
        user_listbox = tk.Listbox(admin_window)
        conn = db_connect()
        if conn is not None:
            cursor = conn.cursor()
            sql_komut = "SELECT kullanici_adi, kullanici_turu FROM kullanicilar"
            cursor.execute(sql_komut)
            kullanicilar = cursor.fetchall()
            cursor.close()
            conn.close()

            if kullanicilar:
                
                for kullanici in kullanicilar:
                    kullanici_adi = kullanici[0]
                    kullanici_turu = kullanici[1]
                    user_listbox.insert(tk.END, f"{kullanici_adi} ({kullanici_turu})")
                user_listbox.pack()
            else:
                messagebox.showinfo("Bilgi", "Kullanıcılar bulunmuyor.")


        def update_user_data():
            selected_user = user_listbox.get(user_listbox.curselection())
            if selected_user:
                user_info = selected_user.split(" (")
                user_name = user_info[0]
                user_type = user_info[1][:-1]  

      
                conn = db_connect()
                if conn is not None:
                    cursor = conn.cursor()
                    sql_komut = "SELECT * FROM kullanicilar WHERE kullanici_adi = %s AND kullanici_turu = %s"
                    cursor.execute(sql_komut, (user_name, user_type))
                    user_data = cursor.fetchone()
                    cursor.close()
                    conn.close()

                    if user_data:
                
                        user_update_window = tk.Toplevel(admin_window)
                        user_update_window.title("Kullanıcı Bilgilerini Güncelle")

                

                        user_name_label = tk.Label(user_update_window, text="Kullanıcı Adı:")
                        user_name_label.pack()
                        user_name_entry = tk.Entry(user_update_window)
                        user_name_entry.insert(0, user_data[0])  # Kullanıcı adını yerleştirin
                        user_name_entry.pack()
                        # Şifre alanını ekleyin
                        password_label = tk.Label(user_update_window, text="Şifre:")
                        password_label.pack()
                        password_entry = tk.Entry(user_update_window)  
                        password_entry.insert(0, user_data[1])  
                        password_entry.pack()


                        user_type_label = tk.Label(user_update_window, text="Kullanıcı Türü:")
                        user_type_label.pack()
                        user_type_entry = tk.Entry(user_update_window)
                        user_type_entry.insert(0, user_data[2])
                        user_type_entry.pack()
                

                        def update_user_data():
                            new_user_name = user_name_entry.get()
                            new_password = password_entry.get()
                            new_user_type = user_type_entry.get()

                            conn = db_connect()
                            if conn is not None:
                                cursor = conn.cursor()
                                sql_komut = "UPDATE kullanicilar SET kullanici_adi = %s, sifre = %s, kullanici_turu = %s WHERE kullanici_adi = %s AND kullanici_turu = %s"
                                sql_komut2="UPDATE dersler SET kullanici_adi=%s WHERE kullanici_adi=%s"
                                sql_komut3="UPDATE hoca_ilgi_alanlari SET kullanici_adi=%s WHERE kullanici_adi=%s"
                                sql_komut4="UPDATE hocalar SET kullanici_adi=%s WHERE kullanici_adi=%s"
                                sql_komut5="UPDATE ilgi_alanlari SET kullanici_adi=%s WHERE kullanici_adi=%s"
                                sql_komut6="UPDATE mesajlar SET ogrenci_adi=%s WHERE ogrenci_adi=%s"
                                sql_komut7="UPDATE ogrenciler SET kullanici_adi=%s WHERE kullanici_adi=%s"
                                
                                cursor.execute(sql_komut, (new_user_name, new_password, new_user_type, user_name, user_data[2]))
                                cursor.execute(sql_komut2,(new_user_name,user_name))
                                cursor.execute(sql_komut3,(new_user_name,user_name))
                                cursor.execute(sql_komut4,(new_user_name,user_name))
                                cursor.execute(sql_komut5,(new_user_name,user_name))
                                cursor.execute(sql_komut6,(new_user_name,user_name))
                                cursor.execute(sql_komut7,(new_user_name,user_name))

                                conn.commit()
                                cursor.close()
                                conn.close()
                                user_update_window.destroy()

                        update_button = tk.Button(user_update_window, text="Güncelle", command=update_user_data)
                        update_button.pack()

                    else:
                        messagebox.showinfo("Bilgi", "Kullanıcı bilgileri bulunamadı.")
                else:
                    messagebox.showerror("Hata", "Veritabanı bağlantısı kurulamadı.")
            else:
                messagebox.showinfo("Bilgi", "Kullanıcı seçilmedi.")

        def delete_user():
            selected_user = user_listbox.get(user_listbox.curselection())
            if selected_user:
                user_info = selected_user.split(" (")
                user_name = user_info[0]
                user_type = user_info[1][:-1] 

                conn = db_connect()
                if conn is not None:
                    cursor = conn.cursor()

                    
                    sql_komut2 = "DELETE FROM mesajlar WHERE ogrenci_adi = %s"
                    cursor.execute(sql_komut2, (user_name,))
                    
                    sql_komut3="DELETE FROM hoca_ilgi_alanlari WHERE kullanici_adi = %s"
                    cursor.execute(sql_komut3, (user_name,))
                    sql_komut4 = "DELETE FROM dersler WHERE kullanici_adi = %s"
                    cursor.execute(sql_komut4, (user_name,))
                    
                    sql_komut5 = "DELETE FROM  ilgi_alanlari WHERE kullanici_adi = %s"
                    cursor.execute(sql_komut5, (user_name,))
                    sql_komut6 = "DELETE FROM  hocalar WHERE kullanici_adi = %s"
                    cursor.execute(sql_komut6, (user_name,))
                    sql_komut7= "DELETE FROM kullanicilar WHERE kullanici_adi = %s AND kullanici_turu = %s"
                    
                    cursor.execute(sql_komut7, (user_name, user_type))
                    
                    conn.commit()
                    cursor.close()
                    conn.close()
                    selected_index = user_listbox.curselection()
                    if selected_index:
                        user_listbox.delete(selected_index)
                    
                    messagebox.showinfo("Başarılı", "Kullanıcı başarıyla silindi.")
                    
                else:
                    messagebox.showerror("Hata", "Veritabanı bağlantısı kurulamadı.")
            else:
                messagebox.showinfo("Bilgi", "Kullanıcı seçilmedi.")


        update_user_button = tk.Button(admin_window, text="Kullanıcıyı Güncelle", command=update_user_data)
        update_user_button.pack()


        delete_user_button = tk.Button(admin_window, text="Kullanıcıyı Sil", command=delete_user)
        delete_user_button.pack()
       
    list_users_button = tk.Button(admin_window, text="Kullanıcıları Listele", command=list_users)
    list_users_button.pack()
    
       
student_window = None




def select_and_upload_pdf():
    file_path = filedialog.askopenfilename(filetypes=[("PDF files", "*.pdf")])

    if file_path:
        images = convert_from_path(file_path)

        ocr_text = ""
        for image in images:
            text = pytesseract.image_to_string(image)
            ocr_text += text

        
        with open("ocr_metni.txt", "w", encoding="utf-8") as text_file:
            text_file.write(ocr_text)
        print(ocr_text)

        pattern = r"([A-Z]{3}\d{3})\s+([\w\s]+)\s+(\d+)\s+([A-F]{2})"

        matches = re.findall(pattern, ocr_text)


        for match in matches:
            print(f"Ders Kodu: {match[0]}, Ders Adı: {match[1]}, Kredi: {match[2]}, Notu: {match[3]}")

    kullanici_adi = username_entry.get()  


    save_course_info(matches, kullanici_adi)
    

def get_course_info(username):
    conn = db_connect()
    if conn is not None:
        cursor = conn.cursor()
        query = f"SELECT ders_kodu, ders_adi, ders_kredi, ders_notu FROM dersler WHERE kullanici_adi = '{username}'"
        cursor.execute(query)
        courses = cursor.fetchall()
        cursor.close()
        conn.close()
        return courses
    
   

def save_course_info(matches, kullanici_adi):
    conn = db_connect()
    if conn is not None:
        cursor = conn.cursor()
        for match in matches:
        
            course_code = match[0]
            course_name = match[1]
            course_credit = match[2]
            course_grade = match[3]

            
            insert_query = "INSERT INTO dersler (kullanici_adi, ders_kodu, ders_adi, ders_kredi, ders_notu) VALUES (%s, %s, %s, %s, %s)"
            cursor.execute(insert_query, (kullanici_adi, course_code, course_name, course_credit, course_grade))
        
        conn.commit()
        conn.close()
        print("Ders bilgileri veritabanına kaydedildi.")
    else:
        print("Veritabanı bağlantı hatası.")



def student_panel(): 
    global student_window
    student_window = tk.Toplevel(root)
    student_window.title("Öğrenci Paneli")
    student_window.config(bg="pink")
    
    check_time() 
    select_pdf_button = tk.Button(student_window, text="PDF Dosyası Seç ve Yükle", command=select_and_upload_pdf)
    select_pdf_button.pack()
    global result_label
    result_label = tk.Label(student_window, text="",)
    result_label.pack()
    username=username_entry.get() 
    courses = get_course_info(username)
    table = tk.Frame(student_window)
    table.pack()

    
    table = ttk.Treeview(student_window, columns=("Ders Kodu", "Ders Adı", "Kredi", "Not"))
    table.heading("#1", text="Ders Kodu")
    table.heading("#2", text="Ders Adı")
    table.heading("#3", text="Kredi")
    table.heading("#4", text="Not")
    table.pack()

    for course in courses:
        table.insert("", "end", values=course)
        
        
        
    show_interests_button = tk.Button(student_window, text="Hocaların ilgi alanlarını göster.", command=show_interests,bg="pink")
    show_interests_button.place(relx=1, rely=0, anchor="ne")

    


    interest_label = tk.Label(student_window, text="İlgi Alanlarınızı Listeden Seçin:")
    interest_label.pack()
    interest_listbox = tk.Listbox(student_window, selectmode=tk.MULTIPLE)
    interest_listbox.pack()
    interests = ["Veri Madenciliği", "Web Tasarımı", "Mobil Programlama", "Oyun Programlama","Veri Tabanları","Doğal Dil İşleme", "Web Programlama", "Bilgisayar Bilimleri", "Algoritma Çözümleme",
                    "İngilizce", "Veri Tabanı Yönetimi", "Sayısal Yöntemler",
                        "Edebiyat", "Programlama", "Görüntü İşleme", "Makine Öğrenmesi", "Yapay Zeka", "Araştırma Problemleri", 
                            "Yazılım Mühendisliği", "Otomata Teorisi", "İşletim Sistemleri", "Programlama Laboratuvarı", "Yazılım Laboratuvarı", "Web Uygulamaları", "İşaret ve Sistemler", "Matematik", "Fizik", "Kimya"]
    for interest in interests:
        interest_listbox.insert(tk.END, interest)

    
    course_label = tk.Label(student_window, text="Almak İstediğiniz Ders Kodunu Girin:")
    course_label.pack()
    course_entry = tk.Entry(student_window)
    course_entry.pack()

    def list_teachers():
        global course_code
        global student_username
        conn = db_connect()
        if conn is not None:
            cursor = conn.cursor()
            selected_interests = [interest_listbox.get(i) for i in interest_listbox.curselection()]
            selected_interests = [f"'{interest}'" for interest in selected_interests]
            course_code = course_entry.get()
            query = f"SELECT kullanici_adi FROM hoca_ilgi_alanlari WHERE ilgi_alani IN ({', '.join(selected_interests)}) AND ders_kodu='{course_code}'"

            cursor.execute(query)
            teachers = cursor.fetchall()
            cursor.close()
            conn.close()
        else:
            print("Veritabanı bağlantı hatası.")
        teacher_listbox.delete(0, tk.END) 
        for teacher in teachers:
            teacher_listbox.insert(tk.END, teacher[0])
        print("Hocalar listelendi.")
    
    list_button = tk.Button(student_window, text="Hocaları Listele", command=list_teachers)
    list_button.pack()

    
    def open_requests_page():
    
        global requests_list 
        requests_window = tk.Toplevel(student_window)
        requests_window.title("Talep Yönetimi")

 
        requests_list = tk.Listbox(requests_window)
        requests_list.pack()

        student_label = tk.Label(requests_window, text="Öğrenci Adı:")
        student_label.pack()
        student_entry = tk.Entry(requests_window)
        student_entry.pack()
        
        
        teacher_label = tk.Label(requests_window, text="Hoca Adı:")
        teacher_label.pack()
        teacher_entry = tk.Entry(requests_window)
        teacher_entry.pack()
        course_label = tk.Label(requests_window, text="Ders Kodu:")
        course_label.pack()
        course_entry = tk.Entry(requests_window)
        course_entry.pack()
        
        
        message_label = tk.Label(requests_window, text="Hoca'ya İletmek İstediğiniz Mesajı Girin:")
        message_label.pack()
        message_entry = tk.Entry(requests_window)
        message_entry.pack()

        error_message = tk.Toplevel(requests_window)
        error_message.title("Hata Mesajı")
        error_message.withdraw() 

        def show_error_message(error_text):
            error_message.deiconify()  
            error_label = tk.Label(error_message, text=error_text)
            error_label.pack()
    
        

        def create_request():       
            course_code = course_entry.get()
            teacher_name = teacher_entry.get()
            student_username = student_entry.get()
            message = message_entry.get()  
            
            if len(message) >character_limit:
                error_text = f"Hata:İletiniz {character_limit} karakteri aştı."
                print(f"Hata: Mesaj {character_limit} karakteri aşmamalıdır.")
                show_error_message(error_text)
                return
            
           
            request = f"{student_username}, {teacher_name}, {course_code}, {message}"
            requests_list.insert(tk.END, request)

            conn = db_connect()
            if conn is not None:
                cursor = conn.cursor()
                insert_query = "INSERT INTO mesajlar (ogrenci_adi, hoca_adi, ders_kodu, talep_mesaji, talep_durumu) VALUES (%s, %s, %s, %s, %s)"
                cursor.execute(insert_query, (student_username, teacher_name, course_code, message, "Beklemede"))
                conn.commit()
                cursor.close()
                conn.close()
                print("Talep başarıyla oluşturuldu.")
            else:
                print("Veritabanı bağlantı hatası.")

        create_request_button = tk.Button(requests_window, text="Talep Oluştur", command=create_request)
        create_request_button.pack()
    
        def cancel_request():
            selected_index = requests_list.curselection()
            if selected_index:
                selected_index = selected_index[0]
        
                selected_request = requests_list.get(selected_index)
                requests_list.delete(selected_index)

       
                conn = db_connect()
                if conn is not None:
                    cursor = conn.cursor()
           
                    cancel_query = "DELETE FROM mesajlar WHERE ogrenci_adi = %s AND hoca_adi = %s AND ders_kodu = %s AND talep_mesaji=%s AND talep_durumu = %s"
                    parts = selected_request.split(", ")
                    if len(parts) == 4:
                        student_username,teacher_name,course_code,message= parts
                        talep_durumu = "Beklemede"
                        cursor.execute(cancel_query, (student_username,teacher_name, course_code,message,talep_durumu ))
                        conn.commit()
                        cursor.close()
                        conn.close()

                        print("Talep başarıyla iptal edildi.")
                    
                    else:
                        print("Telep iptal edilemedi:Geçersiz")
                else:
                    print("Veritabanı bağlantı hatası")
            else:
                print("Talep seçilemedi.")
        
        cancel_request_button = tk.Button(requests_window, text="Talebi İptal Et", command=lambda: cancel_request())

        cancel_request_button.pack()

    manage_requests_button = tk.Button(student_window, text="Talepleri Yönet", command=open_requests_page)
    manage_requests_button.pack()



 
    teacher_listbox = tk.Listbox(student_window)
    teacher_listbox.pack()
    
    message_label = tk.Label(student_window, text="Hocaya İletmek İstediğiniz Mesajı Girin:")
    message_label.pack()
    
    message_entry = tk.Entry(student_window)
    message_entry.pack()

    
    def send_request():
 
        global course_code

        conn = db_connect()
        if conn is not None:
            cursor = conn.cursor()
            selected_teacher = teacher_listbox.get(teacher_listbox.curselection()[0])
            message = message_entry.get()
            query = f"INSERT INTO talepler (ogrenci_adi, hoca_adi, ders_kodu, talep_durumu) VALUES ('{username}', '{selected_teacher}', '{course_code}', '{message}')"
        
            cursor.execute(query)
            conn.commit()
            cursor.close()
            conn.close()
        else:
            print("Veritabanı bağlantı hatası.")
        print("Talep gönderildi.")
    
    send_button = tk.Button(student_window, text="Talep Gönder", command=send_request)
    send_button.pack()

    
def show_interests():
    interests_window = tk.Toplevel(student_window)
    interests_window.title("İlgi Alanları")

    conn = db_connect()
    if conn is not None:
        cursor = conn.cursor()
        query = "SELECT kullanici_adi, ilgi_alani FROM ilgi_alanlari"
        cursor.execute(query)
        interests = cursor.fetchall()
        cursor.close()
        conn.close()

     
        for interest in interests:
            label = tk.Label(interests_window, text=f"{interest[0]} hoca--> İlgi Alanı: {interest[1]}")
            label.pack()
    else:
        print("Veritabanı bağlantı hatası.")



def teacher_panel(hoca_adi):
    
    root.title("Hoca Paneli")

    teacher_window = tk.Toplevel(root)
    teacher_window.title("Hoca Paneli")


    label = tk.Label(teacher_window, text="İlgi Alanlarınızı Seçin:")
    label.pack()

    # İlgi alanları listesi 
    interests_list = ["Bilgisayar Bilimleri", "Algoritma Çözümleme", "İngilizce", "Veri Tabanı Yönetimi", "Sayısal Yöntemler",
                    "Edebiyat", "Programlama", "Görüntü İşleme", "Makine Öğrenmesi", "Yapay Zeka", "Araştırma Problemleri", 
                    "Yazılım Mühendisliği", "Otomata Teorisi", "İşletim Sistemleri", "Programlama Laboratuvarı"]
    selected_interests = []

    interests_listbox = tk.Listbox(teacher_window, selectmode=tk.MULTIPLE)
    for interest in interests_list:
        interests_listbox.insert(tk.END, interest)
    interests_listbox.pack()

    def save_interests():
    
        selected_indices = interests_listbox.curselection()
        for index in selected_indices:
            selected_interest = interests_listbox.get(index)
            selected_interests.append(selected_interest)

     
        conn = db_connect()
        if conn is not None:
            cursor = conn.cursor()
            try:
                for interest in selected_interests:
                    query = "INSERT INTO ilgi_alanlari (kullanici_adi, ilgi_alani) VALUES (%s, %s)"
                    cursor.execute(query, (hoca_adi, interest))
                conn.commit()
            except Exception as e:
               
                conn.rollback()
                print(f"Hata oluştu: {e}")
            finally:
                cursor.close()
                conn.close()

            print("İlgi alanlarınız kaydedildi:", selected_interests)

            messagebox.showinfo("Başarılı", "İlgi alanlarınız başarıyla kaydedildi.")

    save_button = tk.Button(teacher_window, text="İlgi Alanlarını Kaydet", command=save_interests)
    save_button.pack()

    
    
    messages_listbox = tk.Listbox(teacher_window)
    messages_listbox.pack()



    def send_message_to_student(student_name, message):
        conn = db_connect()
        if  conn is not None:
            cursor = conn.cursor()
            try:
                query = "UPDATE mesajlar SET talep_mesaji = %s, talep_durumu = 'Cevaplandı' WHERE hoca_adi = %s AND ogrenci_adi = %s"
                cursor.execute(query, (message, hoca_adi, student_name))
                conn.commit()
            except Exception as e:
                conn.rollback()
                print(f"Hata oluştu: {e}")
            finally:
                cursor.close()
                conn.close()
        
        print(f"Hoca {hoca_adi} öğrenciye mesaj gönderiyor: {message} - Öğrenci: {student_name}")

        
        
    def load_messages():
        conn = db_connect()
        if conn is not None:
            cursor = conn.cursor()
            query = f"SELECT ogrenci_adi, ders_kodu , talep_mesaji FROM mesajlar WHERE hoca_adi = '{hoca_adi}'"
            cursor.execute(query)
            messages = cursor.fetchall()
            cursor.close()
            conn.close()
            messages_listbox.delete(0, tk.END)

        
            for message in messages:
                student_name = message[0]
                message_text = message[2]
                course_text=message[1]
                messages_listbox.insert(tk.END, f"Öğrenci: {student_name} - Mesaj: {message_text} - Ders Kodu: {course_text} ")

        def send_custom_message():
            custom_message = custom_message_entry.get()
            if custom_message:
                selected_index = messages_listbox.curselection()
                if selected_index:
                    selected_message = messages_listbox.get(selected_index)
                    selected_student = selected_message.split(" - ")[0].split(": ")[1]
                    send_message_to_student(selected_student, custom_message)
                    custom_message_entry.delete(0, tk.END)  

        custom_message_label = tk.Label(teacher_window, text="Özel Mesajınızı Girin:")
        custom_message_label.pack()
        custom_message_entry = tk.Entry(teacher_window)
        custom_message_entry.pack()
        send_custom_message_button = tk.Button(teacher_window, text="Mesajı Gönder", command=send_custom_message)
        send_custom_message_button.pack()

    load_messages_button = tk.Button(teacher_window, text="Mesajları Yükle", command=load_messages)
    load_messages_button.pack()

    def show_students_from_other_teachers():
        conn = db_connect()
        if conn is not None:
            cursor = conn.cursor()
            query = f"SELECT ogrenci_adi, ders_kodu, hoca_adi FROM mesajlar WHERE ders_kodu IN (SELECT ders_kodu FROM mesajlar WHERE hoca_adi = '{hoca_adi}') AND hoca_adi != '{hoca_adi}'"
            cursor.execute(query)
            students_from_other_teachers = cursor.fetchall()
            cursor.close()
            conn.close()

            if students_from_other_teachers:
                other_teachers_window = tk.Toplevel(teacher_window)
                other_teachers_window.title("Başka Hocalardan Talep Eden Öğrenciler")
                other_teachers_listbox = tk.Listbox(other_teachers_window)

                for student in students_from_other_teachers:
                    student_name = student[0]
                    course_code = student[1]
                    other_teacher_name = student[2]
                    other_teachers_listbox.insert(tk.END, f"Öğrenci: {student_name} - Ders Kodu: {course_code} - Hoca Adı: {other_teacher_name}")

                other_teachers_listbox.pack()

            else:
                messagebox.showinfo("Bilgi", "Başka hocalardan ders talebinde bulunan öğrenci bulunmuyor.")

    show_students_button = tk.Button(teacher_window, text="Başka Hocalardan Talep Eden Öğrencileri Görüntüle", command=show_students_from_other_teachers)
    show_students_button.pack()
    
    
    
    student_names = get_student_names_from_database()
    bilgi_goster_window=tk.Toplevel()
    for student_name in student_names:
        student_button = tk.Button(bilgi_goster_window, text=student_name, command=lambda name=student_name: show_student_course_info(name))
        student_button.pack()
    
    def show_student_course_info(student_name):
        conn = db_connect()
        if conn is not None:
            cursor = conn.cursor()
            cursor.execute("SELECT ders_kodu, ders_adi, ders_kredi, ders_notu FROM dersler WHERE kullanici_adi = %s", (student_name,))

            course_info = cursor.fetchall()
            cursor.close()
            conn.close()

            student_info_window = tk.Toplevel()
            student_info_window.title(f"{student_name}'in Ders Bilgileri")

            if course_info:
                for course in course_info:
                    ders_kodu, ders_adi, ders_kredi, ders_notu = course
                    info_label = tk.Label(student_info_window, text=f"Ders Kodu: {ders_kodu}, Ders Adı: {ders_adi}, Kredi: {ders_kredi}, Not: {ders_notu}")
                    info_label.pack()
            else:
                no_info_label = tk.Label(student_info_window, text="Öğrencinin ders bilgisi bulunmuyor.")
                no_info_label.pack()

def get_student_names_from_database():
    conn = db_connect()
    if conn is not None:
        cursor = conn.cursor()
        cursor.execute("SELECT DISTINCT kullanici_adi FROM dersler") 
        student_names = [row[0] for row in cursor.fetchall()]
        cursor.close()
        conn.close()
        return student_names
    else:
        return []



root = tk.Tk()
root.title("Proje Dersi Kayıt Uygulama")

root.geometry("300x200") 
root.config(bg="lightblue")

style = ttk.Style()
style.configure("TLabel", foreground="blue", font=("Arial", 12))
style.configure("TEntry", font=("Arial", 12))

custom_font = ("Helvetica", 9, "bold")


username_label = tk.Label(root, text="Kullanıcı Adı:",font=custom_font, fg="red",bg="lightblue")
username_entry = tk.Entry(root)
password_label = tk.Label(root, text="Şifre:",font=custom_font, fg="red",bg="lightblue")
password_entry = tk.Entry(root, show="*")
user_type_label = tk.Label(root, text="Kullanıcı Türü (Öğrenci, Hoca, Yönetici):",font=custom_font, fg="red", bg="lightblue")
user_type_entry = tk.Entry(root)


login_button = tk.Button(root, text="Giriş Yap",
                         command=lambda: login(username_entry.get(), password_entry.get(), user_type_entry.get()),font=custom_font,fg="black")

username_label.pack()
username_entry.pack()
password_label.pack()
password_entry.pack()
user_type_label.pack()
user_type_entry.pack()
login_button.pack()


if db_connect() is not None:
    print("Bağlandı")
else:
    print("Bağlantı başarısız")

root.mainloop()