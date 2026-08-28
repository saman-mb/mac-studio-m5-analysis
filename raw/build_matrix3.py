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

# (group, display, region, include_re, exclude_re, preferred repo prefixes)
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

# plausibility floor on memory_required_gb (GB): ~2-bit floor of true params.
# DB has corrupt entries (mis-parsed community/MLX repos claiming e.g. 117B = 1.2GB).
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

def pick(models, inc, exc, prefs, min_gb):
    cands = [m for m in models if re.search(inc, m["name"].lower()) and not (exc and re.search(exc, m["name"].lower()))]
    cands = [m for m in cands if (m["memory_required_gb"] or 0) >= min_gb]
    if not cands:
        return None
    pref = [m for m in cands if any(m["name"].lower().startswith(p) for p in prefs)]
    pool = pref if pref else cands
    rank = {"Perfect": 0, "Good": 1, "Marginal": 2, "Too Tight": 3}
    return min(pool, key=lambda m: (rank.get(m["fit_level"], 9), -m["score"]))

out = {}
for cfg,_ in CFGS:
    models = json.load(open(f"/tmp/opencode/{cfg}.json"))["models"]
    fam = {}
    for grp, disp, region, inc, exc, prefs in FAM:
        m = pick(models, inc, exc, prefs, MIN_GB[disp])
        if m is None:
            fam[disp] = {"fit":"Missing","raw_tps":0,"scaled_tps":0,"mem":0,"variant":None,"quant":None}
            continue
        raw = m["estimated_tps"] or 0
        fam[disp] = {
            "fit": m["fit_level"], "raw_tps": raw,
            "scaled_tps": round(raw * RATIOS[cfg], 2),
            "mem": m["memory_required_gb"], "variant": m["name"],
            "quant": m["best_quant"],
        }
    out[cfg] = fam

json.dump(out, open("/tmp/opencode/final_matrix3.json","w"), indent=1)

# report: fit + chosen variant per family on a few configs
for grp, disp, region, *_ in FAM:
    row = []
    for cfg,_ in CFGS:
        row.append(f"{out[cfg][disp]['fit'][:4]}")
    v = out["m5max128"][disp]["variant"]
    print(f"{grp:8} {disp:24} {' '.join(row):52} {v}")
missing = [(cfg,d) for cfg,_ in CFGS for g,d,r,*_2 in FAM if out[cfg][d]["fit"]=="Missing"]
print("MISSING:", missing)
