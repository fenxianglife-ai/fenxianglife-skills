#!/usr/bin/env python3
"""粉象 MCP Streamable HTTP 最小客户端（仅标准库）。

用法：
  python3 fenxiang_mcp.py buy_advice '{"goodsUrl":"<商品链接或分享文案>"}'
  python3 fenxiang_mcp.py compare_by_name '{"productName":"iPhone 17 Pro 256G"}'
  python3 fenxiang_mcp.py tools/list
  python3 fenxiang_mcp.py initialize        # 看服务端下发的使用说明
  python3 fenxiang_mcp.py prompts/list

环境变量：
  FENXIANG_MCP_URL          默认 https://api.fenxianglife.com/njia/mcp
  FENXIANG_MCP_CHANNEL      渠道（workbuddy、doubao 等），渠道包里已写好，一般不用设
  FENXIANG_MCP_API_KEY      粉象AI开放平台的 API Key，在 https://ai.fenxianglife.com 申请（测试 Key 免费）。
                            可以不填：不带 Key 时同一 IP 每分钟最多 60 次，只返回 Markdown 结论

TLS：默认严格校验证书；仅内网自签名测试环境可显式加 --insecure。
"""

import argparse
import itertools
import json
import os
import ssl
import sys
import urllib.error
import urllib.request

DEFAULT_URL = "https://api.fenxianglife.com/njia/mcp"
# 渠道包打包时由 build.py 写入（需求 CALL-20）：WorkBuddy、豆包的包分别是 workbuddy、doubao，GitHub 的为空；
# 也可以用环境变量 FENXIANG_MCP_CHANNEL 指定。请求地址带上 ?channel=，服务端才认得出官方渠道
DEFAULT_CHANNEL = ""
SKILL_VERSION = "1.0.9"
USER_AGENT = "fenxiang-saving-assistant-skill/" + SKILL_VERSION
APPLY_URL = "https://ai.fenxianglife.com"
TOOLS = (
    "buy_advice", "batch_analyze", "compare_by_name", "recommend_goods",
    "goods_search", "history_price", "compare_price", "saving_plan",
)


class McpError(RuntimeError):
    pass


class McpClient:
    def __init__(self, url, api_key, timeout=60, insecure=False):
        self.url = url
        self.api_key = api_key
        self.timeout = timeout
        self.context = ssl._create_unverified_context() if insecure else None
        self._ids = itertools.count(1)

    def rpc(self, method, params=None):
        payload = {"jsonrpc": "2.0", "id": next(self._ids), "method": method, "params": params or {}}
        headers = {
            "Content-Type": "application/json",
            "Accept": "application/json, text/event-stream",
            "User-Agent": USER_AGENT,
        }
        if self.api_key:
            headers["Authorization"] = "Bearer " + self.api_key
        request = urllib.request.Request(
            self.url,
            data=json.dumps(payload, ensure_ascii=False).encode("utf-8"),
            headers=headers,
            method="POST",
        )
        try:
            with urllib.request.urlopen(request, timeout=self.timeout, context=self.context) as response:
                body = response.read().decode("utf-8")
                content_type = response.headers.get("Content-Type", "")
        except urllib.error.HTTPError as error:
            body = error.read().decode("utf-8", errors="replace")
            raise McpError(http_error_message(error.code, body, error.headers.get("Retry-After"),
                                              bool(self.api_key))) from error
        except (urllib.error.URLError, OSError) as error:
            # 读超时（TimeoutError）不是 URLError，一并转成 McpError，调用方统一按失败处理
            raise McpError("connection failed: %s" % error) from error

        if "text/event-stream" in content_type:
            body = _last_sse_data(body)
        try:
            data = json.loads(body)
        except json.JSONDecodeError as error:
            raise McpError("invalid JSON response: %s" % body[:500]) from error
        if data.get("error"):
            raise McpError(json.dumps(data["error"], ensure_ascii=False))
        return data.get("result") or {}

    def initialize(self):
        return self.rpc("initialize", {
            "protocolVersion": "2025-06-18",
            "capabilities": {},
            "clientInfo": {"name": "fenxiang-skill-script", "version": "2.0.0"},
        })

    def list_tools(self):
        result = self.rpc("tools/list")
        return result.get("tools") or []

    def list_prompts(self):
        result = self.rpc("prompts/list")
        return result.get("prompts") or []

    def call_tool(self, name, arguments):
        result = self.rpc("tools/call", {"name": name, "arguments": arguments})
        if result.get("isError"):
            raise McpError(_first_text(result) or "tool returned isError=true")
        text = _first_text(result)
        structured = result.get("structuredContent")
        return text, parse_text(text), structured


def http_error_message(status, body, retry_after=None, has_key=False):
    """鉴权、限流错误给出可读提示，带上服务端的 code、message 和 requestId，方便反馈。"""
    try:
        data = json.loads(body)
    except (TypeError, json.JSONDecodeError):
        data = None
    if not isinstance(data, dict):
        return "HTTP %s: %s" % (status, (body or "")[:500])
    detail = "HTTP %s，code %s：%s" % (status, data.get("code"), data.get("message"))
    if data.get("requestId"):
        detail += "（requestId %s）" % data["requestId"]
    wait = " %s 秒" % retry_after if retry_after else "一会儿"
    if status == 401:
        hint = ("API Key 无效：检查 FENXIANG_MCP_API_KEY，Key 重置后要换成新的" if has_key
                else "这个接口需要 API Key，在 %s 申请后设置 FENXIANG_MCP_API_KEY" % APPLY_URL)
    elif status == 403:
        hint = "API Key 已暂停、停用，或没有开通这项能力：到 %s 的工作台处理" % APPLY_URL
    elif status == 429:
        hint = ("调用太快或本月额度用完：等%s再试，额度用完要等下月 1 日" % wait if has_key
                else "不带 API Key 时同一 IP 每分钟最多 60 次：等%s再试，或在 %s 申请 API Key" % (wait, APPLY_URL))
    else:
        return detail
    return "%s。%s" % (hint, detail)


def _first_text(result):
    content = result.get("content") or []
    for block in content:
        if isinstance(block, dict) and block.get("type") == "text":
            return block.get("text")
    return None


def _last_sse_data(body):
    data_lines = []
    for line in body.splitlines():
        if line.startswith("data:"):
            data_lines.append(line[5:].strip())
    if not data_lines:
        return body
    for value in reversed(data_lines):
        try:
            parsed = json.loads(value)
        except json.JSONDecodeError:
            continue
        if isinstance(parsed, dict) and ("result" in parsed or "error" in parsed):
            return json.dumps(parsed, ensure_ascii=False)
    return data_lines[-1]


def parse_text(text):
    if not text:
        return None
    try:
        data = json.loads(text)
    except (TypeError, json.JSONDecodeError):
        return None
    if isinstance(data, str):
        try:
            return json.loads(data)
        except json.JSONDecodeError:
            return data
    return data


def load_api_key(path=None):
    key = os.environ.get("FENXIANG_MCP_API_KEY", "").strip()
    if not key and path:
        with open(os.path.expanduser(path), "r", encoding="utf-8") as handle:
            key = handle.read().strip()
    return key


def build_client(args):
    url = with_channel(args.url or os.environ.get("FENXIANG_MCP_URL") or DEFAULT_URL,
                       os.environ.get("FENXIANG_MCP_CHANNEL") or DEFAULT_CHANNEL)
    return McpClient(url, load_api_key(args.api_key_file), timeout=args.timeout, insecure=args.insecure)


def with_channel(url, channel):
    """地址里还没有 channel 时带上（渠道包的 Skill 由 build.py 写好 DEFAULT_CHANNEL）。"""
    if not channel or "channel=" in url:
        return url
    return url + ("&" if "?" in url else "?") + "channel=" + channel


def main():
    parser = argparse.ArgumentParser(description="粉象 MCP HTTP 客户端")
    parser.add_argument("tool", help=" / ".join(TOOLS) + " / tools/list / prompts/list / initialize")
    parser.add_argument("arguments", nargs="?", default="{}", help="工具参数 JSON，默认 {}")
    parser.add_argument("--url", help="MCP 地址，默认 FENXIANG_MCP_URL 或生产地址")
    parser.add_argument("--api-key-file", help="只包含 API Key 的文件")
    parser.add_argument("--timeout", type=int, default=120)
    parser.add_argument("--insecure", action="store_true",
                        help="仅内网自签名测试环境使用：跳过证书校验，生产环境不要使用")
    parser.add_argument("--pretty", action="store_true", help="尝试格式化 JSON 输出")
    args = parser.parse_args()

    try:
        client = build_client(args)
        if args.tool in ("tools/list", "tools_list", "list"):
            for tool in client.list_tools():
                print("%s\t%s" % (tool.get("name"), tool.get("title") or ""))
            return 0
        if args.tool in ("prompts/list", "prompts_list"):
            for prompt in client.list_prompts():
                print("%s\t%s" % (prompt.get("name"), prompt.get("title") or ""))
            return 0
        if args.tool == "initialize":
            result = client.initialize()
            info = result.get("serverInfo") or {}
            print("%s %s" % (info.get("name"), info.get("version")))
            print(result.get("instructions") or "")
            return 0

        try:
            arguments = json.loads(args.arguments)
        except json.JSONDecodeError as error:
            raise McpError("工具参数不是合法 JSON: %s" % error) from error
        text, parsed, structured = client.call_tool(args.tool, arguments)
        if args.pretty and parsed is not None:
            print(json.dumps(parsed, ensure_ascii=False, indent=2))
        elif args.pretty and structured is not None:
            print(json.dumps(structured, ensure_ascii=False, indent=2))
        else:
            print(text if text is not None else json.dumps(structured, ensure_ascii=False))
        return 0
    except McpError as error:
        print("ERROR: %s" % error, file=sys.stderr)
        return 1


if __name__ == "__main__":
    sys.exit(main())
