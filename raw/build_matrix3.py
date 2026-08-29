import json, re, statistics

CFGS = [("m6_16","16GB"),("m6_24","24GB"),("m6_32","32GB"),
        ("m5pro_24","24GB"),("m5pro_48","48GB"),("m5pro_64","64GB"),
        ("m5max36","36GB"),("m5max48","48GB"),("m5max64","64GB"),("m5max128","128GB"),
        ("m5ultra96","96GB"),("m5ultra256","256GB"),("m5ultra512","512GB")]

# bandwidth ratio per config: derived from prior scaled_full.json (scaled/raw), 256GB/s detector
old = json.load(open("/tmp/opencode/scaled_full.json"))
RATIOS = {}
for cfg,_ in CFGS:
    rs = [v["scaled_tps"]/v["raw_tps"] for v in old[cfg].values() if v["raw_tps"]]
    RATIOS[cfg] = round(statistics.median(rs), 3)
print("ratios:", RATIOS)

DETECTOR_BW = 256.0
EFF = 0.55          # llmfit's own roofline efficiency constant
SLACK = 1.15        # allow formula slack above the theoretical ceiling

FAM = [
 ("frontier","Kimi K3 2.8T","CN", r'kimi-k3', r'dspark|dflash|eagle|draft|pruned|0\.40b|abliterated|uncensored|derisked|k2\.|distill', ["moonshotai/","unsloth/","mlx-community/","lmstudio-community/"]),
 ("frontier","Qwen3.8-Max 2.4T","CN", r'qwen3\.8-2\.4', r'dspark|pruned|distill', ["qwen/","amd/","mlx-community/"]),
 ("frontier","DeepSeek V4-Pro 1.6T","CN", r'deepseek-v4-pro', r'qwen3\.5|distill|spark', ["deepseek-ai/","unsloth/","mlx-community/","intel/","nvidia/","redhatai/"]),
 ("frontier","LongCat 2.0 1.6T","CN", r'longcat-2\.0', r'uncensored|heretic', ["meituan-longcat/","mlx-community/","intel/"]),
 ("frontier","Ling 2.6 1T","CN", r'ling-2\.6-1t', r'-base', ["inclusionai/","mlx-community/"]),
 ("frontier","GLM-5.2 743B","CN", r'glm-5\.2', r'dspark|speculator|sparkulator|vision|distill|dflash', ["zai-org/","unsloth/","mlx-community/","redhatai/"]),
 ("frontier","Nemotron 3 Ultra 550B","US", r'nemotron-3-ultra', r'abliterated|uncensored|reap', ["nvidia/","redhatai/","unsloth/","mlx-community/"]),
 ("mid","Llama 4 Maverick 400B","US", r'llama-4-maverick', r'', ["meta-llama/","redhatai/"]),
 ("mid","Qwen3.5 397B-A17B","CN", r'qwen3\.5-397b', r'', ["qwen/","amd/","mlx-community/","unsloth/"]),
 ("mid","DeepSeek V4-Flash 284B","CN", r'deepseek-v4-flash', r'qwen3\.5|distill|dspark', ["deepseek-ai/","unsloth/","mlx-community/","crusoeai/","amd/","redhatai/"]),
 ("mid","MiniMax M3 427B","CN", r'minimax-m3', r'eagle|dspark', ["minimaxai/","nvidia/","mlx-community/","cyankiwi/"]),
 ("mid","Kimi K2.6 1.1T","CN", r'kimi-k2\.6', r'dflash|dspark|eagle|distill|qwopus|healed', ["moonshotai/","unsloth/","mlx-community/","lmstudio-community/","nvidia/","novita/","z-lab/"]),
 ("mid","Nemotron 3 Super 120B","US", r'nemotron-3-super', r'reap|math|abliterated|uncensored', ["nvidia/","cyankiwi/","mlx-community/","unsloth/"]),
 ("mid","gpt-oss-120b 117B","US", r'gpt-oss-120b', r'vision|eagle', ["openai/","unsloth/","mlx-community/","lmstudio-community/","nvidia/","redhatai/"]),
 ("mid","Llama 4 Scout 109B","US", r'llama-4-scout', r'abliterated', ["meta-llama/","redhatai/"]),
 ("small","Gemma 4 31B","US", r'gemma-4-31b', r'heretic|abliterated|uncensored|deckard|opus|scotoma|novelist|eclipse|roleplay', ["google/","unsloth/","mlx-community/","lmstudio-community/","redhatai/","quanttrio/","cyankiwi/"]),
 ("small","Gemma 4 26B-A4B","US", r'gemma-4-26b-a4b', r'heretic|abliterated|uncensored|sompoa|pawarshardul', ["google/","nvidia/","unsloth/","mlx-community/","lmstudio-community/","redhatai/"]),
 ("small","Qwen3.8 27B","CN", r'qwen3\.8-27b', r'heretic|abliterated|distill|jang|crack|minitron|fable', ["qwen/","unsloth/","mlx-community/","lmstudio-community/","amd/","ulkaa/"]),
 ("small","ERNIE 4.5 21B-A3B","CN", r'ernie-4\.5-21b', r'', ["baidu/","lmstudio-community/","cyankiwi/","mlx-community/"]),
 ("small","Granite 4.1 30B","US", r'granite-4\.1-30b', r'', ["ibm-granite/","mlx-community/","nightmedia/"]),
 ("small","Nemotron 3 Nano 30B","US", r'nemotron-3-nano-30b', r'omni|-base', ["nvidia/","unsloth/","mlx-community/","lmstudio-community/"]),
 ("small","Ministral 3 14B","EU", r'ministral-3-14b', r'', ["mistralai/","ccharnkij/","automatosx/"]),
 ("small","Gemma 4 12B","US", r'gemma-4-12b', r'heretic|abliterated|esper|guardpoint|mlponly', ["google/","unsloth/","mlx-community/","lmstudio-community/","mattbucci/"]),
 ("small","gpt-oss-20b 21B","US", r'gpt-oss-20b', r'vision|internvl|codegpt|heretic', ["openai/","unsloth/","mlx-community/","lmstudio-community/","nvidia/","onnx-community/"]),
]

MIN_GB = {
 "Kimi K3 2.8T": 600, "Qwen3.8-Max 2.4T": 550, "DeepSeek V4-Pro 1.6T": 350,
 "LongCat 2.0 1.6T": 350, "Ling 2.6 1T": 220, "GLM-5.2 743B": 160,
 "Nemotron 3 Ultra 550B": 120, "Llama 4 Maverick 400B": 90, "Qwen3.5 397B-A17B": 90,
 "MiniMax M3 427B": 95, "Kimi K2.6 1.1T": 250, "Nemotron 3 Super 120B": 28,
 "gpt-oss-120b 117B": 28, "Llama 4 Scout 109B": 25, "DeepSeek V4-Flash 284B": 65,
 "Gemma 4 31B": 9, "Gemma 4 26B-A4B": 7, "Qwen3.8 27B": 7.5, "ERNIE 4.5 21B-A3B": 5.5,
 "Granite 4.1 30B": 8, "Nemotron 3 Nano 30B": 8, "Ministral 3 14B": 4,
 "Gemma 4 12B": 3.5, "gpt-oss-20b 21B": 5.5,
}

JUNK = re.compile(r'slice|reap|prune|pct$|-\d+pct|fragm|draft|-\d+b$')

def sane(m):
    """Arithmetic gate on llmfit's own output: a Perfect/Good verdict on a machine whose
    available memory is smaller than the entry's own memory requirement is corrupt."""
    mem = m.get("memory_required_gb") or 0
    avail = m.get("memory_available_gb") or 0
    fit = m.get("fit_level")
    if fit in ("Perfect", "Good") and avail and mem > avail * 0.98:
        return False, f"fit-mem mismatch ({mem:.1f}GB > {avail:.1f}GB)"
    if JUNK.search(m["name"].lower()):
        return False, "junk pattern"
    return True, ""

def candidates(models, inc, exc, min_gb):
    c = [m for m in models if re.search(inc, m["name"].lower()) and not (exc and re.search(exc, m["name"].lower()))]
    c = [m for m in c if (m["memory_required_gb"] or 0) >= min_gb]
    return [m for m in c if sane(m)[0]]

def choose_canonical(by_cfg, prefs):
    """One variant per family, chosen on the tightest config where a rank-0 (Perfect/Good)
    candidate survives the gates. Preferred publishers first, then score; tiebreak on
    smaller memory. Falls back to largest-config Marginal."""
    rank = {"Perfect": 0, "Good": 0, "Marginal": 1, "Too Tight": 2}
    def best(pool):
        if not pool:
            return None
        def key(m):
            is_pref = 0 if any(m["name"].lower().startswith(p) for p in prefs) else 1
            return (is_pref, rank.get(m["fit_level"], 9), -m["score"], m["memory_required_gb"] or 0)
        return min(pool, key=key)
    # smallest config first: a trusted publisher's Marginal beats an unknown repo's
    # "Perfect" (community quant perf metadata is unreliable), hence the (pref, rank) key
    for cfg, _ in CFGS:
        got = best([m for m in by_cfg.get(cfg, []) if rank.get(m["fit_level"], 9) <= 1])
        if got and rank.get(got["fit_level"], 9) <= 1:
            return got, cfg
    for cfg, _ in reversed(CFGS):
        got = best(by_cfg.get(cfg, []))
        if got:
            return got, cfg
    return None, None

RAM = {cfg: float(lbl.replace("GB","")) for cfg, lbl in CFGS}

BW_CFG = {"m6_16": 153, "m6_24": 170, "m6_32": 170,
          "m5pro_24": 307, "m5pro_48": 307, "m5pro_64": 307,
          "m5max36": 460, "m5max48": 614, "m5max64": 614, "m5max128": 614,
          "m5ultra96": 1200, "m5ultra256": 1200, "m5ultra512": 1200}

# active (per-token) parameter counts in billions, from published model cards
ACTIVE_B = {
 "Kimi K3 2.8T": 50, "Qwen3.8-Max 2.4T": 95, "DeepSeek V4-Pro 1.6T": 49,
 "LongCat 2.0 1.6T": 48, "GLM-5.2 743B": 40, "Nemotron 3 Ultra 550B": 55,
 "Llama 4 Maverick 400B": 17, "Qwen3.5 397B-A17B": 17, "DeepSeek V4-Flash 284B": 13,
 "MiniMax M3 427B": 10, "Kimi K2.6 1.1T": 32, "Nemotron 3 Super 120B": 12,
 "gpt-oss-120b 117B": 5.1, "Llama 4 Scout 109B": 17,
 "Gemma 4 26B-A4B": 4, "ERNIE 4.5 21B-A3B": 3, "Nemotron 3 Nano 30B": 3.2,
}

def fit_by_memory(mem, avail):
    """Fit from the variant's measured footprint vs this machine's usable memory.
    Thresholds declared in the post: headroom is what separates Perfect from Good."""
    if mem <= 0.60 * avail: return "Perfect"
    if mem <= 0.85 * avail: return "Good"
    if mem <= 0.98 * avail: return "Marginal"
    return "Too Tight"

out = {}
audit = {}
for grp, disp, region, inc, exc, prefs in FAM:
    by_cfg = {}
    for cfg, _ in CFGS:
        models = json.load(open(f"/tmp/opencode/{cfg}.json"))["models"]
        by_cfg[cfg] = candidates(models, inc, exc, MIN_GB[disp])
    canon, canon_cfg = choose_canonical(by_cfg, prefs)
    if canon is None:
        for cfg, _ in CFGS:
            out.setdefault(cfg, {})[disp] = {"fit":"Missing","raw_tps":0,"scaled_tps":0,"mem":0,"variant":None,"quant":None}
        audit[disp] = {"canonical": None, "chosen_on": None}
        continue
    mem = canon["memory_required_gb"]
    avail_home = RAM[canon_cfg]  # usable memory = config RAM; entry field can be corrupt
    raw_home = canon["estimated_tps"] or 0
    # MoE decode roofline: only active experts are read per token. llmfit 1.1.12 roofs
    # MoE on total bytes (issue #474, fixed by PR #475 upstream), underestimating 6-12x.
    # Corrected: naive bytes/token = active_params x (footprint/total), efficiency 0.25
    # calibrated against measured gpt-oss-120b (95 pred vs 88 measured, M5 Max 614GB/s)
    # and DeepSeek V4-Flash (40 pred vs 34 measured, MLX, M5 Max 128GB).
    active_b = ACTIVE_B.get(disp)
    is_moe_row = disp in ACTIVE_B
    for cfg, _ in CFGS:
        avail = RAM[cfg]
        if is_moe_row and active_b and mem and canon["params_b"]:
            gb_per_tok = active_b * (mem / canon["params_b"])
            tps = BW_CFG[cfg] * 0.25 / gb_per_tok
        else:
            tps = raw_home * RATIOS[cfg]
        fam_disp = {
            "fit": fit_by_memory(mem, avail),
            "raw_tps": round(tps, 2),
            "scaled_tps": round(tps, 2),
            "mem": mem, "variant": canon["name"], "quant": canon["best_quant"],
            "chosen_on": canon_cfg, "tps_method": "moe-active" if is_moe_row else "llmfit-scaled",
        }
        out.setdefault(cfg, {})[disp] = fam_disp
    audit[disp] = {"canonical": canon["name"], "chosen_on": canon_cfg, "mem": mem}

json.dump(out, open("/tmp/opencode/final_matrix3.json","w"), indent=1)

print("\ncanonical picks:")
for disp, a in audit.items():
    print(f"  {disp:26} {a['chosen_on'] or '-':10} {a['canonical'] or '-'}")
print("\nfit matrix (fit | scaled tps):")
for grp, disp, region, *_ in FAM:
    row = " ".join(f"{out[cfg][disp]['fit'][:4]:>4}/{out[cfg][disp]['scaled_tps'] or 0:>6.1f}" for cfg,_ in CFGS)
    print(f"{grp:8} {disp:24} {row}")
missing = [(cfg,d) for cfg,_ in CFGS for d in out[cfg] if out[cfg][d]["fit"]=="Missing"]
print("MISSING:", missing)
