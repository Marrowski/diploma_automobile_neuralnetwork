from typing import List, Dict, Tuple, Any
import re
import cv2
import numpy as np
from ultralytics import YOLO
import easyocr
import pathlib

_CURRENT_FILE_DIR = pathlib.Path(__file__).parent.resolve()
_MODEL_PATH = _CURRENT_FILE_DIR / "license_plate_detector.pt"

try:
    if not _MODEL_PATH.exists():
        raise FileNotFoundError(f"Модель не знайдено: {_MODEL_PATH}")
    _LPD_MODEL = YOLO(_MODEL_PATH)
except Exception as e:
    _LPD_MODEL = None
    raise e

_OCR = easyocr.Reader(['en'], gpu=False)
_PLATE_CLASS_ID = {0}
UA_LETTERS = set("ABCEHIKMOPTXY")

_NON_UA_TO_UA = {
    'D': 'O', 'F': 'E', 'G': 'C', 'J': 'I', 'L': 'I',
    'N': 'H', 'Q': 'O', 'R': 'P', 'U': 'H', 'V': 'B',
    'W': 'M', 'Z': 'X',
}

_TO_LETTER = {
    '0': 'O', '1': 'I', '8': 'B', '5': 'S',
    **_NON_UA_TO_UA,
}

_TO_DIGIT = {
    'O': '0', 'I': '1', 'B': '8', 'S': '5',
    'G': '4', 'D': '0', 'Z': '2', 'T': '7', 'A': '4',
}


def _try_fix_to_ua(text: str) -> str:
    return "".join(_NON_UA_TO_UA.get(c, c) for c in text)


def _force_fit_ua(text: str) -> str:
    if not text:
        return ""

    def fix(s, letter_idx, digit_idx):
        chars = list(s)
        for i in letter_idx:
            c = chars[i]
            if c not in UA_LETTERS:
                chars[i] = _TO_LETTER.get(c, c)
        for i in digit_idx:
            c = chars[i]
            if not c.isdigit():
                chars[i] = _TO_DIGIT.get(c, c)
        result = "".join(chars)
        return result if is_ukrainian_plate(result) else ""

    if len(text) == 8:
        return fix(text, [0, 1, 6, 7], [2, 3, 4, 5])
    if len(text) == 6:
        return fix(text, [4, 5], [0, 1, 2, 3])
    if len(text) == 7:
        return fix(text, [0, 1], [2, 3, 4, 5, 6])
    return ""


def _fix_ocr_confusion(s: str) -> str:
    if not s or len(s) < 6:
        return s

    DIGIT_TO_LETTER = {"0": "O", "1": "I", "8": "B", "5": "S"}
    LETTER_TO_DIGIT = {"O": "0", "I": "1", "B": "8", "S": "5"}

    def fix_positions(s, letter_pos, digit_pos):
        fixed = list(s)
        for i in letter_pos:
            if fixed[i] in DIGIT_TO_LETTER:
                fixed[i] = DIGIT_TO_LETTER[fixed[i]]
        for i in digit_pos:
            if fixed[i] in LETTER_TO_DIGIT:
                fixed[i] = LETTER_TO_DIGIT[fixed[i]]
        return "".join(fixed)

    if len(s) == 8:
        candidate = fix_positions(s, [0, 1, 6, 7], [2, 3, 4, 5])
        if (candidate[0] in UA_LETTERS and candidate[1] in UA_LETTERS
                and candidate[2:6].isdigit()
                and candidate[6] in UA_LETTERS and candidate[7] in UA_LETTERS):
            return candidate

    if len(s) == 6:
        candidate = fix_positions(s, [4, 5], [0, 1, 2, 3])
        if candidate[:4].isdigit() and all(c in UA_LETTERS for c in candidate[4:]):
            return candidate

    if len(s) == 7:
        candidate = fix_positions(s, [0, 1], [2, 3, 4, 5, 6])
        if all(c in UA_LETTERS for c in candidate[:2]) and candidate[2:].isdigit():
            return candidate

    return s


def _normalize_text(s: str) -> str:
    if not s:
        return ""
    s = s.upper()
    s = re.sub(r"[\s\-\._:,\(\)\[\]{}|/\\'\"]", "", s)
    cyrillic_to_latin = {
        "А": "A", "В": "B", "С": "C", "Е": "E", "Н": "H", "І": "I", "К": "K",
        "М": "M", "О": "O", "Р": "P", "Т": "T", "Х": "X",
    }
    s = "".join(cyrillic_to_latin.get(ch, ch) for ch in s)
    s = re.sub(r"[^A-Z0-9]", "", s)
    s = _fix_ocr_confusion(s)
    return s


def is_ukrainian_plate(text: str) -> bool:
    if not text:
        return False
    t = _normalize_text(text)
    ua = "ABCEHIKMOPTXY"
    patterns = [
        re.compile(rf"^[{ua}]{{2}}\d{{4}}[{ua}]{{2}}$"),
        re.compile(rf"^\d{{4}}[{ua}]{{2}}$"),
        re.compile(rf"^[{ua}]{{2}}\d{{5}}$"),
    ]
    return any(p.match(t) for p in patterns)


def _clip_box(x1, y1, x2, y2, W, H):
    x1 = max(0, int(x1))
    y1 = max(0, int(y1))
    x2 = min(W - 1, int(x2))
    y2 = min(H - 1, int(y2))
    if x2 <= x1 or y2 <= y1:
        return None
    return x1, y1, x2, y2


def _score_plate_candidate(text: str) -> float:
    if not text:
        return 0.0
    t = _normalize_text(text)
    if len(t) < 4 or len(t) > 9:
        return 0.0
    alnum_mix = bool(re.search(r"[A-Z]", t)) and bool(re.search(r"\d", t))
    mix_bonus = 0.5 if alnum_mix else 0.0
    len_score = 1.0 - (abs(len(t) - 8) / 8.0)
    return max(0.0, (len_score + mix_bonus) / 2.0)


def _extract_best_text(ocr_results: list) -> str:
    ocr_results = sorted(ocr_results, key=lambda r: r[0][0][0])

    all_texts = []
    for (_, txt, score) in ocr_results:
        if not txt or score < 0.1:
            continue
        t_clean = re.sub(r"[\s\-]", "", txt).upper()
        if t_clean in {"UA", "AU"}:
            continue
        all_texts.append((txt, score))

    if not all_texts:
        return ""

    combined = " ".join(t for t, s in all_texts)
    normalized = _normalize_text(combined)

    if is_ukrainian_plate(normalized):
        return normalized

    fixed = _try_fix_to_ua(normalized)
    if is_ukrainian_plate(fixed):
        return fixed

    force = _force_fit_ua(normalized)
    if force:
        return force

    best_txt, best_score = "", -1.0
    for txt, score in all_texts:
        t_norm = _normalize_text(txt)
        if not t_norm:
            continue
        cand_score = _score_plate_candidate(t_norm) + score
        if is_ukrainian_plate(t_norm):
            cand_score += 2.0
        elif is_ukrainian_plate(_try_fix_to_ua(t_norm)):
            cand_score += 1.5
        elif _force_fit_ua(t_norm):
            cand_score += 1.0
        if cand_score > best_score:
            best_score = cand_score
            best_txt = t_norm

    if best_txt:
        force_best = _force_fit_ua(best_txt)
        if force_best:
            return force_best
        return best_txt

    return normalized


def _plate_text_score(txt: str) -> float:
    if not txt:
        return -1.0
    score = _score_plate_candidate(txt)
    if is_ukrainian_plate(txt):
        score += 3.0
    return score


def _ocr_best_text_from_region(region_bgr: np.ndarray) -> str:
    h, w = region_bgr.shape[:2]
    if w < 250 or h < 60:
        scale = max(250 / max(w, 1), 60 / max(h, 1), 2.0)
        region_bgr = cv2.resize(region_bgr, None, fx=scale, fy=scale,
                                interpolation=cv2.INTER_CUBIC)

    gray = cv2.cvtColor(region_bgr, cv2.COLOR_BGR2GRAY)
    clahe = cv2.createCLAHE(clipLimit=3.0, tileGridSize=(8, 8)).apply(gray)
    _, otsu = cv2.threshold(gray, 0, 255, cv2.THRESH_BINARY + cv2.THRESH_OTSU)
    _, otsu_inv = cv2.threshold(gray, 0, 255, cv2.THRESH_BINARY_INV + cv2.THRESH_OTSU)

    variants = [
        region_bgr,
        cv2.cvtColor(gray, cv2.COLOR_GRAY2BGR),
        cv2.cvtColor(clahe, cv2.COLOR_GRAY2BGR),
        cv2.cvtColor(otsu, cv2.COLOR_GRAY2BGR),
        cv2.cvtColor(otsu_inv, cv2.COLOR_GRAY2BGR),
    ]

    best_txt, best_score = "", -1.0

    for variant in variants:
        try:
            results = _OCR.readtext(variant)
        except Exception:
            continue

        txt = _extract_best_text(results)
        if not txt:
            continue

        score = _plate_text_score(txt)
        if score > best_score:
            best_score = score
            best_txt = txt

        if is_ukrainian_plate(best_txt):
            break

    if best_txt and len(best_txt) < 4:
        return ""
    return best_txt


def _find_plate_regions(img: np.ndarray, conf=0.15) -> List[Tuple[int, int, int, int]]:
    if _LPD_MODEL is None:
        print("DEBUG: LPD_MODEL is None")
        return []
    H, W = img.shape[:2]
    out = []
    results = _LPD_MODEL.predict(img, conf=conf, verbose=False)
    for r in results:
        if r.boxes is not None:
            scores = r.boxes.conf.cpu().numpy()
            print(f"DEBUG: Found {len(scores)} objects")
            print(f"DEBUG: Confidence scores: {scores}")
        else:
            print("DEBUG: No boxes detected at all")

        if r.boxes is None:
            continue
        cls = r.boxes.cls.cpu().numpy().astype(int)
        xyxy = r.boxes.xyxy.cpu().numpy()
        for c, (x1, y1, x2, y2) in zip(cls, xyxy):
            if c in _PLATE_CLASS_ID:
                clipped = _clip_box(x1, y1, x2, y2, W, H)
                if clipped:
                    out.append(clipped)
    return out


def anpr_infer(image_bgr: np.ndarray) -> Dict:
    if _LPD_MODEL is None:
        return {"error": "LPD model not loaded."}

    H, W = image_bgr.shape[:2]
    plate_boxes = _find_plate_regions(image_bgr, conf=0.5)

    results = {"plates": [], "accepted": False}

    if not plate_boxes:
        return results

    for (x1, y1, x2, y2) in plate_boxes:
        pad_x = max(15, int((x2 - x1) * 0.1))
        pad_y = max(15, int((y2 - y1) * 0.15))
        crop = image_bgr[max(0,y1-pad_y):min(H,y2+pad_y), max(0,x1-pad_x):min(W,x2+pad_x)]

        if crop.size == 0:
            continue

        txt = _ocr_best_text_from_region(crop)
        if not txt:
            continue

        is_ua = is_ukrainian_plate(txt)
        results["plates"].append({
            "text": txt,
            "is_ua": is_ua,
            "bbox": [int(x1), int(y1), int(x2), int(y2)]
        })
        if is_ua:
            results["accepted"] = True

    return results


def anpr_infer_image_path(path: str) -> Dict:
    img = cv2.imread(path)
    if img is None:
        return {"error": f"Cannot read image: {path}"}
    return anpr_infer(img)


def anpr_infer_video_path(path: str, every_n_frames: int = 5, max_frames: int = 300) -> Dict:
    cap = cv2.VideoCapture(path)
    if not cap.isOpened():
        return {"error": f"Cannot open video: {path}"}
    plates = []
    accepted = False
    i = 0
    unique_plates = set()
    while True:
        ret, frame = cap.read()
        if not ret or i >= max_frames:
            break
        if i % every_n_frames == 0:
            res = anpr_infer(frame)
            if res.get("accepted", False):
                accepted = True
            for p in res.get("plates", []):
                if p["text"] not in unique_plates:
                    plates.append(p)
                    unique_plates.add(p["text"])
        i += 1
    cap.release()
    return {"plates": plates, "accepted": accepted}
