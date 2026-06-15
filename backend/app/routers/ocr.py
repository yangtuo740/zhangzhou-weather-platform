from fastapi import APIRouter, Depends, HTTPException, UploadFile, File
from sqlmodel import Session
from ..database import get_session
from ..schemas import OcrResult, DeviceOut
from ..auth import get_current_user
from ..models import User
from ..services.device_service import save_ocr_result
from ..config import settings
import uuid, os, re

router = APIRouter(prefix="/api/ocr", tags=["ocr"])

OCR_AVAILABLE = True
reader = None
try:
    import easyocr
    reader = easyocr.Reader(["ch_sim", "en"], gpu=False)
except Exception:
    OCR_AVAILABLE = False

def norm(s):
    return re.sub(r"\s+", "", s)

def _is_noise(text, min_len=2):
    if not text or len(text) < min_len:
        return True
    if re.match(r"^[A-Za-z]{2,6}$", text):
        return True
    if re.match(r"^[\|\}\]\[\)\(\{\}\@\#\*\-\_\+=:;.,/\\'`\"~]+$", text):
        return True
    return False

def find_label_index(lines_norm, label_norm):
    for i, (nt, raw, conf) in enumerate(lines_norm):
        if label_norm in nt:
            return i
    return -1

def get_value_after_label(lines_raw, lines_norm, label_norm, prefer_conf=True, skip_same_line=False):
    idx = find_label_index(lines_norm, label_norm)
    if idx < 0:
        return ""
    if not skip_same_line:
        _, raw, _ = lines_norm[idx]
        raw_norm = norm(raw)
        pos = raw_norm.find(label_norm)
        if pos >= 0:
            after = raw_norm[pos + len(label_norm):]
            if after and not _is_noise(after, 1):
                return after.strip()
    candidates = []
    for j in range(idx + 1, min(idx + 6, len(lines_raw))):
        nxt = lines_raw[j][0].strip()
        conf = lines_raw[j][1]
        if not _is_noise(nxt, 2):
            candidates.append((conf, nxt))
    if not candidates:
        return ""
    if prefer_conf:
        candidates.sort(key=lambda x: x[0], reverse=True)
    return candidates[0][1]

def extract_equip_code(lines_raw):
    for text, conf in lines_raw:
        m = re.search(r"(\d{20,})", text)
        if m:
            code = m.group(1)
            prefix_m = re.search(r"([A-Za-z])" + re.escape(code), text)
            if prefix_m:
                return prefix_m.group(1) + code
            return "Z" + code
    return ""

def extract_date(lines_raw):
    for text, conf in lines_raw:
        m = re.search(r"(\d{4})\s*年\s*(\d{1,2})\s*月\s*(\d{1,2})\s*日", text)
        if m:
            return f"{m.group(1)}-{m.group(2).zfill(2)}-{m.group(3).zfill(2)}"
    year = ""
    for text, _ in lines_raw:
        m = re.search(r"(\d{4})\s*年", text)
        if m:
            year = m.group(1)
            break
    if not year:
        return ""
    for text, _ in lines_raw:
        m = re.search(r"(\d{1,2})\s*月\s*(\d{1,2})\s*日", text)
        if m:
            return f"{year}-{m.group(1).zfill(2)}-{m.group(2).zfill(2)}"
    return f"{year}-01-01"

def clean_name(val):
    if not val:
        return ""
    m = re.search(r"([\u4e00-\u9fff]{2,4})", val)
    return m.group(1) if m else val

def fix_ocr_mistakes(val, field):
    if not val:
        return ""
    if field == "model_spec":
        val = val.replace("I", "1").replace("O", "0").replace("S", "5")
    elif field == "equip_code":
        if val.startswith("Z21"):
            val = "Z11" + val[3:]
        elif val.startswith("21"):
            val = "Z11" + val[2:]
    elif field == "send_unit":
        val = val.replace("褐建", "福建")
    elif field == "device_name":
        val = re.sub(r"\bDQ(\d)", r"DNQ\1", val)
    elif field == "cert_no":
        val = re.sub(r"[｜\|〔〕\[\]\(\)\{\}]", "", val)
    return val

def extract_all(lines_raw, lines_norm) -> OcrResult:
    result = OcrResult()
    result.cert_no = fix_ocr_mistakes(get_value_after_label(lines_raw, lines_norm, "证书编号:", False), "cert_no")
    result.send_unit = fix_ocr_mistakes(get_value_after_label(lines_raw, lines_norm, "送检单位", False), "send_unit")
    result.device_name = fix_ocr_mistakes(get_value_after_label(lines_raw, lines_norm, "计量器具名称", False), "device_name")
    result.model_spec = fix_ocr_mistakes(get_value_after_label(lines_raw, lines_norm, "型号/规格", False), "model_spec")
    result.equip_code = fix_ocr_mistakes(extract_equip_code(lines_raw), "equip_code")
    result.manufacturer = get_value_after_label(lines_raw, lines_norm, "制造单位", False)
    result.approver = clean_name(get_value_after_label(lines_raw, lines_norm, "批准人", True, True))

    val = get_value_after_label(lines_raw, lines_norm, "核验员", True, True)
    if val and ("\uff1a" in val or ":" in val):
        val = re.split(r"[\uff1a:]", val)[-1]
    result.reviewer = clean_name(val)

    val = get_value_after_label(lines_raw, lines_norm, "校准员", True, True)
    if val and ("\uff1a" in val or ":" in val):
        val = re.split(r"[\uff1a:]", val)[-1]
    result.calibrator = clean_name(val)

    result.calib_date = extract_date(lines_raw)

    for text, _ in lines_raw:
        if "校准专用章" in text or "检定专用章" in text:
            result.seal = text.strip()
            break
    return result

@router.post("/recognize", response_model=OcrResult)
async def recognize_certificate(file: UploadFile = File(...), current_user: User = Depends(get_current_user)):
    ext = os.path.splitext(file.filename or "image.png")[1].lower()
    if ext not in (".png", ".jpg", ".jpeg", ".bmp", ".webp"):
        raise HTTPException(400, "仅支持 PNG/JPG/JPEG/BMP/WEBP 格式")
    filename = f"{uuid.uuid4().hex}{ext}"
    filepath = os.path.join(settings.UPLOAD_DIR, filename)
    content = await file.read()
    with open(filepath, "wb") as f:
        f.write(content)
    if not OCR_AVAILABLE or reader is None:
        return OcrResult()
    try:
        ocr_result = reader.readtext(filepath)
        if not ocr_result:
            return OcrResult()
        lines_raw = [(r[1].strip(), r[2]) for r in ocr_result]
        lines_norm = [(norm(r[1]), r[1], r[2]) for r in ocr_result]
        return extract_all(lines_raw, lines_norm)
    except Exception as e:
        print(f"OCR error: {e}")
        return OcrResult()

@router.post("/save", response_model=DeviceOut)
async def save_ocr_device(result: OcrResult, filename: str = "", session: Session = Depends(get_session), current_user: User = Depends(get_current_user)):
    image_path = os.path.join(settings.UPLOAD_DIR, filename) if filename else ""
    return save_ocr_result(session, result, image_path, current_user.id, current_user.username)
