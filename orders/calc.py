"""Единый расчёт оптового заказа: стоимость, вес, объём, паллеты, контейнеры.

Используется калькулятором, оформлением заказа и коммерческим предложением,
поэтому цифры везде совпадают. Загрузка контейнера — предварительная оценка.
"""
from decimal import Decimal
from itertools import permutations
from math import ceil, floor

from catalog.models import Product, price_map

# Внутренние размеры (см), объём (м³) и макс. полезная нагрузка (кг) стандартных контейнеров.
CONTAINERS = {
    "20": {"dims": (589, 235, 239), "volume": 33.2, "payload": 28200},
    "40": {"dims": (1203, 235, 239), "volume": 67.7, "payload": 26700},
}
FALLBACK_FILL = 0.85  # коэффициент заполнения, если габариты коробки не заданы
MAX_BOXES = 100_000


def boxes_fit(box_dims, container_dims):
    """Сколько коробок помещается в контейнер при лучшей из 6 ориентаций (укладка рядами)."""
    best = 0
    for l, w, h in set(permutations(box_dims)):
        n = floor(container_dims[0] / l) * floor(container_dims[1] / w) * floor(container_dims[2] / h)
        best = max(best, n)
    return best


def parse_items(raw):
    """[{id, boxes}] -> {product_id: boxes}; мусор и нулевые количества отбрасываются."""
    result = {}
    for row in raw if isinstance(raw, list) else []:
        try:
            pid, boxes = int(row["id"]), int(row["boxes"])
        except (KeyError, TypeError, ValueError):
            continue
        if 0 < boxes <= MAX_BOXES:
            result[pid] = boxes
    return result


def calculate(items, country=None):
    """items: {product_id: boxes}. country=None — без цен (посетитель без доступа)."""
    prices = price_map(country) if country else {}
    products = Product.objects.filter(pk__in=items, is_active=True).select_related("weight", "flavor")
    lines = []
    total_amount = Decimal(0)
    total_boxes = 0
    weight = Decimal(0)
    volume = Decimal(0)
    weight_complete = volume_complete = pallets_complete = True
    pallets = 0.0
    load = {key: 0.0 for key in CONTAINERS}

    for p in products:
        boxes = items[p.pk]
        price = prices.get(p.pk)
        if country and price is None:
            continue  # товар скрыт из прайса страны — в расчёт не попадает
        amount = price * boxes if price is not None else None
        line_weight = p.gross_weight_kg * boxes if p.gross_weight_kg else None
        line_volume = p.volume_m3 * boxes if p.volume_m3 else None
        lines.append({
            "id": p.pk, "name": p.name, "weight_g": p.weight.grams, "boxes": boxes,
            "packs": p.packs_per_box * boxes if p.packs_per_box else None,
            "price": price, "amount": amount, "weight_kg": line_weight, "volume_m3": line_volume,
        })
        total_boxes += boxes
        if amount is not None:
            total_amount += amount
        if line_weight is None:
            weight_complete = False
        else:
            weight += line_weight
        if line_volume is None:
            volume_complete = False
        else:
            volume += line_volume
        if p.boxes_per_pallet:
            pallets += boxes / p.boxes_per_pallet
        else:
            pallets_complete = False

        for key, c in CONTAINERS.items():
            capacity = 0
            if p.has_dimensions:
                dims = (float(p.box_length_cm), float(p.box_width_cm), float(p.box_height_cm))
                capacity = boxes_fit(dims, c["dims"])
            if not capacity and p.volume_m3:
                capacity = floor(c["volume"] * FALLBACK_FILL / float(p.volume_m3))
            if capacity:
                load[key] += boxes / capacity

    containers = {}
    if lines and volume_complete:
        for key, c in CONTAINERS.items():
            by_weight = float(weight) / c["payload"] if weight_complete else 0.0
            fill = max(load[key], by_weight)
            containers[key] = {
                "count": max(1, ceil(fill - 1e-9)),
                "fill_percent": round(fill * 100, 1),
                "limited_by": "weight" if by_weight > load[key] else "volume",
            }

    return {
        "lines": lines,
        "currency": country.currency.code if country else None,
        "has_prices": bool(country),
        "total_amount": total_amount if country else None,
        "total_boxes": total_boxes,
        "total_weight_kg": weight.quantize(Decimal("0.01")) if lines else None,
        "weight_complete": weight_complete,
        "total_volume_m3": volume.quantize(Decimal("0.001")) if lines else None,
        "volume_complete": volume_complete,
        "pallets": ceil(pallets - 1e-9) if lines and pallets_complete else None,
        "containers": containers,
    }


def to_json(result):
    """Decimal -> str/float для JSON-ответа калькулятора."""
    def conv(value):
        if isinstance(value, Decimal):
            return float(value)
        if isinstance(value, dict):
            return {k: conv(v) for k, v in value.items()}
        if isinstance(value, list):
            return [conv(v) for v in value]
        return value
    return conv(result)
