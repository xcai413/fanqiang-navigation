#!/usr/bin/env python3
"""免费节点自动抓取+聚合+格式转换"""
import urllib.request, json, base64, os, re, time, socket

# ============================================
# 免费节点源（欢迎PR补充）
# ============================================
SOURCES = [
    {"url": "https://raw.githubusercontent.com/freefq/free/master/v2", "type": "plain", "name": "freefq"},
    {"url": "https://raw.githubusercontent.com/Pawdroid/Free-servers/main/sub", "type": "plain", "name": "Pawdroid"},
    {"url": "https://raw.githubusercontent.com/ermaozi/get_subscribe/main/subscribe/clash.yml", "type": "yaml", "name": "ermaozi"},
    {"url": "https://raw.githubusercontent.com/aiboboxx/clashfree/main/clash.yml", "type": "yaml", "name": "aiboboxx"},
    {"url": "https://raw.githubusercontent.com/MaomoVPN/free/main/clash.yaml", "type": "yaml", "name": "MaomoVPN"},
]

def fetch(url, timeout=15):
    try:
        req = urllib.request.Request(url, headers={"User-Agent": "Mozilla/5.0"})
        return urllib.request.urlopen(req, timeout=timeout).read().decode("utf-8", errors="replace")
    except Exception as e:
        print(f"  ⚠ {url} - {str(e)[:60]}")
        return None

def check_alive(host, port, timeout=3):
    try:
        s = socket.socket()
        s.settimeout(timeout)
        s.connect((host, int(port)))
        s.close()
        return True
    except:
        return False

# 下载
all_proxies = []
seen = set()
print("📥 下载节点...")
for src in SOURCES:
    print(f"  [{src['name']}] {src['url']}")
    content = fetch(src["url"])
    if not content:
        continue
    if src["type"] == "yaml":
        import yaml
        try:
            data = yaml.safe_load(content)
            if data and "proxies" in data:
                for p in data["proxies"]:
                    k = p.get("name","") + p.get("server","")
                    if k and k not in seen:
                        seen.add(k)
                        all_proxies.append(p)
        except:
            pass
    else:
        for line in content.split("\n"):
            line = line.strip()
            if line and not line.startswith("#"):
                if line not in seen:
                    seen.add(line)
                    all_proxies.append({"link": line})
    print(f"    → 累计 {len(all_proxies)} 节点")

print(f"\n📊 总计 {len(all_proxies)} 节点")

# 抽样存活检查
print("\n🔍 存活检查（抽样30个）...")
alive = 0
for p in all_proxies[:30]:
    h = p.get("server", "")
    po = p.get("port", 0)
    if h and po and check_alive(h, po):
        alive += 1
    time.sleep(0.1)
print(f"  存活: {alive}/30")

# 写入 Clash YAML
os.makedirs("free", exist_ok=True)
yaml_proxies = [p for p in all_proxies if "server" in p]
if yaml_proxies:
    import yaml
    with open("free/proxies.yaml", "w") as f:
        f.write(yaml.dump({"proxies": yaml_proxies}, default_flow_style=False))
    print(f"  ✅ free/proxies.yaml ({len(yaml_proxies)} 节点)")

# 写入 v2ray 订阅
plain = [p["link"] for p in all_proxies if "link" in p]
with open("free/v2ray.txt", "w") as f:
    f.write("\n".join(plain))
print(f"  ✅ free/v2ray.txt ({len(plain)} 条)")

# 写入 Shadowrocket
with open("free/shadowrocket.txt", "w") as f:
    f.write("\n".join(plain))
print(f"  ✅ free/shadowrocket.txt")

# 状态报告
with open("free/STATUS.md", "w") as f:
    f.write(f"""# 📊 免费节点状态

> 自动更新 | {time.strftime('%Y-%m-%d %H:%M UTC')}

| 指标 | 值 |
|------|-----|
| 总节点数 | {len(all_proxies)} |
| 来源数 | {len(SOURCES)} |
| Clash 格式 | {len(yaml_proxies)} |
| 明文订阅 | {len(plain)} |
| 抽样存活 | {alive}/30 |
""")
print(f"  ✅ free/STATUS.md")
print(f"\n✅ 更新完成")
