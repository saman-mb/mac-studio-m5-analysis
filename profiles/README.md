# llmfit hardware profiles for Apple Silicon SKUs

Each file is a schema_version 1 profile consumed by:

```sh
llmfit --profile profiles/<stem>.json fit --json
```

| Field | Source |
|---|---|
| `total_ram_gb` | Apple configure-to-order unified memory |
| `gpu_memory_bandwidth_gbps` / `ddr_bandwidth_gbps` | Published memory bandwidth for that chip/SKU |
| `unified_memory` | always `true` |
| `match.gpu_name_contains` | provenance only (llmfit does not auto-select) |

CPU core counts are recorded in `scripts/machines.json` for documentation; the
profile schema has no cores field yet.

Regenerate from `scripts/machines.json` if the table changes — keep names equal
to the filename stem (`m5max128.json` → `"name": "m5max128"`).
