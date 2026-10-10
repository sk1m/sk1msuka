"""База техники Apple для сравнения (без AI).

Данные взяты из официальных характеристик Apple на момент выхода устройств.
Цена — стартовая в США в долларах, автономность — «просмотр видео до N часов»
(для Mac и iPhone) или «работа до N часов» (часы, наушники) по данным Apple.
Чтобы добавить устройство, допиши строку в нужный список — бот подхватит её сам.
"""

CATEGORIES = {
    "iphone": "📱 iPhone",
    "ipad": "📲 iPad",
    "mac": "💻 Mac",
    "watch": "⌚ Apple Watch",
    "airpods": "🎧 AirPods",
}

# Какие поля показываем в каждой категории: (ключ, подпись, что лучше: +1 больше, -1 меньше, 0 не сравниваем)
FIELDS = {
    "iphone": [("year", "Год выхода", 1), ("chip", "Процессор", 0), ("display", "Экран", 0), ("camera", "Основные камеры", 0),
               ("front", "Фронтальная", 0), ("battery", "Видео, до ч", 1), ("storage", "Память", 0), ("weight", "Вес", -1),
               ("unlock", "Разблокировка", 0), ("port", "Разъём", 0), ("price", "Цена на старте", -1), ("extra", "Фишки", 0)],
    "ipad": [("year", "Год выхода", 1), ("chip", "Процессор", 0), ("display", "Экран", 0), ("storage", "Память", 0),
             ("weight", "Вес", -1), ("unlock", "Разблокировка", 0), ("pencil", "Apple Pencil", 0),
             ("price", "Цена на старте", -1), ("extra", "Фишки", 0)],
    "mac": [("year", "Год выхода", 1), ("chip", "Процессор", 0), ("ram", "Оперативка (база), ГБ", 1), ("storage", "SSD (база)", 0),
            ("display", "Экран", 0), ("battery", "Видео, до ч", 1), ("weight", "Вес", -1),
            ("price", "Цена на старте", -1), ("extra", "Фишки", 0)],
    "watch": [("year", "Год выхода", 1), ("chip", "Процессор", 0), ("size", "Размеры корпуса", 0), ("battery", "Автономность, до ч", 1),
              ("price", "Цена на старте", -1), ("extra", "Фишки", 0)],
    "airpods": [("year", "Год выхода", 1), ("chip", "Чип", 0), ("anc", "Шумоподавление", 0), ("battery", "Работа, до ч", 1),
                ("case", "С кейсом, до ч", 1), ("port", "Зарядка", 0), ("price", "Цена на старте", -1), ("extra", "Фишки", 0)],
}


def _iphone(name, year, chip, display, camera, front, battery, storage, weight, unlock, port, price, extra, aliases=()):
    return dict(cat="iphone", name=name, year=year, chip=chip, display=display, camera=camera, front=front, battery=battery,
                storage=storage, weight=weight, unlock=unlock, port=port, price=price, extra=extra, aliases=list(aliases))


def _ipad(name, year, chip, display, storage, weight, unlock, pencil, price, extra, aliases=()):
    return dict(cat="ipad", name=name, year=year, chip=chip, display=display, storage=storage, weight=weight, unlock=unlock,
                pencil=pencil, price=price, extra=extra, aliases=list(aliases))


def _mac(name, year, chip, ram, storage, display, battery, weight, price, extra, aliases=()):
    return dict(cat="mac", name=name, year=year, chip=chip, ram=ram, storage=storage, display=display, battery=battery,
                weight=weight, price=price, extra=extra, aliases=list(aliases))


def _watch(name, year, chip, size, battery, price, extra, aliases=()):
    return dict(cat="watch", name=name, year=year, chip=chip, size=size, battery=battery, price=price, extra=extra, aliases=list(aliases))


def _pods(name, year, chip, anc, battery, case, port, price, extra, aliases=()):
    return dict(cat="airpods", name=name, year=year, chip=chip, anc=anc, battery=battery, case=case, port=port, price=price,
                extra=extra, aliases=list(aliases))


OLED60, OLED120 = "OLED 60 Гц", "OLED 120 Гц ProMotion"
P = "Face ID"

PRODUCTS = [
    # ---------------- iPhone ----------------
    _iphone("iPhone XR", 2018, "A12 Bionic", '6,1" LCD 60 Гц', "12 Мп", "7 Мп", 16, "64/128/256 ГБ", 194, P, "Lightning", 749, "6 цветов, одна камера", ["xr"]),
    _iphone("iPhone XS", 2018, "A12 Bionic", f'5,8" {OLED60}', "12 Мп + 12 Мп телевик 2×", "7 Мп", 14, "64/256/512 ГБ", 177, P, "Lightning", 999, "стальной корпус", ["xs"]),
    _iphone("iPhone XS Max", 2018, "A12 Bionic", f'6,5" {OLED60}', "12 Мп + 12 Мп телевик 2×", "7 Мп", 15, "64/256/512 ГБ", 208, P, "Lightning", 1099, "стальной корпус", ["xs max"]),
    _iphone("iPhone 11", 2019, "A13 Bionic", '6,1" LCD 60 Гц', "12 Мп + 12 Мп ширик", "12 Мп", 17, "64/128/256 ГБ", 194, P, "Lightning", 699, "ночной режим"),
    _iphone("iPhone 11 Pro", 2019, "A13 Bionic", f'5,8" {OLED60}', "12 Мп ×3 (ширик, телевик 2×)", "12 Мп", 18, "64/256/512 ГБ", 188, P, "Lightning", 999, "матовое стекло, сталь"),
    _iphone("iPhone 11 Pro Max", 2019, "A13 Bionic", f'6,5" {OLED60}', "12 Мп ×3 (ширик, телевик 2×)", "12 Мп", 20, "64/256/512 ГБ", 226, P, "Lightning", 1099, "матовое стекло, сталь"),
    _iphone("iPhone SE (2020)", 2020, "A13 Bionic", '4,7" LCD 60 Гц', "12 Мп", "7 Мп", 13, "64/128/256 ГБ", 148, "Touch ID", "Lightning", 399, "компактный, кнопка Домой", ["se 2", "se2", "se 2020"]),
    _iphone("iPhone 12 mini", 2020, "A14 Bionic", f'5,4" {OLED60}', "12 Мп + 12 Мп ширик", "12 Мп", 15, "64/128/256 ГБ", 135, P, "Lightning", 699, "5G, MagSafe, самый маленький"),
    _iphone("iPhone 12", 2020, "A14 Bionic", f'6,1" {OLED60}', "12 Мп + 12 Мп ширик", "12 Мп", 17, "64/128/256 ГБ", 164, P, "Lightning", 799, "5G, MagSafe"),
    _iphone("iPhone 12 Pro", 2020, "A14 Bionic", f'6,1" {OLED60}', "12 Мп ×3 (телевик 2×) + LiDAR", "12 Мп", 17, "128/256/512 ГБ", 189, P, "Lightning", 999, "5G, MagSafe, ProRAW"),
    _iphone("iPhone 12 Pro Max", 2020, "A14 Bionic", f'6,7" {OLED60}', "12 Мп ×3 (телевик 2,5×) + LiDAR", "12 Мп", 20, "128/256/512 ГБ", 228, P, "Lightning", 1099, "5G, MagSafe, стабилизация сдвигом матрицы"),
    _iphone("iPhone 13 mini", 2021, "A15 Bionic (4 ядра GPU)", f'5,4" {OLED60}', "12 Мп + 12 Мп ширик", "12 Мп", 17, "128/256/512 ГБ", 140, P, "Lightning", 699, "киноэффект, компактный"),
    _iphone("iPhone 13", 2021, "A15 Bionic (4 ядра GPU)", f'6,1" {OLED60}', "12 Мп + 12 Мп ширик", "12 Мп", 19, "128/256/512 ГБ", 173, P, "Lightning", 799, "киноэффект"),
    _iphone("iPhone 13 Pro", 2021, "A15 Bionic (5 ядер GPU)", f'6,1" {OLED120}', "12 Мп ×3 (телевик 3×) + LiDAR", "12 Мп", 22, "128 ГБ – 1 ТБ", 203, P, "Lightning", 999, "120 Гц, макросъёмка, ProRes"),
    _iphone("iPhone 13 Pro Max", 2021, "A15 Bionic (5 ядер GPU)", f'6,7" {OLED120}', "12 Мп ×3 (телевик 3×) + LiDAR", "12 Мп", 28, "128 ГБ – 1 ТБ", 238, P, "Lightning", 1099, "120 Гц, макросъёмка, ProRes"),
    _iphone("iPhone SE (2022)", 2022, "A15 Bionic", '4,7" LCD 60 Гц', "12 Мп", "7 Мп", 15, "64/128/256 ГБ", 144, "Touch ID", "Lightning", 429, "5G, кнопка Домой", ["se 3", "se3", "se 2022"]),
    _iphone("iPhone 14", 2022, "A15 Bionic (5 ядер GPU)", f'6,1" {OLED60}', "12 Мп + 12 Мп ширик", "12 Мп с автофокусом", 20, "128/256/512 ГБ", 172, P, "Lightning", 799, "SOS через спутник, распознавание аварий"),
    _iphone("iPhone 14 Plus", 2022, "A15 Bionic (5 ядер GPU)", f'6,7" {OLED60}', "12 Мп + 12 Мп ширик", "12 Мп с автофокусом", 26, "128/256/512 ГБ", 203, P, "Lightning", 899, "большой экран, SOS через спутник"),
    _iphone("iPhone 14 Pro", 2022, "A16 Bionic", f'6,1" {OLED120}, Always-On', "48 Мп + 12 Мп ширик + 12 Мп телевик 3×", "12 Мп с автофокусом", 23, "128 ГБ – 1 ТБ", 206, P, "Lightning", 999, "Dynamic Island, Always-On"),
    _iphone("iPhone 14 Pro Max", 2022, "A16 Bionic", f'6,7" {OLED120}, Always-On', "48 Мп + 12 Мп ширик + 12 Мп телевик 3×", "12 Мп с автофокусом", 29, "128 ГБ – 1 ТБ", 240, P, "Lightning", 1099, "Dynamic Island, Always-On"),
    _iphone("iPhone 15", 2023, "A16 Bionic", f'6,1" {OLED60}', "48 Мп + 12 Мп ширик", "12 Мп", 20, "128/256/512 ГБ", 171, P, "USB-C (USB 2)", 799, "Dynamic Island, матовое стекло"),
    _iphone("iPhone 15 Plus", 2023, "A16 Bionic", f'6,7" {OLED60}', "48 Мп + 12 Мп ширик", "12 Мп", 26, "128/256/512 ГБ", 201, P, "USB-C (USB 2)", 899, "Dynamic Island, большой экран"),
    _iphone("iPhone 15 Pro", 2023, "A17 Pro", f'6,1" {OLED120}, Always-On', "48 Мп + 12 Мп ширик + 12 Мп телевик 3×", "12 Мп", 23, "128 ГБ – 1 ТБ", 187, P, "USB-C (USB 3)", 999, "титан, кнопка действия, Apple Intelligence"),
    _iphone("iPhone 15 Pro Max", 2023, "A17 Pro", f'6,7" {OLED120}, Always-On', "48 Мп + 12 Мп ширик + 12 Мп телевик 5×", "12 Мп", 29, "256 ГБ – 1 ТБ", 221, P, "USB-C (USB 3)", 1199, "титан, телевик 5×, Apple Intelligence"),
    _iphone("iPhone 16e", 2025, "A18 (4 ядра GPU)", f'6,1" {OLED60}, «чёлка»', "48 Мп", "12 Мп", 26, "128/256/512 ГБ", 167, P, "USB-C (USB 2)", 599, "кнопка действия, Apple Intelligence, без MagSafe", ["16 e"]),
    _iphone("iPhone 16", 2024, "A18", f'6,1" {OLED60}', "48 Мп + 12 Мп ширик", "12 Мп", 22, "128/256/512 ГБ", 170, P, "USB-C (USB 2)", 799, "кнопка камеры, кнопка действия, Apple Intelligence"),
    _iphone("iPhone 16 Plus", 2024, "A18", f'6,7" {OLED60}', "48 Мп + 12 Мп ширик", "12 Мп", 27, "128/256/512 ГБ", 199, P, "USB-C (USB 2)", 899, "кнопка камеры, большой экран"),
    _iphone("iPhone 16 Pro", 2024, "A18 Pro", f'6,3" {OLED120}, Always-On', "48 Мп + 48 Мп ширик + 12 Мп телевик 5×", "12 Мп", 27, "128 ГБ – 1 ТБ", 199, P, "USB-C (USB 3)", 999, "титан, видео 4K 120 к/с, кнопка камеры"),
    _iphone("iPhone 16 Pro Max", 2024, "A18 Pro", f'6,9" {OLED120}, Always-On', "48 Мп + 48 Мп ширик + 12 Мп телевик 5×", "12 Мп", 33, "256 ГБ – 1 ТБ", 227, P, "USB-C (USB 3)", 1199, "титан, самый большой экран, видео 4K 120 к/с"),
    _iphone("iPhone 17", 2025, "A19", f'6,3" {OLED120}, Always-On', "48 Мп + 48 Мп ширик", "18 Мп Center Stage", 30, "256/512 ГБ", 177, P, "USB-C (USB 2)", 799, "120 Гц в базовой модели, Ceramic Shield 2"),
    _iphone("iPhone Air", 2025, "A19 Pro", f'6,5" {OLED120}, Always-On', "48 Мп", "18 Мп Center Stage", 27, "256 ГБ – 1 ТБ", 165, P, "USB-C (USB 2)", 999, "толщина 5,6 мм, титан, только eSIM", ["air", "17 air", "эйр"]),
    _iphone("iPhone 17 Pro", 2025, "A19 Pro", f'6,3" {OLED120}, Always-On', "48 Мп ×3 (телевик 4×)", "18 Мп Center Stage", 33, "256 ГБ – 1 ТБ", 204, P, "USB-C (USB 3)", 1099, "алюминиевый корпус, испарительная камера охлаждения"),
    _iphone("iPhone 17 Pro Max", 2025, "A19 Pro", f'6,9" {OLED120}, Always-On', "48 Мп ×3 (телевик 4×)", "18 Мп Center Stage", 39, "256 ГБ – 2 ТБ", 231, P, "USB-C (USB 3)", 1199, "рекордная автономность, до 2 ТБ"),

    # ---------------- iPad ----------------
    _ipad("iPad 9", 2021, "A13 Bionic", '10,2" LCD', "64/256 ГБ", 487, "Touch ID (кнопка Домой)", "1-го поколения", 329, "Lightning, последний с кнопкой Домой", ["ipad 2021", "ipad 9th"]),
    _ipad("iPad 10", 2022, "A14 Bionic", '10,9" LCD', "64/256 ГБ", 477, "Touch ID (верхняя кнопка)", "1-го поколения, USB-C", 449, "USB-C, новый дизайн", ["ipad 2022", "ipad 10th"]),
    _ipad("iPad (A16)", 2025, "A16", '11" LCD', "128/256/512 ГБ", 477, "Touch ID (верхняя кнопка)", "USB-C", 349, "больше памяти в базе", ["ipad 11", "ipad a16", "ipad 2025"]),
    _ipad("iPad mini 6", 2021, "A15 Bionic", '8,3" LCD', "64/256 ГБ", 293, "Touch ID (верхняя кнопка)", "2-го поколения", 499, "компактный, USB-C, 5G", ["mini 6"]),
    _ipad("iPad mini (A17 Pro)", 2024, "A17 Pro", '8,3" LCD', "128/256/512 ГБ", 293, "Touch ID (верхняя кнопка)", "Pro, USB-C", 499, "Apple Intelligence", ["mini 7", "ipad mini 7", "ipad mini a17"]),
    _ipad("iPad Air M1", 2022, "M1", '10,9" LCD', "64/256 ГБ", 461, "Touch ID (верхняя кнопка)", "2-го поколения", 599, "5G, Center Stage", ["air 5", "ipad air 5"]),
    _ipad('iPad Air 11" M2', 2024, "M2", '11" LCD', "128 ГБ – 1 ТБ", 462, "Touch ID (верхняя кнопка)", "Pro, USB-C", 599, "Apple Intelligence", ["air m2 11"]),
    _ipad('iPad Air 13" M2', 2024, "M2", '13" LCD', "128 ГБ – 1 ТБ", 617, "Touch ID (верхняя кнопка)", "Pro, USB-C", 799, "большой экран", ["air m2 13"]),
    _ipad('iPad Air 11" M3', 2025, "M3", '11" LCD', "128 ГБ – 1 ТБ", 460, "Touch ID (верхняя кнопка)", "Pro, USB-C", 599, "Apple Intelligence", ["air m3 11"]),
    _ipad('iPad Air 13" M3', 2025, "M3", '13" LCD', "128 ГБ – 1 ТБ", 616, "Touch ID (верхняя кнопка)", "Pro, USB-C", 799, "большой экран", ["air m3 13"]),
    _ipad('iPad Pro 11" M2', 2022, "M2", '11" LCD 120 Гц ProMotion', "128 ГБ – 2 ТБ", 466, "Face ID", "2-го поколения, наведение", 799, "LiDAR, Thunderbolt", ["pro m2 11"]),
    _ipad('iPad Pro 12,9" M2', 2022, "M2", '12,9" mini-LED 120 Гц ProMotion', "128 ГБ – 2 ТБ", 682, "Face ID", "2-го поколения, наведение", 1099, "mini-LED, Thunderbolt", ["pro m2 12.9", "pro m2 13"]),
    _ipad('iPad Pro 11" M4', 2024, "M4", '11" Tandem OLED 120 Гц', "256 ГБ – 2 ТБ", 444, "Face ID", "Pro, USB-C", 999, "OLED, толщина 5,3 мм", ["pro m4 11"]),
    _ipad('iPad Pro 13" M4', 2024, "M4", '13" Tandem OLED 120 Гц', "256 ГБ – 2 ТБ", 579, "Face ID", "Pro, USB-C", 1299, "OLED, толщина 5,1 мм", ["pro m4 13"]),
    _ipad('iPad Pro 11" M5', 2025, "M5", '11" Tandem OLED 120 Гц', "256 ГБ – 2 ТБ", 444, "Face ID", "Pro, USB-C", 999, "OLED, быстрее на AI-задачах", ["pro m5 11"]),
    _ipad('iPad Pro 13" M5', 2025, "M5", '13" Tandem OLED 120 Гц', "256 ГБ – 2 ТБ", 579, "Face ID", "Pro, USB-C", 1299, "OLED, быстрее на AI-задачах", ["pro m5 13"]),

    # ---------------- Mac ----------------
    _mac("MacBook Air M1", 2020, "M1", 8, "256 ГБ", '13,3" Retina', 18, 1.29, 999, "без вентилятора", ["air m1", "macbook m1"]),
    _mac('MacBook Air 13" M2', 2022, "M2", 8, "256 ГБ", '13,6" Liquid Retina', 18, 1.24, 1199, "MagSafe, без вентилятора", ["air m2", "air 13 m2"]),
    _mac('MacBook Air 15" M2', 2023, "M2", 8, "256 ГБ", '15,3" Liquid Retina', 18, 1.51, 1299, "большой экран, без вентилятора", ["air 15 m2"]),
    _mac('MacBook Air 13" M3', 2024, "M3", 8, "256 ГБ", '13,6" Liquid Retina', 18, 1.24, 1099, "2 внешних монитора с закрытой крышкой, с осени 2024 — 16 ГБ в базе", ["air m3", "air 13 m3"]),
    _mac('MacBook Air 15" M3', 2024, "M3", 8, "256 ГБ", '15,3" Liquid Retina', 18, 1.51, 1299, "большой экран, с осени 2024 — 16 ГБ в базе", ["air 15 m3"]),
    _mac('MacBook Air 13" M4', 2025, "M4", 16, "256 ГБ", '13,6" Liquid Retina', 18, 1.24, 999, "2 внешних монитора при открытой крышке, камера 12 Мп", ["air m4", "air 13 m4"]),
    _mac('MacBook Air 15" M4', 2025, "M4", 16, "256 ГБ", '15,3" Liquid Retina', 18, 1.51, 1199, "большой экран, камера 12 Мп", ["air 15 m4"]),
    _mac('MacBook Pro 14" M1 Pro', 2021, "M1 Pro", 16, "512 ГБ", '14,2" mini-LED 120 Гц', 17, 1.6, 1999, "HDMI, SD, MagSafe", ["pro m1 pro 14", "mbp m1 pro"]),
    _mac('MacBook Pro 16" M1 Pro', 2021, "M1 Pro", 16, "512 ГБ", '16,2" mini-LED 120 Гц', 21, 2.1, 2499, "HDMI, SD, MagSafe", ["pro m1 pro 16"]),
    _mac('MacBook Pro 14" M2 Pro', 2023, "M2 Pro", 16, "512 ГБ", '14,2" mini-LED 120 Гц', 18, 1.6, 1999, "HDMI 8K, Wi-Fi 6E", ["pro m2 pro 14"]),
    _mac('MacBook Pro 16" M2 Pro', 2023, "M2 Pro", 16, "512 ГБ", '16,2" mini-LED 120 Гц', 22, 2.15, 2499, "HDMI 8K, Wi-Fi 6E", ["pro m2 pro 16"]),
    _mac('MacBook Pro 14" M3', 2023, "M3", 8, "512 ГБ", '14,2" mini-LED 120 Гц', 22, 1.55, 1599, "самый доступный 14-дюймовый Pro", ["pro m3 14", "mbp m3"]),
    _mac('MacBook Pro 14" M3 Pro', 2023, "M3 Pro", 18, "512 ГБ", '14,2" mini-LED 120 Гц', 18, 1.61, 1999, "цвет «чёрный космос»", ["pro m3 pro 14"]),
    _mac('MacBook Pro 16" M3 Pro', 2023, "M3 Pro", 18, "512 ГБ", '16,2" mini-LED 120 Гц', 22, 2.14, 2499, "цвет «чёрный космос»", ["pro m3 pro 16"]),
    _mac('MacBook Pro 14" M4', 2024, "M4", 16, "512 ГБ", '14,2" mini-LED 120 Гц', 24, 1.55, 1599, "Thunderbolt 4 ×3, опция нано-текстуры", ["pro m4 14", "mbp m4"]),
    _mac('MacBook Pro 14" M4 Pro', 2024, "M4 Pro", 24, "512 ГБ", '14,2" mini-LED 120 Гц', 22, 1.6, 1999, "Thunderbolt 5", ["pro m4 pro 14"]),
    _mac('MacBook Pro 16" M4 Pro', 2024, "M4 Pro", 24, "512 ГБ", '16,2" mini-LED 120 Гц', 24, 2.14, 2499, "Thunderbolt 5", ["pro m4 pro 16"]),
    _mac('MacBook Pro 14" M5', 2025, "M5", 16, "512 ГБ", '14,2" mini-LED 120 Гц', 24, 1.55, 1599, "быстрее на AI-задачах и в играх", ["pro m5 14", "mbp m5"]),
    _mac('iMac 24" M1', 2021, "M1", 8, "256 ГБ", '24" 4.5K Retina', None, 4.46, 1299, "моноблок, 7 цветов", ["imac m1"]),
    _mac('iMac 24" M3', 2023, "M3", 8, "256 ГБ", '24" 4.5K Retina', None, 4.43, 1299, "моноблок", ["imac m3"]),
    _mac('iMac 24" M4', 2024, "M4", 16, "256 ГБ", '24" 4.5K Retina', None, 4.44, 1299, "моноблок, камера 12 Мп, аксессуары с USB-C", ["imac m4"]),
    _mac("Mac mini M1", 2020, "M1", 8, "256 ГБ", "нет (свой монитор)", None, 1.2, 699, "неттоп", ["mini m1"]),
    _mac("Mac mini M2", 2023, "M2", 8, "256 ГБ", "нет (свой монитор)", None, 1.18, 599, "неттоп", ["mini m2"]),
    _mac("Mac mini M4", 2024, "M4", 16, "256 ГБ", "нет (свой монитор)", None, 0.67, 599, "размер 12,7 × 12,7 см, порты спереди", ["mini m4"]),
    _mac("Mac mini M4 Pro", 2024, "M4 Pro", 24, "512 ГБ", "нет (свой монитор)", None, 0.73, 1399, "Thunderbolt 5", ["mini m4 pro"]),
    _mac("Mac Studio M1 Max", 2022, "M1 Max", 32, "512 ГБ", "нет (свой монитор)", None, 2.7, 1999, "для монтажа и 3D", ["studio m1 max"]),
    _mac("Mac Studio M2 Max", 2023, "M2 Max", 32, "512 ГБ", "нет (свой монитор)", None, 2.7, 1999, "для монтажа и 3D", ["studio m2 max"]),
    _mac("Mac Studio M4 Max", 2025, "M4 Max", 36, "512 ГБ", "нет (свой монитор)", None, 2.74, 1999, "Thunderbolt 5", ["studio m4 max"]),
    _mac("Mac Studio M3 Ultra", 2025, "M3 Ultra", 96, "1 ТБ", "нет (свой монитор)", None, 3.64, 3999, "до 512 ГБ оперативки, топ для профи", ["studio m3 ultra"]),

    # ---------------- Apple Watch ----------------
    _watch("Apple Watch SE 2", 2022, "S8", "40 / 44 мм", 18, 249, "распознавание аварий", ["se 2 watch", "watch se 2"]),
    _watch("Apple Watch SE 3", 2025, "S10", "40 / 44 мм", 18, 249, "Always-On, быстрая зарядка", ["watch se 3"]),
    _watch("Apple Watch Series 9", 2023, "S9", "41 / 45 мм", 18, 399, "двойное касание", ["watch 9", "series 9", "s9"]),
    _watch("Apple Watch Series 10", 2024, "S10", "42 / 46 мм", 18, 399, "самые тонкие, широкоугольный OLED", ["watch 10", "series 10", "s10"]),
    _watch("Apple Watch Series 11", 2025, "S10", "42 / 46 мм", 24, 399, "5G, уведомления о давлении", ["watch 11", "series 11", "s11"]),
    _watch("Apple Watch Ultra 2", 2023, "S9", "49 мм титан", 36, 799, "яркость 3000 нит, точный GPS", ["ultra 2"]),
    _watch("Apple Watch Ultra 3", 2025, "S10", "49 мм титан", 42, 799, "SOS через спутник, 5G", ["ultra 3"]),

    # ---------------- AirPods ----------------
    _pods("AirPods 4", 2024, "H2", "нет", 5, 30, "USB-C", 129, "новая форма, лучше сидят", ["airpods 4"]),
    _pods("AirPods 4 с шумоподавлением", 2024, "H2", "да", 5, 30, "USB-C + беспроводная", 179, "шумоподавление в открытых наушниках", ["airpods 4 anc"]),
    _pods("AirPods Pro 2", 2022, "H2", "да", 6, 30, "USB-C (с 2023), MagSafe", 249, "адаптивный звук, функция слухового аппарата", ["pro 2", "airpods pro 2"]),
    _pods("AirPods Pro 3", 2025, "H2", "да, сильнее", 8, 24, "USB-C, беспроводная", 249, "пульсометр, живой перевод", ["pro 3", "airpods pro 3"]),
    _pods("AirPods Max", 2020, "H1", "да", 20, None, "Lightning, с 2024 — USB-C", 549, "полноразмерные", ["max", "airpods max"]),
]

for i, p in enumerate(PRODUCTS):
    p["id"] = i

# ---------- поиск модели по тексту ----------
import re

PHRASES = [("мак мини", "mac mini"), ("эпл вотч", "watch"), ("эпл вотч", "watch"), ("про макс", "pro max")]
WORDS = {"айфон": "iphone", "айфона": "iphone", "айпад": "ipad", "макбук": "macbook", "аймак": "imac", "мак": "mac",
         "вотч": "watch", "часы": "watch", "аирподс": "airpods", "эйрподс": "airpods", "аирпод": "airpods", "аирпods": "airpods",
         "промакс": "pro max", "promax": "pro max", "про": "pro", "макс": "max", "мини": "mini", "плюс": "plus", "эйр": "air",
         "аир": "air", "ультра": "ultra", "серия": "series", "се": "se", "м1": "m1", "м2": "m2", "м3": "m3", "м4": "m4", "м5": "m5", "шумоподавлением": "anc", "шумодавом": "anc"}


def _norm(text: str) -> str:
    t = text.lower().replace("ё", "е")
    t = re.sub(r"[\"”“«»(),!?]", " ", t).replace("-", " ")
    t = re.sub(r"(iphone|айфон|ipad|айпад)(\d)", r"\1 \2", t)   # iphone15 -> iphone 15
    for a, b in PHRASES:
        t = t.replace(a, b)
    return " ".join(WORDS.get(w, w) for w in t.split())


def _tokens(text: str) -> set[str]:
    return set(_norm(text).split()) - {"apple", "с", "the"}


for p in PRODUCTS:
    p["_tok"] = _tokens(p["name"])
    p["_alias"] = [_tokens(a) for a in p["aliases"]]


def find(query: str):
    """Находит устройство по тексту вроде «15 про макс» или «air m2»."""
    q = _tokens(query)
    if not q:
        return None
    best, best_extra = None, 99
    for p in PRODUCTS:
        for variant in [p["_tok"], *p["_alias"]]:
            if q <= variant:
                extra = len(variant - q)
                if extra < best_extra:
                    best, best_extra = p, extra
    return best


SEPARATORS = [" vs ", " versus ", " или ", " против ", " и ", " / ", ";", "|", "\n"]


def find_many(text: str) -> list[dict]:
    """Разбивает «iPhone 15 vs 16 Pro» на модели. Номер без названия наследует семейство предыдущей модели."""
    stop = {"сравни", "сравнить", "сравнение", "что", "лучше", "какой", "какую", "выбрать", "или?"}
    t = " " + " ".join(w for w in _norm(text.replace("\n", " | ")).split() if w not in stop) + " "
    for s in SEPARATORS:
        t = t.replace(s, " | ")
    parts = [x.strip() for x in t.split("|") if x.strip()]
    found, family = [], ""
    for part in parts:
        p = find(part)
        if not p and family:
            p = find(f"{family} {part}")
        if p and p not in found:
            found.append(p)
            family = {"iphone": "iphone", "ipad": "ipad", "watch": "watch", "airpods": "airpods"}.get(p["cat"], "")
    return found


# ---------- вывод ----------
def _val(p, key):
    v = p.get(key)
    if v is None:
        return "—"
    if key == "price":
        return f"${v:,}".replace(",", " ")
    if key == "weight":
        return f"{v:g} кг".replace(".", ",") if p["cat"] == "mac" else f"{v} г"
    return str(v)


def _num(p, key):
    """Число для сравнения: вес Mac хранится в кг, остальных — в граммах."""
    v = p.get(key)
    if key == "weight" and p["cat"] == "mac" and v is not None:
        return v * 1000
    return v


def card(p) -> str:
    lines = [f"{CATEGORIES[p['cat']].split()[0]} <b>{p['name']}</b>", ""]
    for key, label, _ in FIELDS[p["cat"]]:
        if p.get(key) is not None:
            lines.append(f"• {label}: {_val(p, key)}")
    return "\n".join(lines)


def compare(items: list[dict]) -> str:
    """Сравнение 2–3 устройств: по каждой характеристике, ✅ у лучшего значения."""
    cats = {p["cat"] for p in items}
    if len(cats) == 1:
        fields = FIELDS[items[0]["cat"]]
    else:  # разные категории — только общие поля
        common = set.intersection(*({k for k, _, _ in FIELDS[c]} for c in cats))
        fields = [f for f in FIELDS[items[0]["cat"]] if f[0] in common]
    wins = {p["id"]: 0 for p in items}
    out = ["⚖️ <b>" + " vs ".join(p["name"] for p in items) + "</b>"]
    for key, label, better in fields:
        vals = [_num(p, key) for p in items]
        if all(v is None for v in vals):
            continue
        best = None
        nums = [v for v in vals if isinstance(v, (int, float))]
        if better and len(nums) == len(vals) and len(set(nums)) > 1:
            best = max(nums) if better > 0 else min(nums)
        out.append(f"\n<b>{label}</b>")
        for p, v in zip(items, vals):
            mark = " ✅" if best is not None and v == best else ""
            if mark:
                wins[p["id"]] += 1
            out.append(f"  {p['name']}: {_val(p, key)}{mark}")
    out.append("\n🏁 <b>Итог</b>")
    out += [f"  {p['name']}: побед {wins[p['id']]}" for p in items]
    leader = max(items, key=lambda p: wins[p["id"]])
    if list(wins.values()).count(wins[leader["id"]]) == 1:
        out.append(f"\nПо цифрам впереди <b>{leader['name']}</b>. Но смотри на то, что важно тебе: камера, размер, цена.")
    else:
        out.append("\nПо цифрам примерно на равных — выбирай по размеру, цене и фишкам.")
    out.append("\n<i>✅ — лучше в этом пункте. Цены стартовые в США на момент выхода.</i>")
    return "\n".join(out)


def by_cat(cat: str) -> list[dict]:
    return sorted((p for p in PRODUCTS if p["cat"] == cat), key=lambda p: (p["year"], p["price"]), reverse=True)
