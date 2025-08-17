#!/usr/bin/env python3

def _parse_version(version_str: str):
    try:
        vs = version_str.lstrip("v")
        parts = [int(p) for p in vs.split(".") if p.isdigit() or p.isnumeric()]
        # Normalize to 3 parts
        while len(parts) < 3:
            parts.append(0)
        return tuple(parts[:3])
    except Exception:
        return (0, 0, 0)

# Test des versions
current = "1.0.40"
latest = "2.0.0"

current_parsed = _parse_version(current)
latest_parsed = _parse_version(latest)

print(f"Current version: {current} -> {current_parsed}")
print(f"Latest version: {latest} -> {latest_parsed}")
print(f"Latest > Current: {latest_parsed > current_parsed}")
print(f"Latest <= Current: {latest_parsed <= current_parsed}")

# Test avec v prefix
current_v = "v1.0.40"
latest_v = "v2.0.0"

current_v_parsed = _parse_version(current_v)
latest_v_parsed = _parse_version(latest_v)

print(f"\nWith v prefix:")
print(f"Current version: {current_v} -> {current_v_parsed}")
print(f"Latest version: {latest_v} -> {latest_v_parsed}")
print(f"Latest > Current: {latest_v_parsed > current_v_parsed}")
