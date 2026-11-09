# -*- coding: utf-8 -*-
"""Strips instance-specific data out of an exported n8n workflow.

What it removes or replaces:
  credentials blocks        ids and names of credentials inside your n8n
  webhookId                 per-instance webhook uuids
  meta.instanceId           a hash that ties every export to your installation
  versionId, workflow id    identifiers of this workflow in your n8n
  data table references     table id and the /projects/<id>/datatables/<id> url
  hardcoded chat ids        replaced with a placeholder or an expression

It also repairs the trailing commas in the Config node, which make the inner
JSON invalid for any strict parser.

    python sanitize.py "AI Lead Hunter - Ukraine.json"
"""
import json
import re
import sys
from pathlib import Path

CHAT_PLACEHOLDER = "YOUR_TELEGRAM_CHAT_ID"
CHAT_EXPRESSION = "={{ $('Config').first().json.telegramChatId }}"
TABLE_NAME = "lead_hunter_memory"
CHAT_ID_RX = re.compile(r"\b\d{8,12}\b")


def fix_trailing_commas(text):
    return re.sub(r",(\s*[\]\}])", r"\1", text)


def clean(path: Path):
    wf = json.loads(path.read_text(encoding="utf-8"))
    report = []

    for node in wf.get("nodes", []):
        name = node.get("name", "?")

        if node.pop("credentials", None) is not None:
            report.append(f"credentials removed from {name}")
        if node.pop("webhookId", None) is not None:
            report.append(f"webhookId removed from {name}")

        params = node.get("parameters", {})

        # Config node: placeholder chat id, valid inner JSON
        raw = params.get("jsonOutput")
        if isinstance(raw, str) and "telegramChatId" in raw:
            fixed = fix_trailing_commas(raw)
            if fixed != raw:
                report.append(f"trailing commas fixed in {name}")
            fixed = re.sub(r'("telegramChatId"\s*:\s*")\d+(")',
                           r"\g<1>" + CHAT_PLACEHOLDER + r"\g<2>", fixed)
            if fixed != raw:
                params["jsonOutput"] = fixed
            try:
                json.loads(fixed)
                report.append(f"{name}: inner JSON is valid")
            except Exception as e:
                report.append(f"{name}: inner JSON STILL INVALID - {e}")

        # Hardcoded chat id on a Telegram node
        chat = params.get("chatId")
        if isinstance(chat, str) and CHAT_ID_RX.fullmatch(chat.strip()):
            params["chatId"] = CHAT_EXPRESSION
            report.append(f"hardcoded chatId in {name} replaced with the Config expression")

        # Data table reference: by name, without ids and project url
        table = params.get("dataTableId")
        if isinstance(table, dict):
            params["dataTableId"] = {"__rl": True, "mode": "name", "value": TABLE_NAME}
            report.append(f"data table id and project url removed from {name}")

    for key in ("versionId", "id"):
        if wf.pop(key, None) is not None:
            report.append(f"workflow {key} removed")
    if wf.pop("meta", None) is not None:
        report.append("meta removed (instanceId)")

    out = path.with_name(path.stem + ".clean.json")
    out.write_text(json.dumps(wf, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    return out, report


def main():
    path = Path(sys.argv[1] if len(sys.argv) > 1 else "AI Lead Hunter - Ukraine.json")
    out, report = clean(path)
    for line in report:
        print(" -", line)
    print("written:", out)


if __name__ == "__main__":
    sys.stdout.reconfigure(encoding="utf-8", errors="replace")
    main()
