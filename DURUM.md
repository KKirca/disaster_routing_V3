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
