
from typing import Dict, Callable, List, Optional, Tuple
import importlib

def load_registry() -> Dict[str, Callable]:
    GMPE = importlib.import_module("GMPE")
    if hasattr(GMPE, "GMPE_REGISTRY"):
        reg = getattr(GMPE, "GMPE_REGISTRY")
        if isinstance(reg, dict) and reg:
            return dict(reg)
    registry = {}
    for name in dir(GMPE):
        if name.startswith("gmpe_"):
            fn = getattr(GMPE, name)
            if callable(fn):
                registry[name[5:]] = fn
    if not registry:
        raise RuntimeError("No GMPE functions discovered in GMPE.py")
    return registry

_GMPE_REGISTRY = load_registry()
_ACTIVE: List[Tuple[str, Callable]] = list(_GMPE_REGISTRY.items())

def list_gmpes() -> List[str]:
    return list(_GMPE_REGISTRY.keys())

def set_gmpes(names: Optional[List[str]]):
    global _ACTIVE
    if names:
        _ACTIVE = [(n, _GMPE_REGISTRY[n]) for n in names if n in _GMPE_REGISTRY]
    else:
        _ACTIVE = list(_GMPE_REGISTRY.items())

def active_pairs() -> List[Tuple[str, Callable]]:
    return list(_ACTIVE)
