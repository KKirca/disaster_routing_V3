# V3 Durum (2026-10-04)

## Tamamlanan
- 6 kanal (pre+post) U-Net: checkpoints/best_model.pth, test Dice batch-ort 0.4482 / global 0.4523
- 3 kanal (post) U-Net egitimi: checkpoints/post_best.pth, gunluk logs/train_post.csv
- routing.py: OSMnx graf (UTM), A* (duz cizgi sezgiseli), closed kenar, close_edges_near (R tamponu)
- Testler: test_routing.py (T1-T3), test_damage.py (T4-T5), hepsi geciyor

## Siradaki adim
1. 3 kanal modelin test seti Dice'i (6 kanal ile karsilastirma)
2. infer.py: ortusmeli 512 karolama + test_infer.py (T6, 2x2 mozaik)
3. Maske -> poligon -> kose koordinatlariyla enlem/boylam -> UTM
4. Uctan uca: goruntu + bbox + A/B -> rota

## Acik konular
- R degeri sabit degil: duyarlilik analizi (10/15/25/40 m)
- Model secimi val loss'a gore; Dice ile ayni epoch'u secmeyebilir
- KATE-CD GSD'si (m/piksel) bulunacak, girdi goruntusu ile karsilastirilacak
- Veri artirma kodu eski egitimde olu bayrakti; artirma yapilmadi

## Model karsilastirmasi (2026-10-05, test seti, esik 0.5, global)
| model | dice | iou | precision | recall |
|---|---|---|---|---|
| 6 kanal | 0.4523 | 0.2922 | 0.7981 | 0.3156 |
| 3 kanal | 0.4897 | 0.3243 | 0.6289 | 0.4010 |
Karar: sistem 3 kanal modelle devam ediyor (tek goruntu hedefi + daha yuksek recall).

## Ek acik konular
- Fark tek egitime dayaniyor: her model 3 seed ile egitilip ort +- std raporlanmali
- Nesne duzeyinde recall (bina basina) hesaplanmali; rotalama icin piksel recall'dan daha anlamli
- 3 kanal egitiminde asiri uyum: son epochlarda train dice ~0.79, val dice ~0.46-0.51

## 2026-10-06 durum
- Siradaki adim 2-5 tamamlandi: infer.py (T6), georef.py (T7a-c), run_pipeline.py (uctan uca)
- Duman testi (KATE-CD mozaik, sahte konum): rota kapali yollardan gecmiyor, kapali yollar tespitlerin yaninda (gorsel dogrulama)
- TUM python komutlari LC_ALL=C ile calistirilmali (GDAL Turkce locale hatasi)

## Siradaki adim (guncel)
1. Gercek test goruntusu: Google Earth Pro, deprem sonrasi, tepeden (u), kuzey yukari (n), kose koordinatlari
2. run_pipeline.py ile gercek goruntu; GSD kontrolu (kare piksel uyarisi cikmamali)
3. Tez analizleri: R ve esik duyarliligi, nesne duzeyinde recall, 3 seed, veri artirma
- Not: kapali kenar = kavsaktan kavsaga tum segment; "kapanan yol uzunlugu" metrigi bu yuzden abartili

## 2026-10-06 aksam durumu
### Sistem (dogrulandi)
- GeoTIFF girdi (Maxar), kademeli kural (guclu=kapat, zayif=gecikme +100 m), en buyuk SCC, temizleme rotasi
- Testler: T1-T9 hepsi geciyor
### Test sahasi: Kahramanmaras merkez, 1 km, A=(37.5765, 36.9260) B=(37.5835, 36.9340)
- Kirpim: tools/crop_maxar.py <katalog> 37.58 36.93 1000
| goruntu | katalog | tespit | guclu | kapali | sonuc |
|---|---|---|---|---|---|
| 2022-07-26 (deprem oncesi) | 10300100D797E100 | 84 | 17 | 51 | 3 segment temizle |
| 2023-02-11 | 10300100E19A4400 | 69 | 11 | 18 | 1 segment temizle |
| 2023-02-28 | 10300100E3154100 | 181 | 102 | 177 | 9 segment temizle |
- Islahiye (1040010082698700) calismadan cikarildi; agac ve demiryolu yanlis alarmlarinin ornegi olarak saklaniyor
### ANA BULGU (negatif kontrol)
- Deprem oncesi goruntude (enkaz yok) 84 tespit > 11 Subat'ta 69 tespit
- 3 kanal model bu Maxar sahasinda yanlis alarm tabaninin uzerinde sinyal uretmiyor: enkaz yerine dokuyu (agac, cati ekipmani, toprak) buluyor
- Renk normalizasyonu deneyi: model renge duyarli (11 Subat tespitleri -%57), ama tarih farkini aciklamiyor

## SIRADAKI KARAR (buradan devam)
1. 6 kanal modeli bu sahada test et (2022 oncesi + 2023 sonrasi, ayni piksel izgarasi). Saglama: 2022+2022 -> ~0 tespit beklenir. Not: "tek goruntu" hedefinden sapma, karar kullanicida
2. 3 kanal modeli zor negatiflerle yeniden egit: baska karolardan deprem oncesi Maxar (etiket = tamamen 0) + renk artirmasi. Test sahasinin 2022 goruntusu egitime GIRMEYECEK
3. Uc model ayni negatif kontrolle karsilastirilacak

## 2026-10-06 gece: 6 kanal saha testi ve KARAR
| model | 2022 (enkaz yok) | 2023-02-11 | 2023-02-28 |
|---|---|---|---|
| 3 kanal | 84 tespit | 69 | 181 |
| 6 kanal (once=2022) | 0 (ayni goruntu, saglama) | 5 (hepsi zayif) | 20 |
- 6 kanal: yanlis alarm yok ama buyuk enkaz bolgelerini kaciriyor; rota coken seritten geciyor (tehlikeli)
- Esiksiz olasilik haritasi: pikselin %98.5'i < 0.05; enkaz bolgelerinde sinyal yok -> esik sorunu degil
- Sonuc: iki model de Maxar sahasinda alan kaymasi nedeniyle calismiyor (KATE-CD Dice 0.45-0.49 sahaya tasinmiyor)

## KARAR (2026-10-06): Yol 1, 2 gun kaldi
- Yeniden egitim yok. Model KATE-CD sonuclariyla, rotalama testlerle raporlanacak
- Rotalama gosterimi: EMSR648 uzman hasar poligonlari dogrudan girdi
- Saha deneyi (negatif kontrol + 6 kanal) "alan kaymasi" bulgusu olarak raporlanacak, gelecek calisma: EBD ile yeniden egitim
- Maxar rota gorselleri negatif kontrol olmadan "sistem ciktisi" olarak SUNULMAYACAK
## Gun 1: EMSR648 -> rotalama, R duyarliligi (10/25/40) | Gun 2: tablo/sekil toplama, yazim
