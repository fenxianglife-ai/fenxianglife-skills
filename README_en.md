<p align="center"><img src="resource/icon.png" width="96" alt="Fenxiang Saving Assistant"></p>

# Fenxiang Saving Assistant Skill

[中文](README.md) | English

## Overview

**Fenxiang Saving Assistant** (粉象网购省钱管家) is an Agent Skill that helps AI assistants save money on online shopping. It uses the same judgement as the AI saving assistant in the Fenxiang app. Once installed, Claude Code, Cursor and other tools that support Skills can:

* **Tell whether a product link is worth buying now**: verdict, final price, same-item price comparison, price history and saving plan in one answer
* **Find the lowest price for a model**: compares the same item and spec across stores, and says exactly how a similar item differs
* **Recommend products for a need**: by budget, use or gift recipient, asking clarifying questions first when the need is vague
* **Compare several products**: 2–5 products at once

Covers Taobao/Tmall, JD and Vipshop. For links that cannot be parsed (Douyin, Pinduoduo, etc.), it compares by product title instead.

## Features

### Same judgement as the Fenxiang app

Buy advice, same-item matching and recommendations all run on Fenxiang's servers, with the same engine and price-history data as the app. The AI only does two things: pick the right tool, and answer from the result.

### Only what can be verified

All prices come from live queries. Final price, coupon price, government subsidies and new-user prices are reported separately. If something cannot be found, the assistant says so instead of filling in prices from memory or making up price protection, gifts or shipping details.

### Easy-to-read answers

One-line verdict → final price and order link → comparison table → price trend and price track → next step. Comparisons are always tables that fit on a phone screen.

### Ready to use

Free, no sign-up and no API key. Connecting the Fenxiang MCP server is recommended; without it, the Python scripts bundled with the Skill (standard library only) can query the service directly.

## Capabilities

| You give | Tool | You get |
| --- | --- | --- |
| One product link, Taobao password or share text, asking whether to buy | `buy_advice` | Verdict, final price, same-item comparison, price history, saving plan |
| 2–5 product links to compare | `batch_analyze` | Verdict, final price and cheaper channel for each |
| Only a model or product name, asking where it is cheapest | `compare_by_name` | Final price at each store for the same item, lowest first |
| A need (budget, use, gift recipient) | `recommend_goods` | Grouped recommendations of products on sale; clarifying questions first if needed |
| A keyword to browse | `goods_search` | Products on sale, optionally by price range or official stores only |
| Price history only | `history_price` | Every coupon-price change since tracking began |
| Comparison table only | `compare_price` | Prices of the same item across channels |
| Cheapest way to buy only | `saving_plan` | Switching stores, membership, bundling, with steps |

All tools are read-only: they never place orders or change any account data.

## Quick start

### Option 1: Claude Code plugin (recommended, installs the Skill and MCP together)

In a Claude Code session:

```text
/plugin marketplace add fenxianglife-ai/fenxianglife-skills
/plugin install fenxiang-saving-assistant@fenxianglife-skills
```

Or in your terminal:

```bash
claude plugin marketplace add fenxianglife-ai/fenxianglife-skills
claude plugin install fenxiang-saving-assistant@fenxianglife-skills
```

Then run `/reload-plugins` when prompted, or restart Claude Code. The plugin installs both the Skill and the Fenxiang MCP server, so the manual steps below are not needed.

### Option 2: Manual install (Claude Code, Cursor, etc.)

#### Step 1: Get the Skill

```bash
git clone https://github.com/fenxianglife-ai/fenxianglife-skills.git
cd fenxianglife-skills
```

Or click **Code → Download ZIP** on the repository page and unzip it.

#### Step 2: Put it in your tool's skills directory

| Tool | Skills directory |
| --- | --- |
| Claude Code | Personal: `~/.claude/skills/`; one project: `<project>/.claude/skills/` |
| Cursor | `<project>/.cursor/skills/` |
| Other tools that support Agent Skills (`SKILL.md`) | That tool's skills directory |

**Symlink (recommended, picks up `git pull` automatically)**

```bash
# macOS / Linux (Claude Code personal directory as an example)
mkdir -p ~/.claude/skills
ln -s "$(pwd)/fenxiang-saving-assistant" ~/.claude/skills/fenxiang-saving-assistant

# Windows (CMD as administrator)
mklink /D %USERPROFILE%\.claude\skills\fenxiang-saving-assistant C:\path\to\fenxianglife-skills\fenxiang-saving-assistant
```

**Copy**

```bash
cp -r fenxiang-saving-assistant ~/.claude/skills/
```

The result should look like:

```text
~/.claude/skills/
└── fenxiang-saving-assistant/
    ├── SKILL.md
    ├── references/
    └── scripts/
```

#### Step 3: Connect the Fenxiang MCP server (recommended)

Endpoint: `https://api.fenxianglife.com/njia/mcp` (MCP Streamable HTTP, free, no API key)

**Claude Code**

```bash
claude mcp add --transport http fenxiang-saving-assistant https://api.fenxianglife.com/njia/mcp
```

**Cursor**: add this to `<project>/.cursor/mcp.json` or `~/.cursor/mcp.json`

```json
{
  "mcpServers": {
    "fenxiang-saving-assistant": {
      "url": "https://api.fenxianglife.com/njia/mcp"
    }
  }
}
```

**Other tools**: add a Streamable HTTP MCP server with the same endpoint, following the tool's documentation.

> Works without MCP too: the Skill falls back to its bundled `scripts/fenxiang_mcp.py` (Python 3, standard library only).

#### Step 4: Verify

Run the end-to-end self-check (it searches for products on sale, then exercises all 8 tools with their links):

```bash
python3 fenxiang-saving-assistant/scripts/verify.py
```

If the last line reads `summary: passed=… failed=0 …`, the service is reachable. Then ask your AI assistant:

```text
iPhone 17 Pro 256G 哪里买最便宜
```

If it calls `compare_by_name` (or runs the bundled script) and answers with a table of final prices and links per store, you are all set.

## Examples

The service answers in Chinese, so Chinese prompts work best.

### Example 1: Is this link worth buying?

```text
<paste a product link, Taobao password or share text> 这个现在值不值得买？
```

### Example 2: Where is a model cheapest?

```text
iPhone 17 Pro 256G 哪里买最便宜
```

### Example 3: Recommend something for a need

```text
500 元以内送妈妈的生日礼物推荐一下
```

### Example 4: Compare several products

```text
<link 1> <link 2> <link 3> 这几个哪个更划算？
```

## Price terms

| Term | Meaning |
| --- | --- |
| Final price (到手价) | What you pay when ordering directly: store coupons and platform discounts already applied |
| Coupon price (券后价) | Price after store coupons only; price history is recorded in coupon price |
| Plan price (方案价) | Needs a condition such as membership or bundling; always stated with the condition |
| Subsidy / new-user price | Needs eligibility; stated separately and never included in the final price |
| Lowest across stores | Cheapest channel for the same item and spec; third-party stores and suspiciously low prices are flagged |

## Layout

```text
fenxianglife-skills/
├── .claude-plugin/
│   └── marketplace.json        # Claude Code marketplace: installs the Skill and MCP together
├── fenxiang-saving-assistant/
│   ├── SKILL.md                # Skill entry point: tool selection, answer outline, price terms
│   ├── references/
│   │   └── tools.md            # Inputs, outputs and price fields of the 8 tools
│   └── scripts/
│       ├── fenxiang_mcp.py     # MCP client (Python standard library only), used without MCP
│       └── verify.py           # End-to-end self-check
└── resource/
    └── icon.png
```

## FAQ

### Q: The AI searched the web instead of using the Skill

**A:** Check that:

1. The Skill is in your tool's skills directory, with `SKILL.md` directly inside `fenxiang-saving-assistant/`;
2. Your question mentions 「粉象省钱管家」, or you invoke it directly with `/fenxiang-saving-assistant` in Claude Code;
3. The MCP server is connected (`/mcp` in Claude Code lists `fenxiang-saving-assistant`).

### Q: Douyin or Pinduoduo links do not work

**A:** These links cannot be parsed yet. The assistant will ask for the product title and compare by name; you can also send the product name from the share text directly.

### Q: The price differs from the product page

**A:** The final price includes store coupons and platform discounts, but not subsidies, new-user or membership prices, which are stated separately. Prices change in real time; the order page is authoritative.

### Q: The scripts fail with `CERTIFICATE_VERIFY_FAILED`

**A:** Usually Python installed from python.org on macOS has no CA certificates. Run `Install Certificates.command` in the Python install folder once, or prefix the command with `SSL_CERT_FILE=/etc/ssl/cert.pem`. Do not skip verification with `--insecure`.

### Q: Is it free? Do I need an account or API key?

**A:** It is free, with no sign-up and no API key.

### Q: How do I update?

**A:** Plugin install: `claude plugin update fenxiang-saving-assistant@fenxianglife-skills`. Symlink install: `git pull` in the repository. Copy install: copy it again.

### Q: How do I report a problem?

**A:** Open an issue in this repository with your original question and the product link.

## Version

Current version 1.0.7, the same as the Fenxiang MCP server.

## Links

* [Fenxiang](https://www.fenxianglife.com)
* [Claude Code Skills](https://code.claude.com/docs/en/skills)
* [Claude Code MCP](https://code.claude.com/docs/en/mcp)
* [Claude Code plugin marketplaces](https://code.claude.com/docs/en/plugin-marketplaces)
