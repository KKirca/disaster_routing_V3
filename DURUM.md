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
