# Comfortable SSD sizes (from llmfit `disk_size_gb`)

need_gb = 100 (OS/apps) + sum(top 3 fitting disk_size_gb) + max(those) download scratch; round up to Apple SSD SKU; if that SKU would be >85% full, bump one tier.

| Config | Fitting blog models | Keep set (largest 3) | Need (GB) | Floor SSD | Comfortable SSD |
|---|---:|---|---:|---|---|
| Entry: Mac mini M6 16GB (`m6_16`) | 6 | ERNIE 4.5 21B-A3B (14.8GB), gpt-oss-20b 21B (14.6GB), Qwen3.8 27B (13.3GB) | 158 | 256GB | **256GB** |
| Compact-: Mac mini M6 24GB (`m6_24`) | 8 | ERNIE 4.5 21B-A3B (22.9GB), gpt-oss-20b 21B (22.6GB), Qwen3.8 27B (22.2GB) | 191 | 256GB | **256GB** |
| Compact: Mac mini M6 32GB (`m6_32`) | 8 | Qwen3.8 27B (29.2GB), Gemma 4 26B-A4B (27.9GB), Nemotron 3 Nano 30B (25.3GB) | 211 | 256GB | **256GB** |
| Pro mini: M5 Pro 24GB (`m5pro_24`) | 8 | ERNIE 4.5 21B-A3B (22.9GB), gpt-oss-20b 21B (22.6GB), Qwen3.8 27B (22.2GB) | 191 | 256GB | **256GB** |
| Pro mini: M5 Pro 48GB (`m5pro_48`) | 8 | Gemma 4 31B (34.3GB), Nemotron 3 Nano 30B (33.2GB), Granite 4.1 30B (30.3GB) | 232 | 256GB | **512GB** |
| Pro mini: M5 Pro 64GB (`m5pro_64`) | 11 | Nemotron 3 Super 120B (59.3GB), gpt-oss-120b 117B (57.8GB), Llama 4 Scout 109B (52.1GB) | 329 | 512GB | **512GB** |
| Studio Max 36GB (`m5max36`) | 8 | Nemotron 3 Nano 30B (33.2GB), Granite 4.1 30B (30.3GB), Qwen3.8 27B (29.2GB) | 226 | 256GB | **512GB** |
| Studio Max 48GB (`m5max48`) | 8 | Gemma 4 31B (34.3GB), Nemotron 3 Nano 30B (33.2GB), Granite 4.1 30B (30.3GB) | 232 | 256GB | **512GB** |
| Studio Max 64GB (`m5max64`) | 11 | Nemotron 3 Super 120B (59.3GB), gpt-oss-120b 117B (57.8GB), Llama 4 Scout 109B (52.1GB) | 329 | 512GB | **512GB** |
| Sweet spot: Studio Max 128GB (`m5max128`) | 11 | gpt-oss-120b 117B (126.4GB), Llama 4 Scout 109B (114.1GB), Nemotron 3 Super 120B (98.9GB) | 566 | 1TB | **1TB** |
| Studio Ultra 96GB (`m5ultra96`) | 11 | Llama 4 Scout 109B (86.9GB), Nemotron 3 Super 120B (84.1GB), gpt-oss-120b 117B (81.9GB) | 440 | 512GB | **1TB** |
| Frontier-adjacent: Studio Ultra 256GB (`m5ultra256`) | 15 | MiniMax M3 427B (247.7GB), DeepSeek V4-Flash 284B (243.3GB), Qwen3.5 397B-A17B (234.0GB) | 1073 | 2TB | **2TB** |
| Full frontier: Studio Ultra 512GB (`m5ultra512`) | 18 | Nemotron 3 Ultra 550B (448.4GB), MiniMax M3 427B (448.4GB), GLM-5.2 743B (437.0GB) | 1882 | 2TB | **4TB** |

## Per-model disk sizes on Ultra 512GB dump

Taken from `m5ultra512.json` (llmfit best_quant for that machine).

| Model | HF ID | disk_size_gb | fit | quant |
|---|---|---:|---|---|
| Kimi K3 2.8T | `moonshotai/Kimi-K3` | 3205.41 | Too Tight | Q4_K_M |
| DeepSeek V4-Pro 1.6T | `deepseek-ai/DeepSeek-V4-Pro-0813` | 957.29 | Too Tight | Q4_K_M |
| LongCat 2.0 1.6T | `meituan-longcat/LongCat-2.0` | 1029.83 | Too Tight | Q4_K_M |
| Ling 2.6 1T | `inclusionAI/Ling-2.6-1T` | 379.49 | Good | Q2_K |
| GLM-5.2 743B | `zai-org/GLM-5.2` | 436.96 | Good | Q4_K_M |
| Nemotron 3 Ultra 550B | `nvidia/NVIDIA-Nemotron-3-Ultra-550B-A55B-BF16` | 448.42 | Good | Q6_K |
| Llama 4 Maverick 400B | `meta-llama/Llama-4-Maverick-17B-128E-Instruct` | 421.66 | Perfect | Q8_0 |
| Qwen3.5 397B-A17B | `Qwen/Qwen3.5-397B-A17B` | 423.57 | Perfect | Q8_0 |
| DeepSeek V4-Flash 284B | `deepseek-ai/DeepSeek-V4-Flash-0731` | 319.39 | Perfect | Q8_0 |
| MiniMax M3 427B | `MiniMaxAI/MiniMax-M3` | 448.39 | Perfect | Q8_0 |
| Kimi K2.6 1.1T | `moonshotai/Kimi-K2.6` | 391.68 | Too Tight | Q2_K |
| Nemotron 3 Super 120B | `nvidia/NVIDIA-Nemotron-3-Super-120B-A12B-BF16` | 129.79 | Perfect | Q8_0 |
| gpt-oss-120b 117B | `openai/gpt-oss-120b` | 126.43 | Perfect | Q8_0 |
| Llama 4 Scout 109B | `meta-llama/Llama-4-Scout-17B-16E-Instruct` | 114.07 | Perfect | Q8_0 |
| Gemma 4 31B | `google/gemma-4-31B-it` | 34.32 | Perfect | Q8_0 |
| Gemma 4 26B-A4B | `google/gemma-4-26B-A4B-it` | 27.87 | Perfect | Q8_0 |
| Qwen3.8 27B | `Qwen/Qwen3.8-27B` | 29.17 | Perfect | Q8_0 |
| ERNIE 4.5 21B-A3B | `baidu/ERNIE-4.5-21B-A3B-Thinking` | 22.92 | Perfect | Q8_0 |
| Granite 4.1 30B | `ibm-granite/granite-4.1-30b` | 30.31 | Perfect | Q8_0 |
| Nemotron 3 Nano 30B | `nvidia/NVIDIA-Nemotron-3-Nano-30B-A3B-BF16` | 33.16 | Perfect | Q8_0 |
| Gemma 4 12B | `unsloth/gemma-4-12b-it` | 12.56 | Perfect | Q8_0 |
| gpt-oss-20b 21B | `openai/gpt-oss-20b` | 22.59 | Perfect | Q8_0 |

