# Hermes source rollback addendum — hermes-state-snapshot-20260616-153552

建立時間：2026-06-16 16:04:36 CST
目的：Hermes 升級前 source repo rollback 材料索引。此檔不含密碼、token、.env 或 auth JSON 內容。

## 版本與來源

- Hermes pre-update version：`Hermes Agent v0.16.0 (2026.6.5) · upstream c6b0eb4d`
- Source repo：`/home/chien/.hermes/hermes-agent`
- Pre-update HEAD：`24f74eb88853162899fe345dc34a9c5a20f66657`
- Target origin/main：`c6b0eb4de0e5010a752e312c0577a4d04d2a08a5`
- Rollback branch：`backup/pre-update-20260616_152804`
- Source backup dir：`/home/chien/.hermes/backups/hermes-agent-repo-preupdate_20260616_152804`

## Dirty / untracked 狀態

```text
## main...origin/main [behind 377]
 M optional-skills/mlops/training/trl-fine-tuning/SKILL.md
 M skills/mlops/evaluation/lm-evaluation-harness/SKILL.md
 M skills/mlops/inference/vllm/SKILL.md
?? tinker-atropos/
?? tools/reward_model.py

```

## Collision check

```text
== dirty tracked upstream touches ==
== untracked upstream collisions ==
no-collision tinker-atropos/
no-collision tools/reward_model.py

```

## Source rollback commands

```bash
# Hermes source rollback for 20260616_152804
cd /home/chien/.hermes/hermes-agent
git reset --hard backup/pre-update-20260616_152804
git apply --3way /home/chien/.hermes/backups/hermes-agent-repo-preupdate_20260616_152804/tracked-local.diff || true
tar -xzf /home/chien/.hermes/backups/hermes-agent-repo-preupdate_20260616_152804/untracked.tgz -C /home/chien/.hermes/hermes-agent
# Do not restore syntax-broken tools/*.py into tools/ unless py_compile passes.
sudo systemctl restart hermes-gateway.service
/home/chien/.local/bin/hermes gateway status

```

## Post-rollback verification

```bash
cd /home/chien/.hermes/hermes-agent
python3 -m compileall -q run_agent.py cli.py model_tools.py toolsets.py hermes_cli gateway tools agent cron plugins
/home/chien/.local/bin/hermes --version
/home/chien/.local/bin/hermes config check
/home/chien/.local/bin/hermes cron list
/home/chien/.local/bin/hermes gateway status
journalctl -u hermes-gateway.service -n 80 --no-pager
```

## Safety notes

- 不要還原 syntax-broken `tools/*.py` 到 `tools/`，除非先通過 `python3 -m py_compile`。
- 不要把 `.env`、`auth.json`、OAuth token 或備份解密密碼貼給第三方。
- Hermes home/config/session 的 encrypted backup 已由四地備份處理；source repo rollback 由本 addendum 指向本機 source backup。
