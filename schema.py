import json, re
from typing import Dict, Any

# ------------------------------------------------------------------ helpers
def validate_and_normalize_schema(data: Dict[str, Any]) -> Dict[str, Any]:
    """
    Maps common LLM field variations onto a fixed schema and cleans types.
    Extra keys are preserved verbatim.
    """
    EXPECTED = {
        "device": str, "product": str, "mask_type": str, "type": str,
        "features": list, "components": list, "add_ons": list, "accessories": list,
        "diagnosis": str, "SpO2": str, "usage": list, "mobility_status": str,
        "qualifier": str, "compliance_status": str, "ordering_provider": str,
    }

    MAP = {
        # Device
        "equipment": "device", "medical_device": "device", "device_type": "device",
        # Product
        "product_name": "product", "model": "product",
        # Components / accessories
        "supplies": "components", "parts": "components", "items": "components",
        "equipment_list": "components",
        # Diagnosis
        "condition": "diagnosis", "medical_condition": "diagnosis", "disorder": "diagnosis",
        # Provider
        "doctor": "ordering_provider", "physician": "ordering_provider", "provider": "ordering_provider",
        "prescribing_physician": "ordering_provider", "prescribing_doctor": "ordering_provider",
        # Compliance
        "compliance": "compliance_status", "patient_compliance": "compliance_status",
        "adherence": "compliance_status",
        # Usage
        "use_case": "usage", "application": "usage", "purpose": "usage",
        # Oxygen
        "oxygen_saturation": "SpO2", "spo2": "SpO2", "o2_sat": "SpO2",
        # Mobility
        "mobility": "mobility_status", "patient_mobility": "mobility_status",
        # Add-ons
        "addons": "add_ons", "add-ons": "add_ons", "additional_items": "add_ons", "extras": "add_ons",
        # Mask
        "mask": "mask_type", "interface": "mask_type", "mask_style": "mask_type",
        # Variant
        "device_variant": "type", "variant": "type", "style": "type",
    }

    # ---- ① map variations → canonical names (unless canonical already present)
    mapped: Dict[str, Any] = {}
    for k, v in data.items():
        k_std = MAP.get(k.lower(), k)
        if k_std not in data or k_std == k:   # avoid overwriting canonical present in payload
            mapped[k_std] = v
        else:
            mapped[k] = v                     # keep unusual key as-is

    # ---- ② type coerce / clean expected keys
    cleaned: Dict[str, Any] = {}
    for field, expected_type in EXPECTED.items():
        if field not in mapped:
            continue
        val = mapped[field]
        if expected_type is str:
            if isinstance(val, str) and val.strip():
                cleaned[field] = val.strip()
            elif val is not None:
                cleaned[field] = str(val).strip()
        else:  # list
            if isinstance(val, list):
                items = [str(x).strip() for x in val if str(x).strip()]
            elif isinstance(val, str) and val.strip():
                items = [val.strip()]
            else:
                items = []
            if items:
                cleaned[field] = items

    # ---- ③ copy any other keys untouched
    for k, v in mapped.items():
        if k not in cleaned:
            cleaned[k] = v
    return cleaned


def extract_structured_data(raw: str) -> Dict[str, Any]:
    """
    Pull the first JSON block out of the model response.
    If not decodable, return {'raw_response': ...}
    """
    try:
        m = re.search(r"\{.*\}", raw, re.DOTALL)
        if m:
            return validate_and_normalize_schema(json.loads(m.group()))
        return {"raw_response": raw}
    except json.JSONDecodeError:
        return {"raw_response": raw}
