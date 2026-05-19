"""
Ma'lumotlar fayli — bu yerda kategoriya va mahsulotlarni tahrirlang.

Har bir mahsulotda:
  name  → 3 tilda nomi
  price → 3 tilda narxi (string, masalan "150,000 so'm / 14$ / 1200₽")
  usage → 3 tilda qisqacha tavsif / ishlatilishi
  image → rasm URL yoki Telegram file_id  (bo'lmasa None qoldiring)
"""

# ─── Kategoriyalar ────────────────────────────────────────────────────────────
CATEGORIES = {
    "electronics": {
        "name": {
            "uz": "💻 Elektronika",
            "ru": "💻 Электроника",
            "en": "💻 Electronics",
        }
    },
    "household": {
        "name": {
            "uz": "🏠 Maishiy texnika",
            "ru": "🏠 Бытовая техника",
            "en": "🏠 Home Appliances",
        }
    },
    "cosmetics": {
        "name": {
            "uz": "💄 Kosmetika",
            "ru": "💄 Косметика",
            "en": "💄 Cosmetics",
        }
    },
}

# ─── Mahsulotlar (kategoriya ID → mahsulot ID → ma'lumot) ─────────────────────
PRODUCTS = {

    # ── Elektronika ────────────────────────────────────────────────────────────
    "electronics": {
        "laptop_pro": {
            "name": {
                "uz": "LaptopPro X500",
                "ru": "LaptopPro X500",
                "en": "LaptopPro X500",
            },
            "price": {
                "uz": "12,500,000 so'm",
                "ru": "1 150 $",
                "en": "$1,150",
            },
            "usage": {
                "uz": "Dasturlash, grafik dizayn va kundalik ishlar uchun mo'ljallangan yuqori unumdorlikli noutbuk.",
                "ru": "Высокопроизводительный ноутбук для программирования, графического дизайна и повседневных задач.",
                "en": "High-performance laptop designed for programming, graphic design, and everyday tasks.",
            },
            "image": "https://images.unsplash.com/photo-1496181133206-80ce9b88a853?w=800",
        },
        "smartphone_z": {
            "name": {
                "uz": "SmartPhone Z12",
                "ru": "SmartPhone Z12",
                "en": "SmartPhone Z12",
            },
            "price": {
                "uz": "5,800,000 so'm",
                "ru": "540 $",
                "en": "$540",
            },
            "usage": {
                "uz": "Yuqori sifatli kamera, uzoq batareya va tez protsessor bilan jihozlangan zamonaviy smartfon.",
                "ru": "Современный смартфон с камерой высокого качества, длительным аккумулятором и быстрым процессором.",
                "en": "Modern smartphone with high-quality camera, long battery life, and fast processor.",
            },
            "image": "https://images.unsplash.com/photo-1511707171634-5f897ff02aa9?w=800",
        },
        "wireless_earbuds": {
            "name": {
                "uz": "AirBuds Pro",
                "ru": "AirBuds Pro",
                "en": "AirBuds Pro",
            },
            "price": {
                "uz": "890,000 so'm",
                "ru": "82 $",
                "en": "$82",
            },
            "usage": {
                "uz": "Aktiv shovqin bekor qilish va 30 soatlik batareya bilan simsiz quloqchinlar.",
                "ru": "Беспроводные наушники с активным шумоподавлением и 30-часовым аккумулятором.",
                "en": "Wireless earbuds with active noise cancellation and 30-hour battery life.",
            },
            "image": "https://images.unsplash.com/photo-1590658268037-6bf12165a8df?w=800",
        },
    },

    # ── Maishiy texnika ────────────────────────────────────────────────────────
    "household": {
        "vacuum_cleaner": {
            "name": {
                "uz": "TurboClean 3000",
                "ru": "TurboClean 3000",
                "en": "TurboClean 3000",
            },
            "price": {
                "uz": "2,100,000 so'm",
                "ru": "195 $",
                "en": "$195",
            },
            "usage": {
                "uz": "Kuchli so'rish quvvati va HEPA filtri bilan uy uchun simsiz changyutgich.",
                "ru": "Беспроводной пылесос для дома с мощным всасыванием и HEPA-фильтром.",
                "en": "Cordless home vacuum with powerful suction and HEPA filter.",
            },
            "image": "https://images.unsplash.com/photo-1558618666-fcd25c85cd64?w=800",
        },
        "air_purifier": {
            "name": {
                "uz": "PureAir 500",
                "ru": "PureAir 500",
                "en": "PureAir 500",
            },
            "price": {
                "uz": "1,650,000 so'm",
                "ru": "152 $",
                "en": "$152",
            },
            "usage": {
                "uz": "Allergiya va chang zarrachalarini ushlab, xonadagi havoni tozalaydigan havo tozalagich.",
                "ru": "Очиститель воздуха, задерживающий аллергены и пыль для чистого воздуха в комнате.",
                "en": "Air purifier that captures allergens and dust particles for clean indoor air.",
            },
            "image": "https://images.unsplash.com/photo-1585771724684-38269d6639fd?w=800",
        },
    },

    # ── Kosmetika ──────────────────────────────────────────────────────────────
    "cosmetics": {
        "face_serum": {
            "name": {
                "uz": "GlowUp Serum",
                "ru": "GlowUp Serum",
                "en": "GlowUp Serum",
            },
            "price": {
                "uz": "320,000 so'm",
                "ru": "30 $",
                "en": "$30",
            },
            "usage": {
                "uz": "Yuz terisini namlantirib, yorqinlashtiruvchi va qarilikka qarshi C vitamini serumi.",
                "ru": "Сыворотка с витамином C для увлажнения, осветления и антивозрастного ухода за кожей лица.",
                "en": "Vitamin C serum for moisturizing, brightening, and anti-aging facial skincare.",
            },
            "image": "https://images.unsplash.com/photo-1620916566398-39f1143ab7be?w=800",
        },
        "lip_gloss": {
            "name": {
                "uz": "ShineGloss No.7",
                "ru": "ShineGloss No.7",
                "en": "ShineGloss No.7",
            },
            "price": {
                "uz": "95,000 so'm",
                "ru": "9 $",
                "en": "$9",
            },
            "usage": {
                "uz": "Labni namlantirib, tabiiy jilolaydigan, uzoq muddatli lip gloss.",
                "ru": "Увлажняющий блеск для губ с натуральным блеском и длительным эффектом.",
                "en": "Moisturizing lip gloss with natural shine and long-lasting effect.",
            },
            "image": "https://images.unsplash.com/photo-1512496015851-a90fb38ba796?w=800",
        },
    },
}
