<p align="center"><img src="resource/icon.png" width="96" alt="粉象网购省钱管家"></p>

# 粉象网购省钱管家 Skill

中文 | [English](README_en.md)

## 产品介绍

**粉象网购省钱管家**是一个给 AI 助手用的网购省钱技能（Agent Skill），与粉象 App 里的 AI 省钱管家是同一套判断。装上之后，Claude Code、Cursor 等支持 Skills 的 AI 工具可以：

* **发链接判断值不值得买**：一次给出结论、到手价、全网同款比价、历史价走势和省钱方案
* **说型号全网找最低价**：同款同规格比价，相近款会说清差在哪
* **说需求推荐商品**：按预算、用途、送礼对象推荐，需求不清楚时先帮你问清楚
* **批量对比**：2–5 个商品一次比完

覆盖淘宝/天猫、京东、唯品会；抖音、拼多多等解析不了的链接，可以按商品标题比价。

## 产品特点

### 和粉象 App 同一套判断

购买建议、同款判定、商品推荐都在粉象服务端完成，与 App 里的 AI 省钱管家用同一套引擎、同一份历史价数据。AI 只做两件事：选对工具，照结果说话。

### 只说查得到的

价格都来自实时查询；到手价、券后价、国补、新人价分开说，不混在一起。查不到就说查不到，不凭记忆补价格，也不编价保、赠品、物流这类没查到的信息。

### 回答好读

结论一句话 → 到手价和下单链接 → 比价表 → 历史价走势和价格轨迹 → 下一步。比价一律用表格，手机上一屏看得清。

### 开箱即用

免费，不需要注册，也不需要 API Key。推荐连上粉象 MCP 服务；没连上时，Skill 自带的 Python 脚本（只用标准库）也能直接查询。

## 能力介绍

| 你给什么 | 工具 | 返回什么 |
| --- | --- | --- |
| 1 个商品链接、淘口令或整段分享文案，问值不值得买 | `buy_advice` | 结论、到手价、同款比价、历史价、省钱方案 |
| 2–5 个商品链接，要对比 | `batch_analyze` | 每件的结论、到手价和更省的渠道 |
| 只说型号或商品名，问哪里便宜 | `compare_by_name` | 全网同款各店到手价，从低到高 |
| 说需求让推荐（预算、用途、送礼对象） | `recommend_goods` | 分组推荐的在售商品；需求不清楚时先给澄清问题 |
| 按关键词看看有哪些商品 | `goods_search` | 在售商品列表，可限价格区间、只看官方店 |
| 只要历史价曲线 | `history_price` | 收录以来的全部券后价变价点 |
| 只要比价表 | `compare_price` | 同款各渠道报价 |
| 只问怎么买最省 | `saving_plan` | 换店、会员、凑单等买法和步骤 |

所有工具都只读：不下单，不改任何账号数据。

## 快速接入

### 方式一：Claude Code 插件（推荐，一次装好 Skill 和 MCP）

在 Claude Code 对话里执行：

```text
/plugin marketplace add fenxianglife-ai/fenxianglife-skills
/plugin install fenxiang-saving-assistant@fenxianglife-skills
```

或者在终端执行：

```bash
claude plugin marketplace add fenxianglife-ai/fenxianglife-skills
claude plugin install fenxiang-saving-assistant@fenxianglife-skills
```

装好后按提示执行 `/reload-plugins`，或重新打开 Claude Code。插件会同时装上 Skill 和粉象 MCP 服务，不用再做下面的手动步骤。

### 方式二：手动安装（Claude Code、Cursor 等）

#### 第一步：获取 Skill

```bash
git clone https://github.com/fenxianglife-ai/fenxianglife-skills.git
cd fenxianglife-skills
```

也可以在仓库页面点 **Code → Download ZIP** 下载后解压。

#### 第二步：放进 AI 工具的 Skills 目录

| 工具 | Skills 目录 |
| --- | --- |
| Claude Code | 个人：`~/.claude/skills/`；单个项目：`<项目>/.claude/skills/` |
| Cursor | `<项目>/.cursor/skills/` |
| 其他支持 Agent Skills（`SKILL.md`）的工具 | 该工具的 skills 目录 |

**软链接（推荐，`git pull` 后自动生效）**

```bash
# macOS / Linux（以 Claude Code 个人目录为例）
mkdir -p ~/.claude/skills
ln -s "$(pwd)/fenxiang-saving-assistant" ~/.claude/skills/fenxiang-saving-assistant

# Windows（以管理员身份运行 CMD）
mklink /D %USERPROFILE%\.claude\skills\fenxiang-saving-assistant C:\path\to\fenxianglife-skills\fenxiang-saving-assistant
```

**直接复制**

```bash
cp -r fenxiang-saving-assistant ~/.claude/skills/
```

放好后的目录应该是：

```text
~/.claude/skills/
└── fenxiang-saving-assistant/
    ├── SKILL.md
    ├── references/
    └── scripts/
```

#### 第三步：连接粉象 MCP 服务（推荐）

服务地址：`https://api.fenxianglife.com/njia/mcp`（MCP Streamable HTTP，免费，不需要 API Key）

**Claude Code**

```bash
claude mcp add --transport http fenxiang-saving-assistant https://api.fenxianglife.com/njia/mcp
```

**Cursor**：在 `<项目>/.cursor/mcp.json` 或 `~/.cursor/mcp.json` 里加上

```json
{
  "mcpServers": {
    "fenxiang-saving-assistant": {
      "url": "https://api.fenxianglife.com/njia/mcp"
    }
  }
}
```

**其他工具**：按各自文档添加一个 Streamable HTTP 类型的 MCP 服务，地址同上。

> 不连 MCP 也能用：Skill 会改用自带的 `scripts/fenxiang_mcp.py`（需要 Python 3，只用标准库）直接查询。

#### 第四步：验证

先跑一遍全链路自检（先搜索拿到在售商品链接，再逐个验证 8 个工具）：

```bash
python3 fenxiang-saving-assistant/scripts/verify.py
```

最后一行是 `summary: passed=… failed=0 …` 就说明服务可用。然后在 AI 对话里问一句：

```text
iPhone 17 Pro 256G 哪里买最便宜
```

如果 AI 调用了 `compare_by_name`（或运行了 Skill 里的脚本），并用表格给出各店到手价和链接，就说明装好了。

## 使用示例

### 示例 1：发链接问值不值得买

```text
<粘贴商品链接、淘口令或分享文案> 这个现在值不值得买？
```

### 示例 2：说型号找最低价

```text
iPhone 17 Pro 256G 哪里买最便宜
```

### 示例 3：说需求让推荐

```text
500 元以内送妈妈的生日礼物推荐一下
```

### 示例 4：几个商品对比

```text
<链接 1> <链接 2> <链接 3> 这几个哪个更划算？
```

### 回答示例（示意，价格以实时查询为准）

> **全网同款最低：京东 / Apple产品京东自营旗舰店 ¥7999.00**
>
> | # | 到手价 | 链接 | 平台 | 店铺 | 说明 |
> |---|---|---|---|---|---|
> | 1 | ¥7999.00 | 去看看 | 京东 | Apple产品京东自营旗舰店 | 最低、官方/自营 |
> | 2 | ¥8299.00 | 去看看 | 天猫 | Apple Store 官方旗舰店 | 贵 ¥300.00、官方/自营 |
>
> 下一步：点最低价那一行的链接领券下单。
> 价格说明：到手价已扣店铺券和平台优惠

## 价格口径

| 说法 | 含义 |
| --- | --- |
| 到手价 | 直接下单的价格：已扣店铺券和平台优惠（立减、淘金币等） |
| 券后价 | 只扣店铺券的价格；历史价按券后价记录 |
| 方案价 | 要会员、凑单等条件才能拿到的价格，会和条件一起说 |
| 国补 / 新人价 | 要资格才能拿到，单独说，不算进到手价 |
| 全网最低 | 同款同规格里最便宜的渠道；第三方店铺、异常低价会单独提示风险 |

## 目录结构

```text
fenxianglife-skills/
├── .claude-plugin/
│   └── marketplace.json        # Claude Code 插件市场：Skill 和 MCP 一起装
├── fenxiang-saving-assistant/
│   ├── SKILL.md                # 技能主文件（AI 入口）：选工具、回答骨架、价格口径
│   ├── references/
│   │   └── tools.md            # 8 个工具的入参、出参和价格字段
│   └── scripts/
│       ├── fenxiang_mcp.py     # MCP 客户端（只用 Python 标准库），没连 MCP 时用
│       └── verify.py           # 全链路自检
└── resource/
    └── icon.png
```

## 常见问题

### Q: AI 没用这个 Skill，自己上网搜价了

**A:** 请检查：

1. Skill 放在了工具的 skills 目录下，且 `SKILL.md` 就在 `fenxiang-saving-assistant/` 这一层；
2. 提问时带上「粉象省钱管家」，或在 Claude Code 里用 `/fenxiang-saving-assistant` 直接调用；
3. MCP 已连上（Claude Code 里执行 `/mcp` 能看到 `fenxiang-saving-assistant`）。

### Q: 抖音、拼多多的链接查不了

**A:** 这类链接暂时解析不了，AI 会请你发商品标题，再按名称比价。也可以直接把分享文案里的商品名发给它。

### Q: 价格和商品页上看到的不一样

**A:** 到手价已扣店铺券和平台优惠，不含国补、新人价、会员价，这些会单独说明。价格实时变化，以下单页为准。

### Q: 运行脚本报 `CERTIFICATE_VERIFY_FAILED`

**A:** 多半是 macOS 上从 python.org 安装的 Python 没带 CA 证书。运行一次 Python 安装目录里的 `Install Certificates.command`，或者在命令前加 `SSL_CERT_FILE=/etc/ssl/cert.pem`。不要用 `--insecure` 跳过证书校验。

### Q: 收费吗？需要注册或 API Key 吗？

**A:** 免费，不需要注册，也不需要 API Key。

### Q: 如何更新？

**A:** 插件安装的执行 `claude plugin update fenxiang-saving-assistant@fenxianglife-skills`；软链接安装的在仓库目录 `git pull`；复制安装的重新复制一次。

### Q: 遇到问题怎么反馈？

**A:** 在本仓库提 Issue，附上提问原文和商品链接。

## 版本

当前版本 1.0.7，与粉象 MCP 服务端版本一致。

## 相关链接

* [粉象生活](https://www.fenxianglife.com)
* [Claude Code Skills 文档](https://code.claude.com/docs/en/skills)
* [Claude Code MCP 文档](https://code.claude.com/docs/en/mcp)
* [Claude Code 插件市场文档](https://code.claude.com/docs/en/plugin-marketplaces)

**买之前问一句，花得明明白白。**
