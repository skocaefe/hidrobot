# Tank stok çözeltileri (kg cinsinden)
stok_a = {}
stok_b = {}
for gubre, miktar in gubre_miktarlari_gram.items():
    stok_miktar_kg = miktar / konsantrasyon
    if gubre in ["Kalsiyum Amonyum Nitrat", "Kalsiyum Nitrat", "Magnezyum Nitrat", "Kalsiyum Hidroksit", "Calmag"]:
        stok_a[gubre] = stok_miktar_kg
    else:
        stok_b[gubre] = stok_miktar_kg

# Tank hacmi kontrolü
total_stok_a_kg = sum(stok_a.values())
total_stok_b_kg = sum(stok_b.values())
max_kg_per_liter = 1.0  # 1 litre suya yaklaşık 1 kg çözelti sığar (yaklaşık bir değer)
tank_a_capacity_kg = tank_a_hacim * max_kg_per_liter
tank_b_capacity_kg = tank_b_hacim * max_kg_per_liter

# Gerekli minimum tank hacimlerini hesapla
min_tank_a_hacim = total_stok_a_kg / max_kg_per_liter
min_tank_b_hacim = total_stok_b_kg / max_kg_per_liter

# Alternatif konsantrasyon oranı önerisi
if total_stok_a_kg > tank_a_capacity_kg or total_stok_b_kg > tank_b_capacity_kg:
    # Mevcut konsantrasyon oranı ile tankların alabileceği maksimum stok miktarına göre yeni bir konsantrasyon oranı öner
    max_stok_a_kg = tank_a_hacim * max_kg_per_liter
    max_stok_b_kg = tank_b_hacim * max_kg_per_liter
    suggested_konsantrasyon_a = sum(gubre_miktarlari_gram.get(gubre, 0) for gubre in ["Kalsiyum Amonyum Nitrat", "Kalsiyum Nitrat", "Magnezyum Nitrat", "Kalsiyum Hidroksit", "Calmag"]) / max_stok_a_kg if max_stok_a_kg > 0 else konsantrasyon
    suggested_konsantrasyon_b = sum(gubre_miktarlari_gram.get(gubre, 0) for gubre in gubre_miktarlari_gram if gubre not in ["Kalsiyum Amonyum Nitrat", "Kalsiyum Nitrat", "Magnezyum Nitrat", "Kalsiyum Hidroksit", "Calmag"]) / max_stok_b_kg if max_stok_b_kg > 0 else konsantrasyon
    suggested_konsantrasyon = max(suggested_konsantrasyon_a, suggested_konsantrasyon_b)

if total_stok_a_kg > tank_a_capacity_kg:
    st.warning(
        f"A tankı hacmi yetersiz! Toplam {total_stok_a_kg:.2f} kg stok çözelti gerekiyor, ancak tank sadece {tank_a_capacity_kg:.2f} kg alabilir. "
        f"Çözüm Önerileri:\n"
        f"- A tankı hacmini en az {min_tank_a_hacim:.2f} litreye çıkarın, veya\n"
        f"- Stok konsantrasyon oranını {konsantrasyon:.1f}x yerine en fazla {suggested_konsantrasyon:.1f}x olarak ayarlayın."
    )
if total_stok_b_kg > tank_b_capacity_kg:
    st.warning(
        f"B tankı hacmi yetersiz! Toplam {total_stok_b_kg:.2f} kg stok çözelti gerekiyor, ancak tank sadece {tank_b_capacity_kg:.2f} kg alabilir. "
        f"Çözüm Önerileri:\n"
        f"- B tankı hacmini en az {min_tank_b_hacim:.2f} litreye çıkarın, veya\n"
        f"- Stok konsantrasyon oranını {konsantrasyon:.1f}x yerine en fazla {suggested_konsantrasyon:.1f}x olarak ayarlayın."
    )
