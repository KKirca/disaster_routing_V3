# Teze yazilacaklar (2026-10-16)

## Ana iddia (tek cumle)
Rotalama sistemi verilen bir hasar bilgisiyle dogru calisiyor (testler + EMSR648 gosterimi). Hasar tespit modeli kendi veri setinde makul, ama gercek Maxar sahasinda alan kaymasi nedeniyle guvenilir degil. Sistemin tamami sahada dogrulanmis degildir.

## Bolumler
1. Rotalama: OSMnx (UTM), A*, kademeli kural, temizleme rotasi. T1-T9 testleri.
2. Model: KATE-CD, 3 ve 6 kanal, test seti sonuclari.
3. EMSR648 gosterimi (asagida ayrintili).
4. Saha deneyi: Maxar, negatif kontrol, alan kaymasi.
5. Sinirliliklar ve gelecek calisma (EBD ile yeniden egitim).

## EMSR648 gosterimi: nasil yazilacak
Amac cumlesi: "Hasar tespit modelinden bagimsiz olarak, hasar bilgisi dogru bilindiginde sistemin davranisi uzman hasar haritasi ile incelendi."
Yontem (sirayla yaz): saha AOI17 (EMSR648, builtUpA katmani); Destroyed bloklari yolu kapatir; Damaged +100 m, Possibly damaged +50 m gecikme esdegeri; R = 10, 25, 40 m; A ve B noktalari AOI sinirinin guneybati ve kuzeydogu kosesinden %15 iceride, sonuclar gorulmeden onceden sabitlendi (bunu mutlaka yaz, secici raporlama sorusunu onler).

Sonuc tablosu (outputs/emsr_AOI17_duyarlilik.csv dosyasindan al, elle yazma):
| R (m) | kapali kenar | gecikmeli kenar | rota | gercek uzunluk | uzama |
| 10 | 15 | 64 | acik | 4352 m | +82 m |
| 25 | 26 | 282 | acik | 4522 m | +253 m |
| 40 | 29 | 340 | acik | 4522 m | +253 m |
Hasarsiz rota 4270 m, ag: 762 dugum, 2219 kenar, 288 blok (9 yikik, 25 hasarli, 18 olasi hasarli).

Yorum cumleleri (bunlari yazabilirsin):
- Hasar, rotayi hasarsiz duruma gore 82-253 m (%2-6) uzatti ve hicbir R degerinde A-B baglantisi kopmadi.
- R=25 ve R=40 m icin secilen rota ayni; R'ye duyarlilik bu senaryoda 25 m'den sonra doygunluga ulasti.
- Kapali kenar sayisi R ile arttigi icin R, hasarin yol agina yayilimini kontrol eden ana parametredir.
Yorum cumleleri (bunlari YAZMA):
- "Sistem gercek sahada dogrulandi" (hasar girdisi uzman verisi, model ciktisi degil).
- V1 ile dogrudan karsilastirma ("V1 +475 m, V3 +253 m, V3 daha iyi"): kural, ag ve A-B noktalari farkli. Sadece "iki yontemde de sapma gozlendi" de.
- "Kahramanmaras merkez": AOI17 merkezin yaklasik 20 km guneyinde (37.37-37.40 K, 36.83-36.87 D), Turkoglu cevresi. Koordinati haritada dogrula, sonra yaz.

Siniriliklar (hepsini yaz):
1. EMSR builtUpA poligonlari bina degil blok (AOI17 medyan alan 5566 m2, AOI04 2512 m2, AOI16 6460 m2). Hasar sinifi blok duzeyinde.
2. Sadece 9 yikik blok var; senaryo nispeten kolay.
3. Tek A-B cifti; sonuc genellenemez.
4. Gecikme degerleri (100 ve 50 m) keyfi baslangic degerleri, duyarlilik analizine girmedi.
5. EMSR648 yol hasari referansi icermiyor: transportationL katmani test penceresinde 343 yolun tamamini "No visible damage" gosteriyor.

## Yan bulgu: AOI04 referans olarak kullanilamadi
Maxar test penceresi (Kahramanmaras merkez, 1 km2) EMSR648 AOI04 ile tamamen ortusuyor (%100 Image Footprint, %0 Not Analysed). Yine de pencerede 265 bloktan sadece 1 Destroyed var; gozle gorulen cokmelerle celisiyor. Neden: poligonlar blok, etiket blok duzeyinde. Bu yuzden model ciktisi EMSR ile bina duzeyinde karsilastirilmadi. Bunu "model dogrulamasi yapilamadi" diye degil, "uygun referans yoktu" diye yaz.

## Saha deneyi (Maxar, Kahramanmaras merkez): nasil yazilacak
Tablo (ayni 1 km2 pencere, ayni parametreler):
| model | 2022 (enkaz yok) | 2023-02-11 | 2023-02-28 |
| 3 kanal | 84 | 69 | 181 |
| 6 kanal | 0 (ayni goruntu iki kez, kod saglamasi) | 5 | 20 |
Yaz: 3 kanal modeli enkaz olmayan goruntude 11 Subat'tan fazla tespit uretti, yani sinyal yanlis alarm tabaninin ustunde degil. 6 kanal modeli yanlis alarm vermiyor ama buyuk enkaz bolgelerini kaciriyor (esiksiz olasilik haritasinda piksellerin %98.5'i 0.05 altinda). Sebep: alan kaymasi (sensor, mevsim, bakis acisi 23-31 derece, renk dagilimi). Eksik ve onemli: 2022+2022 saglamasi gercek bir negatif kontrol degil (ayni goruntu), bunu yaz.
Bu bolumu "model basarisiz oldu" degil "benchmark basarisi saha basarisi anlamina gelmez, negatif kontrolle gosterildi" diye cercevele.

## Yazilmamasi gerekenler
- 11 ve 28 Subat Maxar rota gorselleri negatif kontrol olmadan "sistem ciktisi" olarak.
- Dice icin "accuracy". Dice 0.4523 (3 kanal 0.4897) ortusme olcusudur.
- "Veri artirma uygulandi": 6 kanal egitiminde augment bayragi kullanilmiyordu, 3 kanal egitiminde de yoktu.
- "0.3 m cozunurluk": Maxar ARD izgarasi 0.3 m, efektif cozunurluk 0.5-0.6 m.
- 3 kanal ve 6 kanal farki "kanitlandi": her model bir kez egitildi (3 seed yok), fark 0.037 Dice.
- Maxar rota gorselleri icin "yol ag: gercek": OSM bugunun verisi (2026), deprem anina ait degil.

## Gelecek calisma (bir paragraf)
EBD (Wang ve ark. 2025, ~944 Turkiye deprem cifti) ile sahayi temsil eden yeniden egitim, deprem oncesi Maxar karolariyla zor negatif ornekler, renk ve bakis acisi artirmasi, 3 seed ile model karsilastirmasi, bina duzeyinde referansla nesne duzeyi recall, gecikme ve R icin duyarlilik analizi, deprem anina ait OSM gecmis verisi.

## Teslimden once son kontrol
- outputs/emsr_AOI17_R25.png sekline bak: mavi rota kirmizi yoldan geciyor mu?
- Tablolardaki her sayiyi csv ve terminal ciktisindan al.
- Sekilleri ve csv dosyalarini tez klasorune elle kopyala (outputs/ git disinda).
