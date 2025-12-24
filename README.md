# TR Plaka DFA Doğrulama Uygulaması

Bu proje, **Türkiye Cumhuriyeti araç plaka formatını** doğrulamak amacıyla
**Otomatlar Teorisi** kapsamında bir **DFA** tasarımı ve
bu otomatın **görsel, adım adım simülasyonunu** içeren bir Python uygulamasıdır.

Proje, yalnızca regex kullanmak yerine **durumlar, geçişler ve kabul koşulları**
üzerinden çalışan gerçek bir otomata yaklaşımı sunar.

---

##  Projenin Amacı

- Türkiye plaka formatını biçimsel olarak tanımlamak
- Bu formatı tanıyan bir DFA tasarlamak
- Otomatın çalışmasını **adım adım ve animasyonlu** şekilde göstermek
- Otomata teorisini gerçek hayat problemi üzerinde somutlaştırmak

---

##  Kabul Edilen Plaka Formatı

Aşağıdaki biçim kabul edilmektedir:

DD ␠ L{1,3} ␠ D{2,4}

### Açıklama:
- `DD`   : İl kodu (01–81 arası)
- `␠`    : Boşluk
- `L`    : Büyük harf (Türk plaka sisteminde izinli harfler)
- `D`    : Rakam (0–9)

### Örnek Geçerli Plakalar:
- `34 ABC 1234`
- `06 TS 1461`
- `01 A 23`

### Örnek Geçersiz Plakalar:
- `90 ABC 1234` (geçersiz il kodu)
- `34 ABÇ 123` (izin verilmeyen harf)
- `34ABC1234` (boşluk yok)
- `34 A 1` (eksik rakam)

---

##  Kullanılan Alfabe

- **Rakamlar:** `0–9`
- **Harfler:** Türk plaka sisteminde kullanılan büyük harfler  
  (İ, Ç, Ğ, Ö, Ş, Ü, Q, W, X gibi harfler hariç)
- **Boşluk:** `␠`

---

##  Otomata Yapısı

- Başlangıç durumu: `q0`
- Kabul durumları: `q9`, `q10`, `q11` (çift daire ile gösterilir)
- Hata durumu: `qDead` (kırmızı çift daire)
- Geçersiz girişlerde otomata `qDead` durumuna düşer

---

##  Görselleştirme Özellikleri

- Tkinter `Canvas` üzerinde otomata çizimi
- Başlangıç oku (q0)
- Kabul ve hata durumlarının ayırt edici gösterimi
- Aktif durum vurgulaması
- **Geçilen geçişlerin mavi renkle animasyonu**
- Tüm grafik otomatik ölçeklendirilmiştir

---

##  Kullanıcı Arayüzü ve Kontroller

Uygulama aşağıdaki kontrolleri sunar:

- **Doğrula (Hazırla):**  
  Girişi analiz eder, DFA adımlarını oluşturur (animasyon başlamaz)
- **İleri Adım:**  
  Otomatı tek adım ilerletir
- **Başlat / Devam:**  
  Adımları otomatik olarak oynatır
- **Duraklat:**  
  Otomatik oynatmayı durdurur

Alt kısımda her adım için:
- Okunan karakter
- Karakter sınıfı
- Kaynak durum → hedef durum  
bilgileri listelenir.

---

**Dosyalar Arası İlişki Akışı**

Kullanıcı
   ↓
app_tk.py (UI Kontrolü)
   ↓
normalize.py (Girdi temizleme)
   ↓
runner.py (Otomatayı çalıştır)
   ↓
tr_plate_dfa.py (Geçiş kuralları)
   ↓
runner.py (Adım sonuçları)
   ↓
app_tk.py
   ↓
dfa_view_tk.py (Görsel animasyon)

---

**tr_plate_dfa.py**

Bu dosya projenin çekirdeğini oluşturur.

Otomatın:

Durumlarını (State)

Kabul durumlarını

Karakter sınıflarını (rakam, harf, boşluk)

Geçiş kurallarını

Türkiye plaka formatına uygun olacak şekilde biçimsel olarak tanımlar

**runner.py**

Bu dosya, tanımlanan otomatı çalıştıran yürütücü (engine) görevi görür.

Kullanıcıdan gelen giriş string’ini alır

Karakter karakter dolaşır

Her adımda:

Okunan karakteri

Karakter sınıfını

Mevcut durum → yeni durumu 
kaydeder

Sonuç olarak:

Kabul / red bilgisi

Tüm geçiş adımlarını içeren bir yapı döndürür

**normalize.py**

Bu dosya, kullanıcıdan alınan girdiyi otomata uygun hâle getirir.

Küçük harfleri büyüğe çevirir

Fazladan boşlukları temizler

Otomatın okuyabileceği standart formata dönüştürür

**app_tk.py**

Bu dosya uygulamanın ana kontrol merkezidir.

Tkinter arayüzünü oluşturur

Butonları ve giriş alanını yönetir

Kullanıcının:

Doğrula

Adım adım ilerleme

Başlat / duraklat
isteklerini kontrol eder

**dfa_view_tk.py**

Bu dosya DFA’nın görsel temsilinden sorumludur.

Tüm durumları ve geçişleri Canvas üzerinde çizer

Başlangıç oku, kabul durumları ve hata durumu görselleştirilir

Aktif durum ve geçilen yollar mavi renkle vurgulanır

Ölçeklendirme otomatik yapılır

---

Çalıştırmak için:
python .\src\main.py
