import numpy as np

def gmpe_HH_1992(Ms,Mw,Re,Rh,vs30,D):
    #震中距
    Rh=np.maximum(Rh, 1)  # 避免 R=0 的情况
    PGA_hr=-1.822+ 1.448*Ms -0.052*Ms**2 -2.018*np.log10(Rh+0.1818*np.exp(0.7072*Ms))
    PGA_ss=-1.164+ 1.203*Ms -0.044*Ms**2 -1.65*np.log10(Rh+0.1818*np.exp(0.7072*Ms))
    lgPGA=np.where(vs30<760,PGA_ss,PGA_hr)
    return 10**lgPGA/100

def gmpe_Si_1999(Ms,Mw,Re,Rh,vs30,D):
    #震源距
    Re=np.maximum(Re, 1)  # 避免 R=0 的情况
    C1,C2,C3,C4,C5 = 0.5,0.0043,0.0055,-0.003,0.61
    lgPGA=C1*Mw + C2*D-np.log10(Re+C3*(10**(0.5*Mw)))+C4*Re+C5
    return 10**lgPGA/100

def gmpe_GB_2015(Ms,Mw,Re,Rh,vs30,D):
    # 模型参数（按 Ms 分段）
    if Ms <= 6.5:
        C1, C2, C3, C4, C5 = 0.561, 0.746, -1.925, 0.956, 0.462
    else:
        C1, C2, C3, C4, C5 = 2.501, 0.448, -1.925, 0.956, 0.462
    # 原始 PGA（单位 cm/s²）
    Re = np.maximum(Re, 1.0)  # 避免 log(0)
    lgY = C1 + C2 * Ms + C3 * np.log10(Re + C4 * np.exp(C5 * Ms))
    pga_cm = 10 ** lgY
    # 场地分类索引（0=IV, ..., 4=I₀）
    site_edges = np.array([170, 260, 640, 1140, np.inf])
    site_indices = np.searchsorted(site_edges, vs30, side='right')
    # PGA 分级边界（单位 cm/s²）
    pga_bounds = np.array([0.05, 0.10, 0.15, 0.20, 0.30, 0.40]) * 980
    pga_indices = np.searchsorted(pga_bounds, pga_cm, side='right')
    pga_indices[pga_indices == len(pga_bounds)] = len(pga_bounds) - 1  # 映射超出到最后一列
    # 场地修正系数矩阵（行=场地类型，列=PGA 区间）
    correction_matrix = np.array([
        [1.25, 1.20, 1.10, 1.00, 0.95, 0.90],  # IV = 0
        [1.30, 1.25, 1.15, 1.00, 1.00, 1.00],  # III = 1
        [1.00, 1.00, 1.00, 1.00, 1.00, 1.00],  # II  = 2
        [0.80, 0.82, 0.83, 0.85, 0.95, 1.00],  # I₁  = 3
        [0.72, 0.74, 0.75, 0.76, 0.85, 0.90],  # I₀  = 4
    ])
    # 获取修正因子
    factors = correction_matrix[site_indices, pga_indices]
    # 应用修正
    corrected_pga = pga_cm * factors
    return corrected_pga/100


def gmpe_Zhou_2019(Ms,Mw,Re,Rh,vs30,D):
    #震中距
    Re=np.maximum(Re, 1)  # 避免 R=0 的情况
    C1, C2, C3, C4, C5, C6 = -1.26102,1.2030,-0.044,-1.65,0.1818,0.7072
    C7,C8=-9.82429e-6,0.0050472
    lgPGA = C1+C2*Mw+C3*Mw**2+C4*np.log10(Re+C5*np.exp(C6*Mw))+C7*Re**2+C8*Re
    #C7*np.log(R)**2+C8*np.log(R)
    return 10**lgPGA/100

def gmpe_Wang_2023(Ms,Mw,Re,Rh,vs30,D):
    #震源距
    Rh=np.maximum(Rh, 1)  # 避免 R=0 的情况
    Vs30_safe = np.nan_to_num(vs30, nan=180) 
    C1, C2, C3, C4, C5, C6 = 8.8987, -0.8896, -0.2112, -3.0899, 0.2673, 10.3706
    C7, C8, C9, C10 = -0.568, -0.172, -0.0067, 0.1
    ln_PGAr = (C1+ C2*Mw + C3*(8.5-Mw)**2+
               (C4+C5*Mw)*np.log(np.sqrt(Rh**2+C6**2)))
    PGAr = np.exp(ln_PGAr)
    lnY =ln_PGAr+ C7 * np.log(Vs30_safe/760)+ C8*np.exp(C9*(Vs30_safe-360.0))*np.log((PGAr+C10)/C10)
    result = np.exp(lnY) * 980
    return result/100







# === GMPE_REGISTRY (auto; define AFTER gmpe_* functions) ===
GMPE_REGISTRY = {}
for _name in ("HH1992", "Si1999", "GB2015", "Zhou_2019", "Wang_2023"):
    _fn = globals().get(f"gmpe_{_name}")
    if callable(_fn):
        GMPE_REGISTRY[_name] = _fn
for _k, _v in list(globals().items()):
    if _k.startswith("gmpe_") and callable(_v):
        _friendly = _k[5:]
        GMPE_REGISTRY.setdefault(_friendly, _v)
if not GMPE_REGISTRY:
    raise RuntimeError("GMPE_REGISTRY is empty. Ensure gmpe_* functions are defined above.")
