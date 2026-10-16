# Canli gosterim akisi (her komut oncesi: conda activate disaster && cd ~/disaster_routing_V3)

## Blok 1: rotalama testleri
LC_ALL=C python test_routing.py && LC_ALL=C python test_damage.py && LC_ALL=C python test_delay.py && LC_ALL=C python test_clearing.py
Beklenen: T1, T2, T3, T4, T5, T8a, T8b, T9 "GECTI"

## Blok 2: EMSR AOI17
LC_ALL=C PYTHONPATH=. python demo_emsr.py AOI17
Beklenen: R=10/25/40 tablosu, hasarsiz 4270 m, R=25 icin 4522 m
Yedek: sunum/yedek/01_emsr_AOI17_R25.png

## Blok 3: Maxar (3 kanal)
# 3a: 11 Subat
LC_ALL=C python run_pipeline.py --image inputs/maxar_2023-02-11_10300100E19A4400.tif --a 37.5765 36.9260 --b 37.5835 36.9340 --out sunum/canli/3k_0211.png
Beklenen: Tespit 69 (guclu 11, zayif 58), acik rota yok, 1 segment (95 m)
Yedek: 02_3kanal_0211.png
# 3b: 28 Subat
LC_ALL=C python run_pipeline.py --image inputs/maxar_2023-02-28_10300100E3154100.tif --a 37.5765 36.9260 --b 37.5835 36.9340 --out sunum/canli/3k_0228.png
Beklenen: Tespit 181 (guclu 102, zayif 79), 9 segment (910 m)
Yedek: 03_3kanal_0228.png
# 3c: Islahiye
LC_ALL=C python run_pipeline.py --image inputs/maxar_2023-02-07_1040010082698700.tif --a 37.0225 36.6275 --b 37.0295 36.6365 --out sunum/canli/3k_islahiye.png
Beklenen: Tespit 311 (guclu 159, zayif 152), 6 segment (543 m)
Yedek: 04_3kanal_islahiye.png

## Blok 4: kontrol (enkazsiz 2022, ayni model, ayni parametre)
LC_ALL=C python run_pipeline.py --image inputs/maxar_2022-07-26_10300100D797E100.tif --a 37.5765 36.9260 --b 37.5835 36.9340 --out sunum/canli/3k_2022_kontrol.png
Beklenen: enkaz olmamasina ragmen cok sayida tespit (~84)
Yedek: 05_3kanal_2022_kontrol.png

## Blok 5: 6 kanal (once=2022, sonra=11 Subat)
LC_ALL=C python run_pipeline.py --pre inputs/maxar_2022-07-26_10300100D797E100.tif --image inputs/maxar_2023-02-11_10300100E19A4400.tif --a 37.5765 36.9260 --b 37.5835 36.9340 --out sunum/canli/6k_0211.png
Beklenen: Tespit 5 (hepsi zayif), rota 1369.0 m (+42.5 m)
Yedek: 06_6kanal_0211.png, olasilik haritasi: 09_olasilik_haritasi.png
