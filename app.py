import streamlit as st
import pandas as pd
from reportlab.lib.pagesizes import letter
from reportlab.pdfgen import canvas
import io
import json
import os
import math
import logging
from typing import Dict, Any, List, Tuple

# Loglama yapılandırması
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(name)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

# Gübre veritabanı için varsayılan değerler
DEFAULT_GUBRELER = {
    "Potasyum Nitrat": {"formul": "KNO3", "besin": {"K": 0.378, "NO3": 0.135}, "agirlik": 101.10},
    "Potasyum Sülfat": {"formul": "K2SO4", "besin": {"K": 0.45, "SO4": 0.18}, "agirlik": 174.26},
    "Kalsiyum Nitrat": {"formul": "Ca(NO3)2·4H2O", "besin": {"Ca": 0.187, "NO3": 0.144}, "agirlik": 236.15},
    "Amonyum Sülfat": {"formul": "(NH4)2SO4", "besin": {"NH4": 0.272, "SO4": 0.183}, "agirlik": 132.14},
    "Calmag": {"formul": "Calmag", "besin": {"Ca": 0.165, "Mg": 0.06}, "agirlik": 1.0},
    "Magnezyum Sülfat": {"formul": "MgSO4·7H2O", "besin": {"Mg": 0.096, "SO4": 0.132}, "agirlik": 246.51},
    "Magnezyum Nitrat": {"formul": "Mg(NO3)2·6H2O", "besin": {"Mg": 0.09, "NO3": 0.10}, "agirlik": 256.41},
    "Mono Potasyum Fosfat": {"formul": "KH2PO4", "besin": {"K": 0.282, "H2PO4": 0.225}, "agirlik": 136.09},
    "Mono Amonyum Fosfat": {"formul": "NH4H2PO4", "besin": {"H2PO4": 0.266, "NH4": 0.17}, "agirlik": 115.03},
    "Üre Fosfat": {"formul": "H3PO4·CO(NH2)2", "besin": {"H2PO4": 0.194, "N": 0.17}, "agirlik": 1.0},
    "Foliar Üre": {"formul": "CO(NH2)2", "besin": {"N": 0.46}, "agirlik": 60.06},
    "Kalsiyum Klorür": {"formul": "CaCl2", "besin": {"Ca": 0.38}, "agirlik": 110.98},
    "Potasyum Klorür": {"formul": "KCl", "besin": {"K": 0.524}, "agirlik": 74.55},
    "WS 0-0-60+48 Cl": {"formul": "KCl", "besin": {"K": 0.498}, "agirlik": 74.55},
    "NK 16-0-40": {"formul": "NK 16-0-40", "besin": {"K": 0.332, "N": 0.16}, "agirlik": 1.0},
    "Mangan Sülfat": {"formul": "MnSO4·H2O", "besin": {"Mn": 0.32}, "agirlik": 169.02},
    "Çinko Sülfat": {"formul": "ZnSO4·7H2O", "besin": {"Zn": 0.23}, "agirlik": 287.56},
    "Boraks": {"formul": "Na2B4O7·10H2O", "besin": {"B": 0.11}, "agirlik": 381.37},
    "Sodyum Molibdat": {"formul": "Na2MoO4·2H2O", "besin": {"Mo": 0.40}, "agirlik": 241.95},
    "Demir-EDDHA": {"formul": "Fe-EDDHA", "besin": {"Fe": 0.04}, "agirlik": 932.00},
    "Bakır Sülfat": {"formul": "CuSO4·5H2O", "besin": {"Cu": 0.075}, "agirlik": 250.00}
}

# Mikro besin elementleri için referans değerler (µmol/L cinsinden)
MIKRO_BESINLER = {
    "Demir-EDDHA": {"besin": "Fe", "ref_umol_L": 40, "mg_L": 37.280},
    "Boraks": {"besin": "B", "ref_umol_L": 30, "mg_L": 2.858},
    "Mangan Sülfat": {"besin": "Mn", "ref_umol_L": 5, "mg_L": 0.845},
    "Çinko Sülfat": {"besin": "Zn", "ref_umol_L": 4, "mg_L": 1.152},
    "Bakır Sülfat": {"besin": "Cu", "ref_umol_L": 0.75, "mg_L": 0.188},
    "Sodyum Molibdat": {"besin": "Mo", "ref_umol_L": 0.5, "mg_L": 0.120}
}

def load_gubreler() -> Dict[str, Any]:
    """Gübre veritabanını yükler veya oluşturur."""
    try:
        if not os.path.exists("gubreler.json"):
            logger.info("gubreler.json dosyası bulunamadı, yeni bir dosya oluşturuluyor...")
            st.warning("gubreler.json dosyası bulunamadı, yeni bir dosya oluşturuluyor...")
            with open("gubreler.json", "w", encoding="utf-8") as f:
                json.dump(DEFAULT_GUBRELER, f, ensure_ascii=False, indent=4)
        
        with open("gubreler.json", "r", encoding="utf-8") as f:
            gubreler = json.load(f)
        
        # Amonyum Sülfat'ın varlığını kontrol et
        if "Amonyum Sülfat" not in gubreler:
            logger.warning("Amonyum Sülfat gübresi gübre veritabanında bulunamadı!")
            st.error("Amonyum Sülfat gübresi gubreler.json dosyasında bulunamadı! Dosyayı kontrol edin veya yeniden oluşturun.")
            gubreler["Amonyum Sülfat"] = DEFAULT_GUBRELER["Amonyum Sülfat"]
            with open("gubreler.json", "w", encoding="utf-8") as f:
                json.dump(gubreler, f, ensure_ascii=False, indent=4)
            st.success("Amonyum Sülfat gübresi eklendi ve gubreler.json dosyası güncellendi.")
        
        return gubreler
    except Exception as e:
        logger.error(f"gubreler.json dosyasını yüklerken bir hata oluştu: {str(e)}")
        st.error(f"gubreler.json dosyasını yüklerken bir hata oluştu: {str(e)}")
        st.stop()

def save_recipe(recipe_data: Dict[str, Any], recipe_name: str) -> bool:
    """Reçeteyi JSON dosyasına kaydeder."""
    try:
        if not recipe_name:
            st.error("Lütfen bir reçete adı girin!")
            return False
            
        saved_recipe = {
            "name": recipe_name,
            "original_recete": recipe_data["original_recete"],
            "gubre_miktarlari_gram": recipe_data["gubre_miktarlari_gram"],
            "konsantrasyon": recipe_data["konsantrasyon"],
            "ec": recipe_data["ec"],
            "ph": recipe_data["ph"],
            "stok_a": recipe_data["stok_a"],
            "stok_b": recipe_data["stok_b"]
        }
        
        # recipes.json dosyasını kontrol et, yoksa oluştur
        if not os.path.exists("recipes.json"):
            with open("recipes.json", "w", encoding="utf-8") as f:
                json.dump([], f, ensure_ascii=False, indent=4)
        
        # Mevcut reçeteleri yükle
        with open("recipes.json", "r", encoding="utf-8") as f:
            recipes = json.load(f)
        
        # Yeni reçeteyi ekle
        recipes.append(saved_recipe)
        
        # Güncellenmiş reçeteleri kaydet
        with open("recipes.json", "w", encoding="utf-8") as f:
            json.dump(recipes, f, ensure_ascii=False, indent=4)
        
        st.success(f"Reçete '{recipe_name}' başarıyla kaydedildi!")
        return True
    except Exception as e:
        logger.error(f"Reçete kaydederken hata: {str(e)}")
        st.error(f"Reçete kaydederken bir hata oluştu: {str(e)}")
        return False

def load_recipes() -> List[Dict[str, Any]]:
    """Kaydedilmiş reçeteleri yükler."""
    try:
        if os.path.exists("recipes.json"):
            with open("recipes.json", "r", encoding="utf-8") as f:
                return json.load(f)
        return []
    except Exception as e:
        logger.error(f"Reçeteleri yüklerken hata: {str(e)}")
        st.error(f"Reçeteleri yüklerken bir hata oluştu: {str(e)}")
        return []

def calculate_adjusted_recipe(original_recipe: Dict[str, float], water_values: Dict[str, float]) -> Dict[str, float]:
    """Su kaynağındaki değerleri dikkate alarak hedef konsantrasyonları ayarlar."""
    return {
        "NO3": max(0, original_recipe["NO3"] - water_values["no3"]),
        "H2PO4": max(0, original_recipe["H2PO4"] - water_values["h2po4"]),
        "SO4": max(0, original_recipe["SO4"] - water_values["so4"]),
        "NH4": max(0, original_recipe["NH4"] - water_values["nh4"]),
        "K": max(0, original_recipe["K"] - water_values["k"]),
        "Ca": max(0, original_recipe["Ca"] - water_values["ca"]),
        "Mg": max(0, original_recipe["Mg"] - water_values["mg"]),
        "Fe": original_recipe["Fe"],
        "B": original_recipe["B"],
        "Mn": original_recipe["Mn"],
        "Zn": original_recipe["Zn"],
        "Cu": original_recipe["Cu"],
        "Mo": original_recipe["Mo"]
    }

def calculate_anyon_katyon_balance(recipe: Dict[str, float]) -> Tuple[Dict[str, List], float, float, float, float]:
    """Anyon-Katyon dengesini hesaplar."""
    anyon_me = recipe["NO3"] + recipe["H2PO4"] + (recipe["SO4"] * 2)
    katyon_me = recipe["NH4"] + recipe["K"] + (recipe["Ca"] * 2) + (recipe["Mg"] * 2)
    anyon_mmol = recipe["NO3"] + recipe["H2PO4"] + recipe["SO4"]
    katyon_mmol = recipe["NH4"] + recipe["K"] + recipe["Ca"] + recipe["Mg"]
    
    tablo_denge = {
        "Anyon": ["NO3", "H2PO4", "SO4", "", "Toplam"],
        "mmol/L (Anyon)": [recipe["NO3"], recipe["H2PO4"], recipe["SO4"], "", anyon_mmol],
        "me/L (Anyon)": [recipe["NO3"], recipe["H2PO4"], recipe["SO4"] * 2, "", anyon_me],
        "Katyon": ["NH4", "K", "Ca", "Mg", "Toplam"],
        "mmol/L (Katyon)": [recipe["NH4"], recipe["K"], recipe["Ca"], recipe["Mg"], katyon_mmol],
        "me/L (Katyon)": [recipe["NH4"], recipe["K"], recipe["Ca"] * 2, recipe["Mg"] * 2, katyon_me]
    }
    
    return tablo_denge, anyon_me, katyon_me, anyon_mmol, katyon_mmol

def calculate_ec_ph(recipe: Dict[str, float], water_ec: float, water_ph: float) -> Tuple[float, float]:
    """EC ve pH değerlerini hesaplar."""
    # EC hesaplama (iyon etkileşim faktörü ile)
    ec_ion = (recipe["NO3"] * 0.075) + (recipe["H2PO4"] * 0.090) + (recipe["SO4"] * 0.120) + \
             (recipe["NH4"] * 0.073) + (recipe["K"] * 0.074) + (recipe["Ca"] * 0.120) + (recipe["Mg"] * 0.106)
    ec = (ec_ion + water_ec) * (1 - 0.1)  # Etkileşim faktörü: 0.1

    # pH hesaplama (tamponlama kapasitesi ile)
    h2po4_ratio = recipe["H2PO4"] / (recipe["H2PO4"] + 0.01)  # HPO₄²⁻/H₂PO₄⁻ oranı (basitleştirilmiş)
    pka_h2po4 = 7.2
    ph_base = pka_h2po4 + math.log10(h2po4_ratio) if h2po4_ratio > 0 else 7.0
    ph_adjust = -(recipe["NH4"] * 0.1) + (recipe["Ca"] * 0.05 + recipe["Mg"] * 0.03)
    ph = (ph_base + water_ph) / 2 + ph_adjust  # Su pH'sı ile ortalama alınıp düzeltme yapılır
    
    return ec, ph

def calculate_fertilizer_amounts(adjusted_recipe: Dict[str, float], gubreler: Dict[str, Any]) -> Tuple[Dict, Dict, Dict]:
    """Gübre miktarlarını hesaplar."""
    # Makro besinler için gübre miktarları (mmol/L) 
    gubre_miktarlari_mmol = {
        "Amonyum Sülfat": {"NH4": 0.0, "SO4": 0.0},
        "Kalsiyum Nitrat": {"NO3": 0.0, "Ca": 0.0},
        "Magnezyum Nitrat": {"Mg": 0.0, "NO3": 0.0},
        "Mono Amonyum Fosfat": {"NH4": 0.0, "H2PO4": 0.0},
        "Mono Potasyum Fosfat": {"H2PO4": 0.0, "K": 0.0},
        "Potasyum Nitrat": {"K": 0.0, "NO3": 0.0},
        "Potasyum Sülfat": {"K": 0.0, "SO4": 0.0}
    }

    # Adım adım hesaplama (HydroBuddy mantığı)
    # 1. NH₄ ihtiyacını Amonyum Sülfat ve Mono Amonyum Fosfat ile karşıla
    total_nh4_needed = adjusted_recipe["NH4"]
    if total_nh4_needed > 0:
        # Önce H₂PO₄ ihtiyacını göz önünde bulundurarak MAP kullan
        if adjusted_recipe["H2PO4"] > 0:
            # MAP ile hem NH₄ hem de H₂PO₄ ihtiyacını karşılamaya çalış
            nh4_from_map = min(total_nh4_needed, adjusted_recipe["H2PO4"] / (0.266 / 0.17))  # MAP'in NH₄ katkısı
            gubre_miktarlari_mmol["Mono Amonyum Fosfat"]["NH4"] = nh4_from_map
            gubre_miktarlari_mmol["Mono Amonyum Fosfat"]["H2PO4"] = nh4_from_map * (0.266 / 0.17)

        # Kalan NH₄ ihtiyacını Amonyum Sülfat ile karşıla
        remaining_nh4 = total_nh4_needed - gubre_miktarlari_mmol["Mono Amonyum Fosfat"]["NH4"]
        if remaining_nh4 > 0:
            gubre_miktarlari_mmol["Amonyum Sülfat"]["NH4"] = remaining_nh4
            gubre_miktarlari_mmol["Amonyum Sülfat"]["SO4"] = remaining_nh4 * (0.183 / 0.272)

    # 2. Kalan H₂PO₄ için Mono Potasyum Fosfat (MKP)
    remaining_h2po4 = adjusted_recipe["H2PO4"] - gubre_miktarlari_mmol["Mono Amonyum Fosfat"]["H2PO4"]
    if remaining_h2po4 > 0:
        gubre_miktarlari_mmol["Mono Potasyum Fosfat"]["H2PO4"] = remaining_h2po4
        gubre_miktarlari_mmol["Mono Potasyum Fosfat"]["K"] = remaining_h2po4 * (0.282 / 0.225)

    # 3. Kalsiyum için Kalsiyum Nitrat
    if adjusted_recipe["Ca"] > 0:
        gubre_miktarlari_mmol["Kalsiyum Nitrat"]["Ca"] = adjusted_recipe["Ca"]
        gubre_miktarlari_mmol["Kalsiyum Nitrat"]["NO3"] = adjusted_recipe["Ca"] * (0.144 / 0.187) * (62 / 14)

    # 4. Magnezyum için Magnezyum Nitrat
    if adjusted_recipe["Mg"] > 0:
        gubre_miktarlari_mmol["Magnezyum Nitrat"]["Mg"] = adjusted_recipe["Mg"]
        gubre_miktarlari_mmol["Magnezyum Nitrat"]["NO3"] = adjusted_recipe["Mg"] * (0.10 / 0.09) * (62 / 14)

    # 5. Kalan NO₃ için Potasyum Nitrat
    remaining_no3 = adjusted_recipe["NO3"] - (gubre_miktarlari_mmol["Kalsiyum Nitrat"]["NO3"] + gubre_miktarlari_mmol["Magnezyum Nitrat"]["NO3"])
    if remaining_no3 > 0:
        gubre_miktarlari_mmol["Potasyum Nitrat"]["NO3"] = remaining_no3
        gubre_miktarlari_mmol["Potasyum Nitrat"]["K"] = remaining_no3 * (0.378 / 0.135) * (14 / 62)

    # 6. Kalan K için Potasyum Sülfat
    remaining_k = adjusted_recipe["K"] - (gubre_miktarlari_mmol["Mono Potasyum Fosfat"]["K"] + gubre_miktarlari_mmol["Potasyum Nitrat"]["K"])
    if remaining_k > 0:
        gubre_miktarlari_mmol["Potasyum Sülfat"]["K"] = remaining_k
        gubre_miktarlari_mmol["Potasyum Sülfat"]["SO4"] = remaining_k * (0.18 / 0.45)
    else:
        gubre_miktarlari_mmol["Potasyum Sülfat"]["K"] = 0.0
        gubre_miktarlari_mmol["Potasyum Sülfat"]["SO4"] = 0.0

    # 7. Kalan SO₄ ihtiyacı (Amonyum Sülfat ve Potasyum Sülfat sonrası)
    remaining_so4 = adjusted_recipe["SO4"] - (gubre_miktarlari_mmol["Amonyum Sülfat"]["SO4"] + gubre_miktarlari_mmol["Potasyum Sülfat"]["SO4"])
    if remaining_so4 > 0:
        additional_amonyum_sulfat = remaining_so4 / (0.183 / 0.272)
        gubre_miktarlari_mmol["Amonyum Sülfat"]["SO4"] += remaining_so4
        gubre_miktarlari_mmol["Amonyum Sülfat"]["NH4"] += additional_amonyum_sulfat

    # Gram cinsinden hesaplama (1000 litre için) - Makro besinler
    gubre_miktarlari_gram = {}
    try:
        for gubre, besinler in gubre_miktarlari_mmol.items():
            if gubre not in gubreler:
                logger.error(f"Hata: '{gubre}' gübresi veritabanında bulunamadı!")
                st.error(f"Hata: '{gubre}' gübresi veritabanında bulunamadı! Lütfen gubreler.json dosyasını kontrol edin veya güncelleyin.")
                continue
            
            gubre_bilgi = gubreler[gubre]
            try:
                if gubre == "Amonyum Sülfat":
                    miktar_mmol = besinler["NH4"]
                    miktar_gram = (miktar_mmol / (0.272 / 18)) * gubre_bilgi["agirlik"] if miktar_mmol > 0 else 0.0
                elif gubre == "Mono Amonyum Fosfat":
                    miktar_mmol = besinler["NH4"]
                    miktar_gram = (miktar_mmol / (0.17 / 18)) * gubre_bilgi["agirlik"] if miktar_mmol > 0 else 0.0
                elif gubre == "Mono Potasyum Fosfat":
                    miktar_mmol = besinler["H2PO4"]
                    miktar_gram = (miktar_mmol / (0.225 / 31)) * gubre_bilgi["agirlik"] if miktar_mmol > 0 else 0.0
                elif gubre == "Potasyum Sülfat":
                    miktar_mmol = besinler["K"]
                    miktar_gram = (miktar_mmol / (0.45 / 39)) * gubre_bilgi["agirlik"] if miktar_mmol > 0 else 0.0
                elif gubre == "Potasyum Nitrat":
                    miktar_mmol = besinler["NO3"]
                    miktar_gram = (miktar_mmol / (0.135 / 14 * 62 / 62)) * gubre_bilgi["agirlik"] if miktar_mmol > 0 else 0.0
                elif gubre == "Magnezyum Nitrat":
                    miktar_mmol = besinler["Mg"]
                    miktar_gram = (miktar_mmol / (0.09 / 24)) * gubre_bilgi["agirlik"] if miktar_mmol > 0 else 0.0
                elif gubre == "Kalsiyum Nitrat":
                    miktar_mmol = besinler["Ca"]
                    miktar_gram = (miktar_mmol / (0.187 / 40)) * gubre_bilgi["agirlik"] if miktar_mmol > 0 else 0.0
                else:
                    miktar_mmol = besinler["Ca"] if "Ca" in besinler else besinler["NO3"]
                    miktar_gram = miktar_mmol * gubre_bilgi["agirlik"] if miktar_mmol > 0 else 0.0
                gubre_miktarlari_gram[gubre] = miktar_gram
            except Exception as e:
                logger.error(f"'{gubre}' gübresi için gram hesaplama sırasında bir hata oluştu: {str(e)}")
                st.error(f"'{gubre}' gübresi için gram hesaplama sırasında bir hata oluştu: {str(e)}")
                gubre_miktarlari_gram[gubre] = 0.0
    except Exception as e:
        logger.error(f"Gübre miktarlarını hesaplarken genel bir hata oluştu: {str(e)}")
        st.error(f"Gübre miktarlarını hesaplarken bir hata oluştu: {str(e)}")

    # Mikro besinler için gram cinsinden hesaplama (1000 litre için)
    for gubre, info in MIKRO_BESINLER.items():
        besin = info["besin"]
        ref_umol_L = info["ref_umol_L"]
        ref_mg_L = info["mg_L"]
        if besin in adjusted_recipe and adjusted_recipe[besin] > 0:
            gubre_miktarlari_gram[gubre] = (adjusted_recipe[besin] / ref_umol_L) * ref_mg_L
        else:
            gubre_miktarlari_gram[gubre] = 0.0

    return gubre_miktarlari_mmol, gubre_miktarlari_gram

def create_stock_solutions(gubre_miktarlari_gram: Dict[str, float], konsantrasyon: float) -> Tuple[Dict[str, float], Dict[str, float]]:
    """A ve B tanklarındaki stok çözeltileri hesaplar."""
    stok_a = {}
    stok_b = {}
    
    for gubre, miktar in gubre_miktarlari_gram.items():
        stok_miktar_kg = miktar / konsantrasyon
        if gubre in ["Kalsiyum Nitrat", "Magnezyum Nitrat", "Kalsiyum Hidroksit", "Calmag"]:
            stok_a[gubre] = stok_miktar_kg
        else:
            stok_b[gubre] = stok_miktar_kg
    
    return stok_a, stok_b

def check_tank_capacity(stok_a: Dict[str, float], stok_b: Dict[str, float], 
                      tank_a_hacim: float, tank_b_hacim: float, 
                      konsantrasyon: float) -> Dict[str, Any]:
    """Tank kapasitelerini kontrol eder ve uyarıları hazırlar."""
    warnings = {}
    max_kg_per_liter = 1.0  # 1 litre suya yaklaşık 1 kg çözelti sığar (yaklaşık bir değer)
    
    # Tank hacmi kontrolü
    total_stok_a_kg = sum(stok_a.values())
    total_stok_b_kg = sum(stok_b.values())
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
        suggested_konsantrasyon_a = konsantrasyon * (max_stok_a_kg / total_stok_a_kg) if total_stok_a_kg > 0 else konsantrasyon
        suggested_konsantrasyon_b = konsantrasyon * (max_stok_b_kg / total_stok_b_kg) if total_stok_b_kg > 0 else konsantrasyon
        suggested_konsantrasyon = min(suggested_konsantrasyon_a, suggested_konsantrasyon_b)
    else:
        suggested_konsantrasyon = konsantrasyon

    if total_stok_a_kg > tank_a_capacity_kg:
        warnings["tank_a"] = {
            "message": f"A tankı hacmi yetersiz! Toplam {total_stok_a_kg:.2f} kg stok çözelti gerekiyor, ancak tank sadece {tank_a_capacity_kg:.2f} kg alabilir.",
            "suggestions": [
                f"A tankı hacmini en az {min_tank_a_hacim:.2f} litreye çıkarın, veya",
                f"Stok konsantrasyon oranını {konsantrasyon:.1f}x yerine en az {suggested_konsantrasyon:.1f}x olarak ayarlayın."
            ]
        }
    
    if total_stok_b_kg > tank_b_capacity_kg:
        warnings["tank_b"] = {
            "message": f"B tankı hacmi yetersiz! Toplam {total_stok_b_kg:.2f} kg stok çözelti gerekiyor, ancak tank sadece {tank_b_capacity_kg:.2f} kg alabilir.",
