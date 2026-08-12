# 协议对接指南（Protocol Integration Guide）

> **用途**：Phase 2 部署方案设计阶段的协议对接参考文档。
> **覆盖范围**：智体共合全产品线（小龙虾 AI 盒子 / 龙虾 U 盘 / 龙虾移动硬盘 / 灵虾平台）在客户现场与外部系统对接所需的 6 类核心协议。
> **使用方式**：方案设计时选定协议 → 按本文档对接步骤设计 → 实施时按 Checklist 执行 → 联调时按常见问题排查。
> **关联交付物**：部署方案书（deployment-plan-template.md）、部署清单（deployment-checklist.md）。
> **更新机制**：协议规格升级或厂商变更时同步更新本指南。

---

## 📑 协议速查表

| 协议 | 端口 | 适用场景 | 智体共合产品 | 优先级 | 章节 |
|------|------|---------|------------|--------|------|
| **RTSP** | 554 / 8554 | 实时视频流拉取 | 盒子/U盘/硬盘 ← 摄像头 | ★★★★★ | §1 |
| **ONVIF** | 80 / 8080 | 摄像头发现/控制/录像 | 盒子 ← 摄像头 / NVR | ★★★★ | §2 |
| **OPC UA** | 4840 | 工业设备数据交换 | 盒子 ← → MES / PLC / SCADA | ★★★★ | §3 |
| **Modbus TCP** | 502 | PLC / 工业仪表 | 盒子 ← PLC / 传感器 | ★★★ | §4 |
| **MQTT** | 1883 / 8883 | IoT 消息推送 | 盒子 ← → 推送服务器 / IoT 平台 | ★★★ | §5 |
| **HTTP API** | 80 / 443 | 业务系统对接 | 盒子 ← → ERP/CRM/QMS/推送 | ★★★★★ | §6 |

**章节使用建议**：
- 视频类项目：必读 RTSP + ONVIF（§1 + §2）
- 工业控制类项目：必读 OPC UA 或 Modbus TCP（§3 + §4）
- 推送/IoT 类项目：必读 MQTT + HTTP API（§5 + §6）
- 全栈集成项目：6 协议都需评估

---

# §1. RTSP（Real Time Streaming Protocol）

## 1.1 协议概述

### 1.1.1 是什么

RTSP（实时流传输协议）是 **RFC 2326** 定义的"网络视频流控制协议"——1998 年由 RealNetworks / Netscape / Columbia University 提出，用于**控制多媒体服务器（摄像头/NVR）提供的实时/录制媒体流**。RTSP 本身只负责"控制"（PLAY/PAUSE/TEARDOWN），实际视频数据通过 RTP/UDP 或 RTP/TCP 传输。

```text
┌────────┐                              ┌────────┐
│ 视频源 │ ──RTP (媒体流 554+1) ────────→ │ 播放器 │  ← 小龙虾AI盒子
│(摄像头)│                                │        │
└────────┘ ──RTSP (信令 554) ──────────→ └────────┘
           SDP 协商/PLAY/PAUSE 指令
```

**关键点**：
- RTSP = 控制信令（不传视频）
- RTP/RTCP = 实际视频包传输（UDP 默认 / TCP 可选）
- 配套 SDP（会话描述协议）描述流参数

### 1.1.2 标准体系

| 标准 | 年份 | 演进 |
|------|------|------|
| **RFC 2326** | 1998 | RTSP 1.0 原始标准 |
| **RFC 7826** | 2016 | RTSP 2.0（替换版） |
| **ONVIF Profile S/T** | 2011+ | 基于 RTSP + RTP |
| **RTP/RTCP** | RFC 3550 | 媒体流传输 |

> **现场部署说明**：当前绝大多数摄像头使用 RTSP 1.0，RTSP 2.0 实际部署率低。

### 1.1.3 常见厂商

| 厂商 | 默认 RTSP 端口 | 鉴权方式 | 特殊说明 |
|------|---------------|---------|----------|
| **海康威视** | 554 | Digest + Basic | 主码流 / 子码流分离 |
| **大华** | 554 | Basic + Digest | URL 携带 channel/subtype |
| **宇视** | 554 | Digest | unicast/multicast |
| **华为** | 554 | Basic | Livestream 路径 |
| **萤石（EZVIZ）** | 554 | Basic | h264/ch01/main 路径 |
| **Axis（安讯士）** | 554 | Basic | /axis-media/media.amp |
| **Dahua OEM** | 554 | Basic | 与大华相同 |
| **智体共合（自家）** | 8554 | Token | 反向推送（如数字人流） |

---

## 1.2 适用场景（智体共合产品线）

| 场景 | RTSP 用法 | 智体共合端 |
|------|---------|----------|
| **工业质检** | 拉取产线工业相机视频流 | 小龙虾 AI 盒子 Pro |
| **安全监测** | 拉取 4-8 路摄像头 | 小龙虾 AI 盒子 Pro |
| **货架空位** | 拉取货架顶部摄像头 | 小龙虾 AI 盒子 Lite |
| **AI 店长** | 拉取门口/货架/收银 3 路 | 小龙虾 AI 盒子 Lite |
| **数字人生产** | 接收数字人流（内推 / 外拉） | 龙虾 U 盘 / 移动硬盘 |
| **反向录像** | 接收外部推流（如无人机/执法仪） | 小龙虾盒子作为 RTSP Server |

---

## 1.3 对接步骤

### Step 1：网络与端口准备

```bash
# 1. 确认网络可达
ping {摄像头IP}

# 2. 确认 RTSP 端口开放
telnet {摄像头IP} 554

# 3. 防火墙/ACL 已配置允许 554/TCP
#    （仅 LAN 内一般无限制；公网谨慎开放）
```

### Step 2：获取摄像头 RTSP URL

通过摄像头 Web 后台 / 厂商工具 / ONVIF Device Manager 获取：
```
rtsp://{username}:{password}@{IP}:{port}/{path}
```

**主流厂商 RTSP URL 速查**：

| 厂商 | 主码流 | 子码流 | 备注 |
|------|--------|--------|------|
| 海康（老固件） | `/{channel}01` | `/{channel}02` | 例：`/Streaming/Channels/101`、`/102` |
| 海康（新固件） | `/Streaming/Channels/{n}01` | `/Streaming/Channels/{n}02` | n = 通道号 |
| 大华 | `/cam/realmonitor?channel=1&subtype=0` | `/cam/realmonitor?channel=1&subtype=1` | subtype 0=主、1=子 |
| 宇视 | `/unicast/c{n}/s0/live` | `/unicast/c{n}/s1/live` | s0=主、s1=子 |
| 华为 | `/Livestream/1/ch1` | `/Livestream/2/ch1` | |
| Axis | `/axis-media/media.amp?videocodec=h264` | 同上加 `&streamprofile=2` | |
| 萤石 | `/h264/ch01/main/av_stream` | `/h264/ch01/sub/av_stream` | |
| Onvif 通用 | `/onvif/1`（部分支持） | | |

### Step 3：测试 RTSP 流

```bash
# 方法1：ffplay（最简洁）
ffplay -rtsp_transport tcp "rtsp://admin:abcd1234@192.168.1.64:554/Streaming/Channels/101"

# 方法2：VLC（图形）
vlc rtsp://admin:abcd1234@192.168.1.64:554/Streaming/Channels/101

# 方法3：ffprobe（纯探测）
ffprobe -v quiet -print_format json -show_format -show_streams \
  "rtsp://admin:abcd1234@192.168.1.64:554/Streaming/Channels/101"

# 输出示例：
# { "streams": [{ "codec_name": "h264", "width": 1920, "height": 1080, "r_frame_rate": "25/1" }] }
```

### Step 4：在灵虾平台绑定

**Web 控制台**：`设备管理 → 添加设备 → 选择 RTSP 类型`

```yaml
# 灵虾平台 RTSP 摄像头配置（保存为部署档案）
device:
  name: CAM-01
  type: rtsp_camera
  vendor: hikvision
  url: rtsp://admin:abcd1234@192.168.1.64:554/Streaming/Channels/101
  url_sub: rtsp://admin:abcd1234@192.168.1.64:554/Streaming/Channels/102
  transport: tcp                   # 推荐 TCP（避免 UDP 丢包）
  buffer_size_ms: 100              # 缓冲 100ms 抗抖动
  decode_hw: auto                  # Pro 盒子优先用 GPU 解码
  decode_thread: 1                 # Lite / 单路建议 1
```

### Step 5：验证推流

```bash
# 在小盒子端拉流
curl -X POST http://{box-IP}:8080/api/v1/cameras \
  -H "Content-Type: application/json" \
  -d '{
    "name": "CAM-01",
    "rtsp_url": "rtsp://admin:abcd1234@192.168.1.64:554/Streaming/Channels/101",
    "sub_url": "rtsp://admin:abcd1234@192.168.1.64:554/Streaming/Channels/102",
    "fps": 25,
    "resolution": "1920x1080"
  }'

# 查看拉流状态
curl http://{box-IP}:8080/api/v1/cameras/CAM-01/status
# { "online": true, "fps": 25, "bitrate_kbps": 4128, "dropped_frames": 0 }
```

---

## 1.4 配置示例

### 1.4.1 主子码流策略（强烈推荐）

```yaml
# 用主子码流组合节省算力
# 主码流：录像用（高码率 高清晰）
# 子码流：AI 识别用（低码率 低分辨率 但算力省）
camera_streams:
  main:
    url: rtsp://.../Streaming/Channels/101    # 录像 + 偶尔抽查
    fps: 25
    resolution: 1920x1080
    bitrate_kbps: 4096
  sub:
    url: rtsp://.../Streaming/Channels/102    # AI 推理
    fps: 10
    resolution: 704x576
    bitrate_kbps: 512
ai_inference:
  source: sub                    # AI 读子码流
  interval_ms: 200               # 5 FPS 识别
```

### 1.4.2 反向 RTSP Server（小龙虾盒子作为服务端）

```yaml
# 应用场景：执法仪/无人机推流到盒子反向 RTSP
# 智体盒子提供 RTSP Server 接收外部流
rtsp_server:
  enabled: true
  listen_port: 8554
  auth: token                    # token 鉴权
  paths:
    - path: /live/uav-01
      token: {uuid-generated}
    - path: /live/bodycam-02
      token: {uuid-generated}
# 外部推流命令（gstreamer / ffmpeg）
# gst-launch-1.0 -v filesrc location=video.mp4 ! decodebin ! x264enc ! rtph264pay pt=96 ! udpsink host={box-ip} port=8554
```

### 1.4.3 FFMpeg 转封装/降分辨率（边缘优化）

```bash
# 把高分辨率主码流转封装为更低分辨率后给 AI
ffmpeg -i "rtsp://admin:pass@192.168.1.64:554/Streaming/Channels/101" \
  -c:v copy -an -f rtsp "rtsp://localhost:8554/ai/CAM-01"

# 强制 GPU 硬解码 + 缩放
ffmpeg -hwaccel cuda -i "rtsp://..." \
  -vf "scale=1280:720" -c:v h264_nvenc -preset p4 \
  -f rtsp "rtsp://localhost:8554/ai/CAM-01"
```

### 1.4.4 多协议兼容处理（解决 URL 解析问题）

```python
# Python 伪代码（智体盒子内 OpenClaw 内核处理 RTSP URL）
def normalize_rtsp_url(url: str, vendor: str) -> List[str]:
    """尝试多种 URL 变体以适配老固件摄像头"""
    if vendor == 'hikvision':
        return [
            url,                                     # 原始
            url.replace('/101', '/201'),             # 老固件主码流
            url.replace('/Streaming', '/h264'),      # 极老固件
            url.replace(':554', ':554/h264'),        # 备用路径
        ]
    elif vendor == 'dahua':
        return [
            url,
            url + '&subtype=0',
            url.replace('subtype=1', 'subtype=0'),
        ]
    return [url]
```

---

## 1.5 常见问题与解决

| 问题 | 现象 | 根因 | 解决方案 |
|------|------|------|---------|
| **RTSP 401 Unauthorized** | 拉流失败返回 401 | 用户名/密码错误 | 1. 重置密码 2. 改 URL 转义（@→%40） |
| **404 Not Found** | 找不到路径 | 厂商固件升级改路径 | 查厂商最新文档；用 ONVIF 自动发现 URL |
| **TCP/UDP 协商失败** | 长时间黑屏后报错 | 防火墙拦截 UDP | 改用 TCP 传输：`rtsp_transport=tcp` |
| **花屏/马赛克** | 视频偶发花屏 | 带宽不足 / 网络拥塞 / 帧率设置过高 | 降帧率到 15fps；改子码流；切独立 VLAN |
| **延迟过高（>5s）** | 实时画面延迟明显 | TCP 缓冲 + 解码缓冲过大 | 调小 `buffer_size_ms`（100ms 起步） |
| **无法拉流（无任何响应）** | curl 无返回 | 网络层不通 | 测 ping + telnet 554；检查 ACL |
| **断流频繁** | 视频流周期性断 | 摄像头供电不稳 / 网线接触不良 | 测电压 + 重压水晶头；用 PoE 时检查功率 |
| **H.265 拉不动** | CPU 占用高 | 软件解码未启用 | 启 N 卡硬解（Pro 盒子）；改用子码流 H.264 |
| **RTSP over HTTP 端口冲突** | 8554 端口被占 | 已有服务占用 | 换端口；用不同范围 8554-8560 |
| **多客户端拉同一摄像头掉帧** | 摄像头只支持 N 路并发 | 超过摄像头并发数 | 改用 NVR；用盒子做 RTSP 转发 |

---

## 1.6 参考资料

- **RFC 2326**（RTSP 1.0）：https://tools.ietf.org/html/rfc2326
- **RFC 7826**（RTSP 2.0）：https://tools.ietf.org/html/rfc7826
- **Live555 库**（FFmpeg RTSP 实现底层）：https://www.live555.com/
- **FFmpeg RTSP 文档**：https://trac.ffmpeg.org/wiki/StreamingGuide
- **GStreamer RTSP 教程**：https://gstreamer.freedesktop.org/documentation/gst-rtsp-server/
- **海康威视 RTSP 开发文档**：https://www.hikvision.com/cn/download-detail-view_5001.html
- **ONVIF Profile S**：https://www.onvif.org/profiles/profile-s/

---

# §2. ONVIF（Open Network Video Interface Forum）

## 2.1 协议概述

### 2.1.1 是什么

ONVIF（开放网络视频接口论坛）成立于 **2008 年**，由安讯士（Axis）、博世（Bosch）、海康（HiKvision）共同发起，旨在为基于 IP 的物理安防产品（IP 摄像头 / NVR / 视频管理平台）提供**标准化接口**。ONVIF 通过 **Web Services**（SOAP/XML）实现设备发现、设备管理、媒体流、PTZ 控制、事件订阅等能力。

```text
ONVIF 体系结构：
┌──────────────────────────────────────────┐
│             客户端（智体盒子）               │
├──────────────────────────────────────────┤
│  Discovery (WS-Discovery) ←──→ 设备发现    │
│  Device Management (WS) ←──→ 设备属性管理   │
│  Media (WS)        ←──→ 媒体配置 + RTSP    │
│  Imaging (WS)       ←──→ 图像参数 + PTZ    │
│  Events (WS)        ←──→ 事件订阅 / 推送    │
│  Recording (WS)    ←──→ 录像控制 / 回放    │
│  Analytics (WS)    ←──→ 智能分析（VCA）    │
└──────────────────────────────────────────┘
                ↓ SOAP / HTTP / RTSP / RTP
┌──────────────────────────────────────────┐
│  摄像头 / NVR / 视频平台（ONVIF 设备）      │
└──────────────────────────────────────────┘
```

### 2.1.2 ONVIF Profile（兼容等级）

| Profile | 发布年 | 适用设备 | 核心能力 |
|---------|--------|---------|---------|
| **Profile S** | 2011 | 摄像头 / NVR | 实时流 + 录像回放 |
| **Profile G** | 2014 | NVR / VMS | 录像控制 + 存储管理 |
| **Profile C** | 2013 | 门禁控制 | 门禁事件 |
| **Profile A** | 2014 | 报警 / 访问控制 | 报警配置 |
| **Profile T** | 2018 | 高级流（云台/视频）| H.265 + 高级特性 |
| **Profile M** | 2019 | 元数据 / 分析 | 智能分析数据流 |
| **Profile D** | 2020 | 门禁查询 / 凭据 |  |

> **现场部署建议**：2018 年后的摄像头应选 **Profile T** 兼容；老摄像头多为 Profile S；现代 AI 摄像头多半带 Profile M（智能元数据）。

### 2.1.3 常见厂商（大多支持 ONVIF）

| 厂商 | ONVIF Profile | 默认端口 | 备选方案 |
|------|---------------|---------|----------|
| 海康威视 | S/T/M | 80 (HTTP) / 554 (RTSP) | 启用 ONVIF：网络 → 高级 → ONVIF |
| 大华 | S/T | 80 | 启用 ONVIF |
| 安讯士（Axis） | S/T | 80 | 原生支持 |
| 博世（Bosch） | S/T | 80 | 需 enable ONVIF |
| 华为 | S/T | 80 | 多 Profile |
| 索尼 | S | 80 | 较老固件兼容 |

> **注意**：部分厂商 **默认不开启 ONVIF**，需手动启用（摄像头的 Web 后台 → 网络 → ONVIF）。

---

## 2.2 适用场景

| 场景 | ONVIF 用法 |
|------|-----------|
| **批量摄像头发现** | FDE 现场一次发现所有 ONVIF 摄像头，批量导入盒子（无需逐个查 IP） |
| **跨厂商统一接入** | 海康/大华/华为混用时统一协议接入 |
| **PTZ 控制** | 智能盒子根据 AI 识别自动控制云台（球机）跟踪可疑目标 |
| **事件订阅** | 摄像头端触发事件（移动侦测 / 视频遮挡）推送给盒子 |
| **录像集中管理** | 盒子对接 NVR Profile G，统一检索录像 |
| **VMS 平台对接** | 智体盒子作为 ONVIF Client 对接客户既有 VMS |
| **数字人反向流** | 智体盒子作为 ONVIF Profile S Server，对外提供 RTSP 流 |

---

## 2.3 对接步骤

### Step 1：确认摄像头支持 ONVIF

```bash
# 方法1：Web 后台查 Firmware Spec（支持 ONVIF 哪几个 Profile）
# 方法2：WS-Discovery 探测（UDP 多播 239.255.255.250 端口 3702）
# 方法3：ONVIF Device Manager（推荐图形工具）
#   下载：http://tekniskaonsult.se/onvif/
#   自动发现网内 ONVIF 设备
```

### Step 2：启用摄像头 ONVIF 服务

在摄像头 Web 后台：
```
网络 → 高级配置 → 集成协议 → ONVIF
- [✓] 启用 ONVIF
- 用户名：admin / 同管理 / ONVIF 专用
- 密码：{ONVIF-PASS}
- 端口：80 (HTTP) / 443 (HTTPS)
```

### Step 3：用 ONVIF Device Manager 测试

```text
1. 打开 ONVIF Device Manager（Windows / Linux）
2. 软件自动扫描网内 ONVIF 设备
3. 双击设备 → 输入用户名密码 → 连接
4. 检查：
   - Device Information（厂商/型号/固件）
   - Video Stream（主码流 RTSP URL）
   - Profile 列表（S/T/G/M/C/A）
   - PTZ 控制（如球机）
   - Snapshot（抓拍测试）
```

### Step 4：在智体盒子绑定 ONVIF

**两种方式**：

```yaml
# 方式A：通过 ONVIF 自动发现（推荐，批量导入）
lingxia_platform:
  path: 设备管理 → 添加设备 → ONVIF 自动发现
  options:
    discovery_timeout_ms: 5000
    auto_import: true
    auth_required: true
    username: admin
    password: {摄像头ONVIF密码}
    profile_filter: ["S", "T"]       # 限定 Profile
    discovered_devices:
      - ip: 192.168.1.64
        vendor: Hikvision
        model: DS-2CD3T47
        firmware: V5.7.10
        main_stream: rtsp://...
        sub_stream: rtsp://...
        ptz: false                   # 球机才是 true
        analytics_support: true      # Profile M
        action: 已添加

# 方式B：手动指定 ONVIF 端点
device:
  name: CAM-01
  type: onvif_camera
  onvif_endpoint: http://admin:{pass}@192.168.1.64:80/onvif/device_service
  media_service: http://admin:{pass}@192.168.1.64:80/onvif/media_service
  ptz_service: http://admin:{pass}@192.168.1.64:80/onvif/ptz_service
  profile: S                        # 主 Profile
  media_profile:
    name: mainStream                 # 摄像头侧 Profile 名
    video_source_config:
      token: VideoSourceConfig001
      use_count: 1
    video_encoder_config:
      token: VideoEncoderConfig001
      encoding: H264
      resolution: 1920x1080
      fps: 25
      bitrate: 4096
```

### Step 5：事件订阅（高级）

```python
# ONVIF PullPoint 事件订阅（Python 伪代码）
import onvif

camera = onvif.ONVIFCamera(
    host='192.168.1.64',
    port=80,
    user='admin',
    passwd='{pass}'
)

# 创建 PullPoint 订阅
events_service = camera.create_events_service()
pull_point = events_service.CreatePullPointSubscription(
    Filter={'MessageContentFilter': {}},
    InitialTerminationTime='PT1H'    # 1 小时续订
)

# 循环拉取事件
while True:
    notifications = pull_point.PullMessages(
        Timeout='PT5S',              # 5 秒超时
        MessageLimit=10
    )
    for msg in notifications:
        topic = msg.Topic
        # 处理事件：MotionDetected / VideoLoss / TamperDetected / ...
        if 'MotionDetected' in topic:
            print("移动侦测触发")
        elif 'TamperDetected' in topic:
            print("视频遮挡触发")
```

---

## 2.4 配置示例

### 2.4.1 PTZ 自动跟踪（球机 + AI 触发）

```yaml
# 应用场景：安全监测 Skill 检测到闯入 → 球机自动跟拍
onvif_ptz:
  enabled: true
  camera: CAM-PTZ-01                  # 球机
  trigger_skill: safety-monitoring
  trigger_event: intrusion_detection
  ptz_actions:
    on_alarm:
      service: ptz
      action: AbsoluteMove
      pan_position: ${target_x}        # 计算目标在画面位置
      tilt_position: ${target_y}
      zoom_position: 0.3               # 拉近
      speed_pan: 0.5
      speed_tilt: 0.5
      timeout_ms: 30000                # 跟踪 30 秒
    on_idle:
      service: ptz
      action: ContinuousMove
      pan_velocity: -0.1
      tilt_velocity: 0.0
      timeout_ms: 5000                 # 慢速扫描 5 秒
      action_after: stop
    preset_positions:                  # 预置位
      - name: entrance
        pan: 0.5
        tilt: 0.0
        zoom: 0.2
      - name: east_corner
        pan: 0.3
        tilt: 0.4
        zoom: 0.5
      - name: west_corner
        pan: 0.7
        tilt: 0.4
        zoom: 0.5
```

### 2.4.2 ONVIF 元数据推送（Profile M，对接 AI 摄像头自带算法）

```yaml
# 应用场景：摄像头侧已经做了 AI 检测（如某品牌摄像头自带安全帽识别）
# 智体盒子只接收元数据事件，统一告警推送
onvif_metadata:
  enabled: true
  source: camera_built_in_ai
  metadata_stream:
    rtsp_url: rtsp://.../Streaming/Channels/103   # 元数据子码流
    rtp_metadata: true
    schema: {"events": ["helmet_off", "intrusion"]}
  parsed_events:
    helmet_off:
      rule:
        class_id: ["person_no_helmet"]
        min_duration_s: 5
      action: send_wechat_alert
    intrusion:
      rule:
        class_id: ["person_in_zone"]
        min_confidence: 0.85
      action: send_wechat_alert + sound_alarm
```

### 2.4.3 多厂商混用场景（最常见）

```yaml
# 现场多品牌摄像头共存
onvif_discovery:
  vendors:
    - hikvision
    - dahua
    - axis
    - uniview
    - huawei
  auto_add_to_lingxia: true
  auth_strategy:
    default_user: admin
    default_password: ${camera_pass}        # 统一预设
  fallback_rtsp_url: true                   # ONVIF 失败时回退到 RTSP
  per_vendor_test:
    hikvision:
      onvif_test: usually_pass              # 几乎没问题
      known_issue: "老固件需 XML escape"
      workaround: ONVIF 升级到 V5.5+
    dahua:
      onvif_test: usually_pass
      known_issue: "PTZ 协议需用 Dahua 私有扩展"
      workaround: 切换到 Profile T
    axis:
      onvif_test: always_pass
      known_issue: 无
```

### 2.4.4 ONVIF Server（智体盒子作为服务端，对外推流）

```yaml
# 应用场景：客户既有 VMS（如 Milestone/Genetec/HikCentral）需要接入智体盒子 AI 分析结果
onvif_server:
  enabled: true
  listen_ip: 0.0.0.0
  http_port: 8000
  rtsp_port: 8554
  device_info:
    manufacturer: "Zhiti Federation"
    model: "Crayfish-AI-Box-Pro"
    firmware_version: "v1.0.0"
    serial_number: "{SN}"
    hardware_id: "ZHITIBOX-AI-PRO"
  profiles:
    - name: main_stream
      token: ProfileToken1
      video_source_token: VideoSrcToken1
      video_encoder_token: VideoEncToken1
      encoding: H264
      width: 1920
      height: 1080
      fps: 25
      bitrate_kbps: 4096
  capabilities:
    - media
    - events
    - ptz                         # 若支持云台
    - analytics                   # VCA 元数据
  event_topics:
    - tns1:VideoSource/MotionAlarm
    - tns1:RuleEngine/IntrusionDetected
    - tns1:RuleEngine/HelmetOffDetected
```

---

## 2.5 常见问题与解决

| 问题 | 现象 | 根因 | 解决方案 |
|------|------|------|---------|
| **ONVIF Device Manager 找不到设备** | 扫描不到任何设备 | 1. ONVIF 未启用 2. VLAN 隔离 3. 防火墙 | 启用 ONVIF；改同 VLAN；关闭电脑防火墙 |
| **连接 401** | 输入密码后被拒 | 1. ONVIF 用户未设置 2. 密码错 3. 第三方固件 | 在摄像头加 ONVIF 用户；用 HTTP Basic vs Digest 测试 |
| **找不到 Video Stream URL** | 可连接但 RTSP 为空 | 老固件 / 非标实现 | 改用厂商私有 RTSP URL；升级固件 |
| **PTZ 控制无响应** | 命令成功但镜头不动 | 1. 未启用 PTZ 服务 2. 协议不匹配 3. 阻塞 | 启用 PTZ；切换 ONVIF Profile；复位云台 |
| **断连重连频繁** | 设备频繁掉线 | 1. Keep-Alive 心跳超时 2. 网络抖动 | 缩短心跳间隔（30s）；改独立 VLAN |
| **认证失败（Token expired）** | WS-Security 错误 | 客户端时钟不对 | 同步 NTP；切到 HTTP Basic（允许明文） |
| **录像回放找不到** | Profile G 功能失败 | NVR 不支持 Profile G | 检查 NVR Profile；试用本地直拉 |
| **元数据事件解析失败** | Profile M 事件乱码 | 不同厂商实现差异 | 用厂商 SDK；联系智体技术支持 |
| **HTTPS 证书无效** | 启 HTTPS 后失败 | 默认证书无效 | 改回 HTTP；或安装可信证书 |
| **PTZ 移动慢/卡顿** | 跟踪移动物体延迟 | 速度过快/边界限制 | 调小 speed_pan；增加缓冲 |

---

## 2.6 参考资料

- **ONVIF 官方文档**：https://www.onvif.org/specifications/
- **ONVIF Device Test Tool**：https://www.onvif.org/tools/
- **ONVIF 客户端开发（C++）**：https://github.com/onvif/onvif
- **ONVIF Python 客户端**：https://github.com/FalkTannroth/onvif-python
- **ONVIF Compliance Tool**：测试摄像头的 ONVIF 符合度
- **GSoap ONVIF 实现**：https://www.genivia.com/dev.html

---

# §3. OPC UA（OPC Unified Architecture）

## 3.1 协议概述

### 3.1.1 是什么

OPC UA（OPC Unified Architecture）由 OPC Foundation 于 2008 年推出，是 **工业 M2M（机器对机器）通信的统一架构**。OPC UA = 信息建模框架 + 通信协议 + 安全机制。目标是替代传统 OPC DA（基于 Windows COM/DCOM），实现**跨平台、跨厂商、面向服务**的工业数据交换。

```text
OPC UA 协议栈：

┌────────────────────────────────────────┐
│        Information Model (信息模型)       │  ← 业务语义
├────────────────────────────────────────┤
│        Services (服务调用 API)            │  ← Read/Write/Subscribe/Call
├────────────────────────────────────────┤
│        Security (加密 + 鉴权 + 审计)        │
├────────────────────────────────────────┤
│        Transport (TCP/HTTP/WebSocket)     │
└────────────────────────────────────────┘
          ↓ 编码格式 (Binary / XML / JSON)
```

**关键特性**：
- **信息建模**：地址空间（AddressSpace）模型，节点（Node）含数据/方法/事件
- **通信协议**：TCP 二进制（默认）/ HTTP 文本（调试）/ WebSocket
- **安全**：端到端加密 + 签名 + 审计 + 鉴权（支持证书、用户名/密码、匿名）
- **跨平台**：独立于 OS，独立于厂商

### 3.1.2 标准版本

- **OPC UA 1.00**：2010 年发布
- **OPC UA 1.04 / 1.05**：当前主流（推荐 1.04）
- **OPC UA Pub/Sub**：2018+（Kafka/MQTT 上扩展）
- **OPC UA over TSN**：实时以太网（与 5G/工业互联网结合）

### 3.1.3 常见厂商

| 厂商 | 产品 | OPC UA 支持 |
|------|------|------------|
| **西门子（Siemens）** | SIMATIC S7-1500 | 原生 UA Server（端口 4840）|
| **施耐德（Schneider）** | M580/M340 | UA Server + 需授权激活 |
| **罗克韦尔（Rockwell） | ControlLogix | UA Server 需 V30+ 固件 |
| **三菱（Mitsubishi）** | MELSEC iQ-R | OPC UA 模块选配 |
| **欧姆龙（Omron）** | NX/NJ 系列 | NX-OPC-UA 模块 |
| **倍福（Beckhoff）** | TwinCAT | 集成 UA Server |
| **汇川（Inovance）** | H5U/AM600 | UA Server |
| **国产工业互联网平台** | 阿里/华为/树根 | OPC UA Gateway |

---

## 3.2 适用场景

| 场景 | OPC UA 用法 |
|------|-----------|
| **工业质检** | 盒子读取 PLC 检测工位信号 → 写入 QC 结果到 MES |
| **安全监测** | 盒子触发 → PLC 自动停线 |
| **设备数据采集** | 盒子订阅 PLC/传感器实时数据，AI 分析异常 |
| **数字孪生** | 盒子 → 数字孪生平台（双向） |
| **与 MES/ERP 对接** | 标准化交换，避免协议适配重复开发 |
| **OPC UA 网关** | 盒子作为 OPC UA Gateway（Modbus → OPC UA） |
| **信创场景** | 与麒麟/统信/UOS 国产化操作系统适配 |

---

## 3.3 对接步骤

### Step 1：前置条件确认

- [ ] PLC/工控机已启用 OPC UA Server
- [ ] 网络可达，端口 4840 TCP 开放
- [ ] 安全策略已与 IT/OT 对齐（防火墙单向/双向）
- [ ] 凭据（证书/用户名密码）已获取
- [ ] 数据点列表已与 MES 工程师对齐

### Step 2：测试连通性

```bash
# 端口检查
telnet {PLC-IP} 4840        # 应返回 Accepted

# 用 OPC UA 客户端验证（推荐工具）
# - Prosys OPC UA Browser（图形 / 免费）
# - UA Expert（最常用，跨平台）
# - Node-RED OPC UA Client
# - Python opcua 库（pip install opcua）

python3 -c "
from opcua import Client
client = Client('opc.tcp://192.168.1.100:4840')
client.set_security_string('Basic256,Sign,None')
client.set_user_certificate('cert.pem', 'key.pem')  # 可选
client.set_username_password('agi-agent', 'xxx')
client.connect()
print('Browse:')
root = client.get_root_node()
for child in root.get_children():
    print(f'  {child}')
client.disconnect()
"
```

### Step 3：配置 OPC UA Client（智体盒子）

```yaml
# 智体盒子 OPC UA 客户端配置
opcua_clients:
  - client_id: mes-main
    endpoint_url: opc.tcp://192.168.1.100:4840
    security_policy: None              # 测试阶段；生产建议 Basic256
    auth_method: username_password
    username: agi-agent
    password: {保密}
    namespace_uris:
      - http://customer-qc/v1
      - urn:festo/specific
    session_timeout_ms: 30000         # 30 秒
    reconnect:
      enabled: true
      backoff_ms: [1000, 5000, 30000]
      max_attempts: 10
    subscriptions:                     # 订阅（盒子 → MES）
      - subscription_id: status
        publishing_interval_ms: 100
        monitored_items:
          - node_id: ns=1;s=Line1.Status
            attribute: Value
            sampling_interval_ms: 100
            queue_size: 10
            data_change_filter:
              trigger: StatusValue    # 值变化或状态变化
      - subscription_id: production_count
        publishing_interval_ms: 1000
        monitored_items:
          - node_id: ns=1;s=Line1.OK_Count
          - node_id: ns=1;s=Line1.NG_Count
          - node_id: ns=1;s=Line1.Speed
    publishes:                        # 发布（MES → 盒子写）
      - node_id: ns=1;s=Agent.DetectResult
        write_delay_ms: 100
        data_type: string
      - node_id: ns=1;s=Agent.Alarm
        data_type: boolean
      - node_id: ns=1;s=Agent.StopLine
        data_type: boolean
```

### Step 4：测试双向通信

```python
# 盒子侧 OPC UA 伪代码
from opcua import Client

async def main():
    client = Client('opc.tcp://192.168.1.100:4840')
    client.set_username_password('agi-agent', 'secret')
    await client.connect()
    
    # 1. 订阅 PLC 节点变化
    sub = await client.create_subscription(100, handler)
    sub.subscribe_data_change([
        client.get_node('ns=1;s=Line1.Status'),
        client.get_node('ns=1;s=Line1.OK_Count')
    ])
    
    # 2. 写入 QC 结果
    node = client.get_node('ns=1;s=Agent.DetectResult')
    node.write_value('PASS')        # 或 'NG_划痕'
    
    # 3. 读取 PLC 状态
    status_node = client.get_node('ns=1;s=Line1.Status')
    status = await status_node.read_value()
    print(f'PLC 当前状态：{status}')
    
    # 4. 调用 Method（高级）
    method = client.get_node('ns=1;s=Line1.Stop')
    method.call([])
    
    await client.disconnect()

# 事件回调（异步）
async def handler(node, val, data):
    if node == 'ns=1;s=Line1.Status' and val == 0:
        print("产线停机，立即调用 AI 检测")
```

### Step 5：在灵虾平台绑定

```yaml
# 灵虾平台 → 协议管理 → 添加 OPC UA
lingxia_protocols:
  - protocol: opcua
    name: 客户QC系统
    endpoint: opc.tcp://192.168.1.100:4840
    credentials:
      type: username_password
      username: agi-agent
      password_ref: vault:mes-pass
    skills_bind: [industrial-qc]
    data_mapping:
      - agent_node: alarm_level
        opcua_node: ns=1;s=Agent.Alarm
        direction: read
      - agent_node: detect_result
        opcua_node: ns=1;s=Agent.DetectResult
        direction: write
      - agent_node: stop_line
        opcua_node: ns=1;s=Agent.StopLine
        direction: write
    data_history: true                # 历史记录到时序库
    metric_export:
      prometheus: true
      labels: ["line", "result"]
```

---

## 3.4 配置示例

### 3.4.1 工业 QC 数据交互（端到端）

```text
场景：A 公司智能制造产线
- PLC（西门子 S7-1500）控制产线启停
- MES 跟踪每个工件的检测结果
- 小龙虾 AI 盒子 Pro 做视觉检测

数据流：

PLC          小龙虾盒子           MES
 │              │                 │
 │─── 生产节拍 →│                 │
 │              │ ←── 抓拍信号 ────│ (软触发或硬触发)
 │              │ ── QC 结果 ──────→│ (PASS / NG: 划痕)
 │              │ ── 报警状态 ─────→│
 │              │ ←── 设备状态 ─────│
 │              │ ── 停线控制 ─────→│
 │              │ ←── 启停指令 ─────│
```

### 3.4.2 安全证书配置（生产环境推荐）

```bash
# 1. 生成客户端证书
openssl req -new -x509 -days 3650 -nodes \
  -out client_cert.pem -keyout client_key.pem \
  -subj "/CN=Zhiti-AI-Box-SN12345678"

# 2. 客户端证书导入到 OPC UA Server
# 方式 A：上传到 Server 的 Trusted 目录
# 方式 B：通过 Server 配置工具注册

# 3. 客户端配置
```

```yaml
opcua_client:
  endpoint: opc.tcp://192.168.1.100:4840
  security:
    policy: Basic256Sha256
    mode: SignAndEncrypt
    certificate: client_cert.pem
    private_key: client_key.pem
    server_certificate_trust: server_cert.der
    application_uri: urn:zhiti:ai-box:SN12345678
```

### 3.4.3 网关模式（盒子作为 OPC UA Gateway）

```yaml
# 应用场景：现场是 Modbus TCP 设备，盒子提供 OPC UA Server 接入 MES
opcua_gateway:
  mode: server
  listen_port: 4840
  endpoint: opc.tcp://0.0.0.0:4840
  security_policy: None
  northbound_devices:                # 上游（北向：盒子 → MES）
    - type: opcua_server              # 自身作为 Server
      name: Agi-AI-Box-GW
  southbound_devices:                # 下游（南向：盒子 ← 设备）
    - device_id: PLC-01
      protocol: modbus_tcp
      ip: 192.168.1.50
      port: 502
      unit_id: 1
      register_mapping:
        - node_id: ns=2;s=PLC.Temperature
          address: 40001
          type: int16
          scan_interval_ms: 1000
        - node_id: ns=2;s=PLC.Pressure
          address: 40002
          type: float
          scan_interval_ms: 1000
        - node_id: ns=2;s=PLC.Speed
          address: 40010
          type: uint16
          scan_interval_ms: 100
```

### 3.4.4 OPC UA Pub/Sub（高级，Kafka/MQTT）

```yaml
# 应用场景：大规模设备实时数据分发（数百台设备）
opcua_pubsub:
  enabled: true
  transport: mqtt                      # or kafka
  mqtt:
    broker: mqtt://broker.local:1883
    topic_prefix: opcua/agi-box/
  published_messages:
    - dataset: qc-results
      metadata: { line: "L1", station: "S1" }
      fields:
        - name: detect_result
          type: string
        - name: confidence
          type: double
        - name: timestamp
          type: datetime
      publishing_interval_ms: 1000
```

---

## 3.5 常见问题与解决

| 问题 | 现象 | 根因 | 解决方案 |
|------|------|------|---------|
| **BadSecurityChecksFailed** | 客户端证书 / 密钥不匹配 | 安全策略 / 证书格式错 | 重新生成证书；检查 trust 列表 |
| **BadCommunicationError** | 连接后立即断开 | 1. 防火墙 2. License 3. Server 资源 | 测 telnet 4840；查 PLC 资源 |
| **BadNodeIdUnknown** | 找不到节点 | 1. namespace 错 2. ID 错 3. 服务器没暴露 | 用 Prosys/UA Expert Browse 确认正确路径 |
| **BadOutOfService** | 节点读写失败 | 该节点当前不可用 | 等服务恢复；查 PLC 该节点有没有电源 |
| **BadTimeout** | 调用 Method 超时 | Server 处理慢 | 增加 timeout 到 30s+；用异步调用 |
| **BadUserAccessDenied** | 鉴权失败 | 用户无权限 | 检查 read/write 权限分配 |
| **数据刷新慢** | 订阅延迟 > 1s | publishingInterval 设置过大 | 调小到 100-500ms |
| **断线后不重连** | 客户端永久离线 | reconnect 策略未启用 | 启用重连；指数退避 |
| **中文乱码** | 字符串节点读出来乱码 | 编码不一致 | 设置客户端 UTF-8；明确编码 |
| **OPC UA 找不到模块** | PLC 兼容问题 | 固件版本老 | 升级固件或加 OPC UA 模块 |

---

## 3.6 参考资料

- **OPC UA 官方文档**：https://opcfoundation.org/developer-tools/specifications-unified-architecture/
- **Prosys OPC UA SDK**：https://www.prosysopc.com/products/
- **Eclipse Milo（开源 OPC UA Server/Client）**：https://github.com/eclipse/milo
- **python-opcua**：https://github.com/FreeOpcUa/python-opcua
- **Node-RED OPC UA**：https://flows.nodered.org/node/node-red-contrib-opcua
- **西门子 OPC UA 编程手册**：SIMATIC S7-1500 OPC UA 文档
- **智体共合 OPC UA 适配指南**（内部 kb: XrneKkrCkkdLgfe-lti6VAiwoipSAe7CsltatLHrAAs= → 搜"OPC UA"）

---

# §4. Modbus TCP（Modbus Protocol over TCP）

## 4.1 协议概述

### 4.1.1 是什么

Modbus 由 **Modicon（现施耐德电气）** 于 **1979 年**发布，是 **工业自动化领域最古老、应用最广泛**的通信协议。原本运行在串行（RS-232/RS-485）上，1999 年扩展到 TCP/IP（Modbus TCP），2007 年加 Modbus over TCP 安全机制。

```text
Modbus TCP 帧结构：
┌──────────────┬─────────────────┬─────────────────┬─────────┬─────────┐
│ MBAP Header  │   Function Code │   Data          │  Error   │  CRC    │
│  (7 bytes)   │   (1 byte)      │  (N bytes)      │  (Opt.)  │ (Opt.)  │
└──────────────┴─────────────────┴─────────────────┴─────────┴─────────┘

MBAP Header:
- Transaction ID (2 bytes)
- Protocol ID (2 bytes, 固定 0x0000)
- Length (2 bytes)
- Unit ID (1 byte)
```

**关键点**：
- 客户端/服务器模型（Client 主动请求，Server 响应）
- 4 类寄存器（Coil / Discrete Input / Holding Register / Input Register）
- 端口 502 / TCP
- 无内置认证（生产建议放在 VPN/网闸后面）

### 4.1.2 寄存器分类

| 类型 | 名称 | 读写 | 用途 | 访问范围 |
|------|------|------|------|----------|
| **Coils** | 线圈 | RW | 数字输出（如启停、继电器）| 0xxxx |
| **Discrete Inputs** | 离散输入 | RO | 数字输入（如按钮、限位）| 1xxxx |
| **Holding Registers** | 保持寄存器 | RW | 模拟输出（如设定值）| 4xxxx |
| **Input Registers** | 输入寄存器 | RO | 模拟输入（如温度、压力）| 3xxxx |

### 4.1.3 常见功能码

| 功能码 | 名称 | 用途 |
|--------|------|------|
| **01** | Read Coils | 读线圈 |
| **02** | Read Discrete Inputs | 读离散输入 |
| **03** | Read Holding Registers | 读保持寄存器 |
| **04** | Read Input Registers | 读输入寄存器 |
| **05** | Write Single Coil | 写单线圈 |
| **06** | Write Single Register | 写单寄存器 |
| **15 (0F)** | Write Multiple Coils | 写多线圈 |
| **16 (10)** | Write Multiple Registers | 写多寄存器 |
| **23 (17)** | Read/Write Multiple Registers | 读写多寄存器 |

### 4.1.4 常见厂商

| 厂商 | Modbus TCP 支持 |
|------|-----------------|
| **西门子（Siemens）** | S7-1200/1500 通过 CM/CP 模块支持 |
| **施耐德（Schneider）** | M340/M580 原生支持 |
| **三菱（Mitsubishi）** | MELSEC-Q/FX5 原生或模块 |
| **欧姆龙（Omron）** | CP1H/NX 原生 |
| **罗克韦尔（Allen-Bradley）** | MicroLogix/ControlLogix 部分支持 |
| **国产 PLC** | 汇川/信捷/合信/禾川 普遍原生支持 |
| **电表/传感器** | Schneider/ABB/Siemens 多功能电表 |

---

## 4.2 适用场景

| 场景 | Modbus TCP 用法 |
|------|----------------|
| **PLC 集成** | 盒子读 PLC 寄存器（温度/速度/计数）|
| **传感器接入** | 盒子读电表/温湿度/压力表 |
| **设备控制** | 盒子写 PLC 控制字（启停/速度）|
| **QMS 数据采集** | 盒子定期 read QMS 寄存器 |
| **OPC UA 网关** | 盒子做 Modbus TCP → OPC UA 转换 |
| **OPC UA 双栈兼容** | 老 PLC 不支持 OPC UA，Modbus 是兜底方案 |

---

## 4.3 对接步骤

### Step 1：确认 Modbus 设备参数

```yaml
modbus_device:
  ip: 192.168.1.50
  port: 502
  unit_id: 1                          # 站号
  protocol: tcp
  timeout_ms: 3000
  byte_order: big_endian              # CDAB / ABCD 看设备
  word_order: big_endian
```

### Step 2：测试连接

```bash
# 方法1：MBPoll（命令行工具）
mbpoll -m tcp -a 1 -t 4 -r 1 -c 5 192.168.1.50
# -m tcp = TCP 模式
# -a 1 = 站号 1
# -t 4 = Input Register
# -r 1 = 起始寄存器 40001
# -c 5 = 读 5 个

# 方法2：libmodbus + Python
python3 -c "
from pymodbus.client import ModbusTcpClient
client = ModbusTcpClient('192.168.1.50', port=502)
result = client.read_holding_registers(0, 10, slave=1)
print(f'Values: {result.registers}')
client.close()
"
```

### Step 3：映射到智体盒子

```yaml
# 智体盒子 Modbus Client 配置
modbus_clients:
  - client_id: plc-line1
    host: 192.168.1.50
    port: 502
    unit_id: 1
    timeout_ms: 3000
    reconnect:
      enabled: true
      interval_ms: 5000
    byte_order: big_endian
    polling:
      - registers:
          type: holding                   # 03 Holding Register
          start: 0
          count: 10
          interval_ms: 1000
          tag_map:
            - register: 0
              name: production_count
              data_type: uint16
              unit: 件
            - register: 1
              name: defect_count
              data_type: uint16
              unit: 件
            - register: 2
              name: line_speed
              data_type: uint16
              unit: m/min
              scale_factor: 0.1           # 原始值 × 0.1 = 真实值
            - register: 3
              name: temperature
              data_type: int16
              unit: ℃
              offset: -50                # 原始值 -50 = 真实值
      - registers:
          type: input                    # 04 Input Register
          start: 0
          count: 5
          interval_ms: 5000
          tag_map:
            - register: 0
              name: motor_current
              data_type: uint16
              unit: A
              scale_factor: 0.01
      - coils:
          type: coil                     # 01 Coils
          start: 0
          count: 8
          interval_ms: 1000
          tag_map:
            - coil: 0
              name: line_running
            - coil: 1
              name: alarm_active
            - coil: 2
              name: emergency_stop
    writes:                              # 写入控制
      enable_writes: true
      trigger_skill: industrial-qc       # 哪些 Skill 可以写
      register_map:
        - register: 100
          name: detect_result
          data_type: uint16
          value_map:
            0: PASS
            1: NG_SCRATCH
            2: NG_DENT
            3: NG_CONTAMINATION
        - register: 101
          name: stop_line
          data_type: uint16
          write_value: 1                 # 写 1 触发停线
        - register: 102
          name: reset_alarm
          data_type: uint16
          write_value: 1
```

### Step 4：双向通信测试

```python
# 测试脚本（在盒子上跑）
from pymodbus.client import ModbusTcpClient

client = ModbusTcpClient('192.168.1.50', port=502)

# 1. 读
result = client.read_holding_registers(0, 10, slave=1)
print(f"生产计数：{result.registers[0]}")
print(f"次品计数：{result.registers[1]}")
print(f"线速：{result.registers[2] * 0.1} m/min")

# 2. 写 QC 结果
client.write_register(100, 1, slave=1)         # 写入 NG_SCRATCH

# 3. 写停线指令
client.write_register(101, 1, slave=1)         # 触发停线

# 4. 触发紧急按钮（Coil 写）
client.write_coil(7, True, slave=1)            # 紧急停线

client.close()
```

---

## 4.4 配置示例

### 4.4.1 多 PLC 实时采集

```yaml
# 应用场景：工厂 5 条产线，每条配 PLC
modbus_clients:
  - {host: 192.168.1.50, unit_id: 1, name: "Line1-PLC"}
  - {host: 192.168.1.51, unit_id: 1, name: "Line2-PLC"}
  - {host: 192.168.1.52, unit_id: 1, name: "Line3-PLC"}
  - {host: 192.168.1.53, unit_id: 1, name: "Line4-PLC"}
  - {host: 192.168.1.54, unit_id: 1, name: "Line5-PLC"}
polling:
  parallel: true                          # 并行读
  fail_fast: false                        # 单线失败不影响其他
  timeout_per_device_ms: 3000
data_aggregation:
  interval_ms: 5000
  to_ai_skill: industrial-qc
  to_mes: yes                             # 同时转发到 MES（OPC UA 桥）
```

### 4.4.2 反向控制（盒子 → PLC 写入）

```yaml
# 应用场景：AI 识别 NG → 立即通过 Modbus 写 PLC 寄存器 101 = 1 → 停线
ai_to_plc_writes:
  - trigger:
      skill: industrial-qc
      event: defect_detected
      confidence: >= 0.90
      classes: [scratch, dent]
    actions:
      - type: write_register
        target: plc-line1
        register: 101
        value: 1
      - type: write_coil
        target: plc-line1
        coil: 7
        value: true
      - type: delay_ms
        value: 200
      - type: write_register
        target: plc-line1
        register: 101
        value: 0
  - trigger:
      skill: industrial-qc
      event: defect_resolved       # 工人处理完
    actions:
      - type: write_register
        register: 102
        value: 1
      - type: delay_ms
        value: 500
      - type: write_register
        register: 102
        value: 0
```

### 4.4.3 Modbus 安全网关 + OPC UA 桥接

```yaml
# 现场 PLC 都是 Modbus，但客户 MES 只支持 OPC UA
# 智体盒子作为网关，做 Modbus ← → OPC UA 双向转换
gateway:
  south_bound:                          # 下游：PLC
    type: modbus_tcp
    devices:
      - {host: 192.168.1.50, unit_id: 1, name: PLC1}
      - {host: 192.168.1.51, unit_id: 1, name: PLC2}
  north_bound:                          # 上游：MES
    type: opcua_server
    endpoint: opc.tcp://0.0.0.0:4840
  mapping:
    PLC1.HoldingRegister[0]:
      opcua_node: ns=2;s=PLC1.ProductionCount
      type: uint16
    PLC1.HoldingRegister[1]:
      opcua_node: ns=2;s=PLC1.DefectCount
      type: uint16
    PLC1.HoldingRegister[3]:
      opcua_node: ns=2;s=PLC1.Temperature
      type: float
      scale_factor: 0.1
    PLC1.Coil[0]:
      opcua_node: ns=2;s=PLC1.Running
      type: boolean
    ai.qc_result:
      opcua_node: ns=2;s=AI.QCResult
      direction: write_to_opcua_from_ai
```

### 4.4.4 电表 / 仪表数据采集

```yaml
# 应用场景：采集 20 台电表数据，AI 分析能耗异常
modbus_energy_meters:
  - meter_id: EM-01
    host: 192.168.1.100
    unit_id: 1
    type: schneider_pm5320
    registers:
      - address: 3000
        name: voltage_a
        type: float
      - address: 3002
        name: current_a
        type: float
      - address: 3054
        name: total_active_power
        type: float
        unit: kW
      - address: 3840
        name: total_energy
        type: float
        unit: kWh
    scan_interval_ms: 5000
  - meter_id: EM-02
    host: 192.168.1.101
    ...
ai_skill:
  name: energy-monitoring
  trigger:
    - if: total_power - avg(total_power, 24h) > 2σ then anomaly_alert
    - if: energy_total(today) - energy_total(yesterday) > 120% then abnormal_increase
```

---

## 4.5 常见问题与解决

| 问题 | 现象 | 根因 | 解决方案 |
|------|------|------|---------|
| **Connection refused** | TCP 连接被拒 | 1. 端口错 2. 没起来 Server 3. 防火墙 | 测 telnet 502；启 Modbus Server |
| **No response / Timeout** | 无响应 | 1. unit_id 错 2. 寄存器范围越界 3. 双字序问题 | 查设备手册；调整寄存器地址 |
| **Illegal Data Address** | 返回错误码 02 | 寄存器地址不在范围内 | 查设备地址映射表（如 40001-49999） |
| **Illegal Function** | 不支持的功能码 | 该设备只支持部分功能码 | 改用兼容的功能码（如 03 vs 04） |
| **Slave Device Failure** | 错误码 04 | PLC 内部处理失败 | 查 PLC 日志；可能是数据溢出 |
| **CRC Error** | RTU 模式校验错 | 字节序或时序错 | Modbus TCP 通常无 CRC 问题；检查 TCP 完整性 |
| **多设备同 IP** | 数据串台 | 二层 VLAN/路由配错 | 改端到端 IP；用 PCAP 抓包分析 |
| **寄存器读写值不对** | 读到错值 | byte/word order；scale factor | 设备手册有字节序说明；带符号、单位换算 |
| **写不进去** | write 报 Illegal Address | 该寄存器只读（Input） | 改用 Holding Register；查设备权限 |
| **并发冲突** | 同时读写多寄存器失败 | Modbus 是 request-response，不支持并发 | 串行化请求；每次只能一个事务 |
| **连接频繁断开** | Modbus TCP 长连接掉线 | keep-alive/中间网络设备 | 启用 keep-alive（60s 一次）；加重连 |

---

## 4.6 参考资料

- **Modbus 官方规范**：http://www.modbus.org/specs.php
- **Modbus 工具**：https://www.modbustools.com/modbus_poll.html
- **libmodbus 库**：https://libmodbus.org/
- **pymodbus（Python）**：https://github.com/riptideio/pymodbus
- **Modbus Master Simulator**：https://www.win-tech.com/demos/demo32.htm

---

# §5. MQTT（Message Queuing Telemetry Transport）

## 5.1 协议概述

### 5.1.1 是什么

MQTT 由 IBM 的 Andy Stanford-Clark 与 Eurotech 的 Arlen Nipper 于 **1999 年**为窄带卫星链路和石油管道监控设计。它是一个**轻量级发布/订阅（Pub/Sub）消息协议**，针对低带宽、不稳定网络的 IoT 场景优化。**2014 年成为 OASIS 标准**，现在是 IoT 和工业 IoT 最流行的应用层协议。

```text
MQTT 架构：

发布者 Publisher ══╗
                     ╠══→  MQTT Broker（消息中枢）══→ 订阅者 Subscriber
发布者 Publisher ══╝                          ↑     订阅者 Subscriber
                                        （主题路由）

核心概念：
- Topic（主题）：分层消息路由（如 factory/line1/temperature）
- QoS（消息质量）：0 最多一次 / 1 至少一次 / 2 恰好一次
- Retain（保留消息）：新订阅者立即收到最后一条消息
- Last Will（遗嘱）：客户端异常断开时自动通知
```

**关键点**：
- 基于 TCP（端口 1883 明文 / 8883 TLS）
- 极轻量（头部最小 2 字节）
- 三种 QoS 等级适配不同可靠需求
- 心跳机制（Keep Alive）保持长连接

### 5.1.2 协议版本

- **MQTT 3.1.0**：OASIS 标准基础版
- **MQTT 3.1.1**：当前最广泛支持（推荐）
- **MQTT 5.0**：2019 年发布，新增多项企业特性：
  - 共享订阅（Shared Subscriptions，多客户端负载均衡）
  - 主题别名（Topic Alias，节省带宽）
  - 消息属性（User Properties）
  - Reason Codes（详尽响应码）
- **MQTT-SN**：UDP 适配版本（极低带宽）
- **MQTT over QUIC**：基于 UDP 的低延迟版本（试验中）

### 5.1.3 常见 Broker

| Broker | 特点 |
|--------|------|
| **EMQX**（开源） | 国货龙头，分布式、100万级连接 |
| **Mosquitto**（轻量） | 单机部署，5万级连接 |
| **HiveMQ**（企业） | 商业版本，企业特性全 |
| **VerneMQ** | 高性能，水平扩展 |
| **AWS IoT Core** | 云托管 |
| **阿里云 LinkKit IoT** | 云托管 |
| **EMQX Cloud** | 国货云托管 |

---

## 5.2 适用场景

| 场景 | MQTT 用法 |
|------|-----------|
| **告警推送** | 盒子告警 → MQTT Broker → 企业微信 / 钉钉 / SMS 网关 |
| **多端数据订阅** | 同一份数据，多端订阅（展示大屏 / 移动端 / 归档）|
| **设备生命周期管理** | 上下线通知、心跳、配置下发 |
| **车间看板** | 实时数据 → 大屏可视化 |
| **数字孪生** | 双向 MQTT 流（盒子 → 孪生平台；孪生 → 盒子）|
| **OPC UA 桥接** | 盒子 OPC UA Pub/Sub over MQTT |
| **算网设备纳管** | 龙虾算网节点 → MQTT 上报 → 算网调度 |

---

## 5.3 对接步骤

### Step 1：选择 Broker

```yaml
mqtt_brokers:
  - broker_id: customer-broker-1
    role: customer                      # 客户自有
    endpoint: mqtt://192.168.1.200:1883
    auth:
      username: agi-agent
      password: {保密}
    client_id_prefix: "zhiti-ai-box"
  - broker_id: agi-cloud-broker
    role: cloud                          # 智体云
    endpoint: mqtts://mqtt.594agent.com:8883
    auth:
      username: {授权 ID}
      password: {授权 token}
      tls:
        ca: ca.crt
        client_cert: client.crt
        client_key: client.key
    client_id_prefix: "zhiti-prod"
```

### Step 2：在智体盒子启用 MQTT 客户端

```yaml
mqtt_clients:
  - broker_id: customer-broker-1
    client_id: zhiti-ai-box-SN12345678     # 必须唯一
    transport: tcp                          # tcp / websockets / tls
    keep_alive_seconds: 60                  # 心跳
    clean_session: false                    # 持久会话（重启保留订阅）
    auto_reconnect: true
    reconnect:
      min_ms: 1000
      max_ms: 60000
      exponential_backoff: true
    last_will:                              # 遗嘱
      topic: zhiti/ai-box/SN12345678/status
      payload: offline
      qos: 1
      retain: true
    queues:                                 # 离线消息队列
      max_inflight: 100
      max_queued: 10000
```

### Step 3：定义发布主题

```yaml
publishes:
  # 1. 设备状态（每分钟）
  - topic: zhiti/ai-box/SN12345678/status
    qos: 1
    retain: true
    interval_ms: 60000
    payload:
      type: device_status
      fields:
        device_id: SN12345678
        timestamp: ${iso8601}
        online: true
        cpu_usage: 35
        memory_usage: 40
        disk_usage: 60
        temperature: 45
        uptime_s: 86400
        skill_running: [safety-monitoring, shelf-gap-detection]
  
  # 2. 告警事件（实时）
  - topic: zhiti/ai-box/SN12345678/alarms
    qos: 1
    retain: false
    trigger: skill.event.fired
    payload:
      type: alarm
      fields:
        alarm_id: ${uuid}
        device_id: SN12345678
        skill: ${skill_name}
        class: ${event_class}
        severity: ${p0|p1|p2|p3}
        location: ${camera_id}
        timestamp: ${iso8601}
        evidence_url: ${screenshot_url}
        confidence: 0.92
  
  # 3. QC 检测结果（每次）
  - topic: zhiti/ai-box/SN12345678/qc-results
    qos: 2
    payload:
      type: qc_result
      fields:
        timestamp: ${iso8601}
        line_id: L1
        station_id: S1
        workpiece_id: ${from_plc}
        result: PASS                          # or NG
        ng_class: ${if NG then type}
        confidence: 0.96
        decision_time_ms: 230
  
  # 4. 摄像头流量指标
  - topic: zhiti/ai-box/SN12345678/cameras/metrics
    qos: 0
    interval_ms: 30000
```

### Step 4：定义订阅主题

```yaml
subscriptions:
  - topic: zhiti/cmd/SN12345678/+
    qos: 1
    description: 远程控制命令
    handler:
      - topic_pattern: "reboot"
        action: reboot_box
        auth_required: true
        allowed_clients: ["ops-center"]
      - topic_pattern: "skill/stop"
        action: stop_skill
        payload: { skill_name: "${payload.skill}" }
      - topic_pattern: "skill/update"
        action: update_skill
        payload: { skill_name: "...", version: "..." }
      - topic_pattern: "config/update"
        action: update_config
        payload: { key: "...", value: "..." }
  
  - topic: zhiti/event/+/alarms
    qos: 1
    description: 接收其他设备告警（用于级联）
    handler:
      - action: forward_to_console
      - action: trigger_skill_chain
```

### Step 5：测试通信

```bash
# 用 mosquitto 工具
# 安装：apt-get install mosquitto-clients

# 订阅
mosquitto_sub -h 192.168.1.200 -p 1883 -u agi-agent -P xxx \
  -t "zhiti/ai-box/SN12345678/status" -v

# 发布
mosquitto_pub -h 192.168.1.200 -p 1883 -u agi-agent -P xxx \
  -t "zhiti/cmd/SN12345678/reboot" -m '{"reason":"manual"}'
```

```python
# 智体盒子内 Python 伪代码（paho-mqtt 库）
import paho.mqtt.client as mqtt

def on_connect(client, userdata, flags, rc):
    print(f"Connected with result code {rc}")
    client.subscribe("zhiti/cmd/SN12345678/+")
    # 上线通知
    client.publish("zhiti/ai-box/SN12345678/status", 
                   '{"status":"online"}', qos=1, retain=True)

def on_message(client, userdata, msg):
    topic_parts = msg.topic.split('/')
    if topic_parts[-1] == 'reboot':
        if auth_check(msg):
            os.system("sudo reboot")

client = mqtt.Client()
client.username_pw_set("agi-agent", "xxx")
client.on_connect = on_connect
client.on_message = on_message
client.connect("192.168.1.200", 1883, 60)
client.loop_forever()
```

---

## 5.4 配置示例

### 5.4.1 告警推送网关

```yaml
# 应用场景：客户企业微信 / 钉钉无直接 MQTT 接入
# 智体盒子自动桥接：MQTT → Webhook（企业微信）
mqtt_to_wechat_bridge:
  enabled: true
  broker: customer-broker-1
  subscribe_topic: "zhiti/+/alarms"
  qos: 1
  webhook:
    url: "https://qyapi.weixin.qq.com/cgi-bin/webhook/send?key=xxxxx"
    template: |
      {
        "msgtype": "markdown",
        "markdown": {
          "content": "## ${severity}告警\n**设备**：${device_id}\n**位置**：${location}\n**类型**：${class}\n**时间**：${timestamp}\n[查看详情](${evidence_url})"
        }
      }
  conditions:
    severity_filter: ["P0", "P1"]          # 只推重要告警
    time_window: ["08:00-22:00"]
    cooldown_seconds: 60                   # 同设备 60 秒内不重推
```

### 5.4.2 MQTT 5 共享订阅（多端负载均衡）

```yaml
# 应用场景：客户有 3 个中央大屏需要同一份实时数据
mqtt5_shared_subscriptions:
  - topic: "$share/zhiti-stream/line1/all"
    description: 共享订阅 3 个大屏节点
    subscribers: ["dash-board-A", "dash-board-B", "dash-board-C"]
    strategy: round_robin                  # or random / hash
    # 每个订阅者只接收一部分消息，负载均衡
```

### 5.4.3 数字孪生平台对接

```yaml
# 应用场景：智体盒子向数字孪生平台上报实时数据；平台下发控制指令
mqtt_digital_twin:
  broker: mqtts://twin.platform.com:8883
  reports:
    - topic: factory/line1/state
      payload_template: |
        {
          "ts": "${iso8601}",
          "line_state": "${plc.running ? 'RUNNING' : 'STOPPED'}",
          "production": "${plc.OK_count}",
          "defect": "${plc.NG_count}",
          "ai_alarms": "${recent_alarms_count}"
        }
      interval_ms: 1000
  commands:
    - topic: factory/line1/cmd/+
      handler: write_to_plc
    - topic: factory/line1/config/+
      handler: update_config
```

### 5.4.4 算网节点纳管

```yaml
# 应用场景：龙虾算网 V2.1 节点统一纳管
# 智体云平台订阅所有算网节点的 MQTT
agg_network_mqtt:
  broker: mqtts://agg.594agent.com:8883
  username: agg-node-${node_id}
  password: ${auth_token}
  client_id: agg-node-${node_id}
  publishes:
    - topic: agg/network/status
      interval_ms: 30000
      payload: {online, compute_load, idle_gpu, allocated_skills}
    - topic: agg/network/credit
      payload: {earned_credits_per_hour, tasks_completed}
    - topic: agg/network/heartbeat
      interval_ms: 30000
  subscribes:
    - topic: agg/network/task/+
      handler: execute_task
    - topic: agg/network/config/+
      handler: update_config
```

---

## 5.5 常见问题与解决

| 问题 | 现象 | 根因 | 解决方案 |
|------|------|------|---------|
| **Connection refused** | TCP 连不上 | 1. 端口错 2. 防火墙 3. broker 未启动 | 测 telnet 1883；启 broker；开 ACL |
| **Auth failed (5)** | 鉴权失败 | 用户名/密码错 | 重新配置 broker 用户 |
| **Not authorized (5)** | 鉴权失败但用户存在 | ACL 限制（白名单） | broker 配置允许 client_id / topic 前缀 |
| **Topic not found** | 订阅无消息 | 消息发到别的 topic | 检查 topic 拼写；用通配符订阅 `+`、`#` |
| **QoS 2 重传太频繁** | 大量 PUBLISH 重传 | 网络抖动 | 改用 QoS 1；增大 inflight |
| **消息丢失** | 发送成功但订阅者没收到 | QoS 0 + 异常断开 | 用 QoS 1 或 2；启用持久会话 |
| **保留消息覆盖** | 订阅新设备总收到旧消息 | retain 没清 | 用 admin API 清；或者删除重发 |
| **客户端掉线** | LastWill 触发意外 | 1. 心跳超时 2. 网络中断 | 调 keep_alive 到 30-60s；查网络 |
| **百万级连接扛不住** | broker 性能瓶颈 | 单机 Mosquitto 上限约 5 万 | 换 EMQX 分布式；多 broker 分片 |
| **TLS 握手失败** | 无法 TLS 连接 | 1. 证书不匹配 2. CA 未导入 | 装客户端证书；信任服务端 CA |
| **消息乱码** | 收到乱码字符串 | 编码不一致 | 用 UTF-8 发送；统一编码声明 |

---

## 5.6 参考资料

- **MQTT 官方规范（OASIS）**：https://docs.oasis-open.org/mqtt/mqtt/v5.0/mqtt-v5.0.html
- **EMQX 文档**：https://docs.emqx.io/
- **Mosquitto**：https://mosquitto.org/
- **HiveMQ**：https://www.hivemq.com/
- **paho-mqtt（Python）**：https://github.com/eclipse/paho.mqtt.python
- **MQTT Box（测试客户端）**：http://workswithweb.com/mqttbox.html

---

# §6. HTTP API（RESTful API）

## 6.1 协议概述

### 6.1.1 是什么

**HTTP API** 是基于 HTTP/HTTPS 协议的 **REST（Representational State Transfer）** 风格接口。**REST** 是 Roy Fielding 在 **2000 年博士论文**中正式命名的架构风格，不是协议而是设计约定。HTTP API 利用 HTTP 方法（GET/POST/PUT/DELETE）操作资源（Resource），用 URL 标识资源，用 JSON/XML 作为数据格式。

```text
HTTP API 核心约定：
- 资源用 URL 表示（/customers/12345）
- HTTP 方法代表动作（GET 读 / POST 创建 / PUT 更新 / DELETE 删除）
- 状态码表示结果（200 OK / 201 Created / 404 Not Found）
- JSON 作为数据格式（推荐，替代 XML）
- 无状态（无 session；用 token / cookie）

请求结构：
GET /api/v1/customers/12345 HTTP/1.1
Host: api.example.com
Authorization: Bearer eyJhbGc...
Content-Type: application/json

响应：
HTTP/1.1 200 OK
Content-Type: application/json
{
  "id": "12345",
  "name": "ABC 公司",
  "status": "active"
}
```

### 6.1.2 关键概念

| 概念 | 说明 |
|------|------|
| **REST** | Representational State Transfer 架构风格 |
| **RESTful** | 遵循 REST 风格的 API |
| **HTTP 方法** | GET 读 / POST 创建 / PUT 全量更新 / PATCH 部分更新 / DELETE 删除 |
| **状态码** | 2xx 成功 / 3xx 重定向 / 4xx 客户端错 / 5xx 服务端错 |
| **Header** | Authorization / Content-Type / Accept |
| **数据格式** | JSON（推荐）/ XML / YAML |
| **鉴权** | Bearer Token / API Key / OAuth2 / JWT |
| **限流** | X-RateLimit-* 头 |
| **幂等性** | 同请求多次执行结果一致（重要，POST 不幂等需配 ID）|

### 6.1.3 API 设计规范（智体共合内部）

| 项 | 规范 |
|---|------|
| 基础路径 | `/api/v{major}.{minor}/` |
| 资源命名 | 复数名词（`/customers` 而非 `/customer`） |
| 嵌套资源 | `/customers/{id}/orders`（不超过 2 层） |
| 过滤 | `?status=active&sort=-created_at` |
| 字段展开 | `?expand=items,address` |
| 分页 | `?page=1&page_size=20` 或 `cursor=...&limit=50` |
| 字段过滤 | `?fields=id,name,email` |
| 错误格式 | `{ "code": "...", "message": "...", "trace_id": "..." }` |
| 时间格式 | RFC3339（ISO8601），`2026-08-15T08:30:00+08:00` |
| 长整型 ID | 字符串（避免 JS 精度） |
| 鉴权 | Bearer Token / API Key + Secret |
| CORS | 严格白名单 |
| HTTPS | 强制 |

### 6.1.4 常见业务系统

| 系统 | API 风格 | 文档样例 |
|------|---------|----------|
| **企业微信** | 几乎 RESTful | https://developer.work.weixin.qq.com/document/path/91770 |
| **钉钉** | RESTful | https://open.dingtalk.com/document/isvapp/dingtalk-retail-overview |
| **飞书** | RESTful | https://open.feishu.cn/document/server-docs/api-call-guide/server-api-list |
| **SAP** | OData/REST | https://api.sap.com/ |
| **Salesforce** | RESTful + sObject | https://developer.salesforce.com/docs/atlas.en-us.api_rest.meta/api_rest/intro_rest.htm |
| **MySQL/PostgreSQL** | 无原生 HTTP，但可架 POSTGREST | |
| **阿里云/华为云/腾讯云** | RESTful + OpenAPI | |
| **Webhook**（反向） | RESTful 入参，无状态码 |

---

## 6.2 适用场景

| 场景 | HTTP API 用法 |
|------|--------------|
| **告警推送** | 盒子 → Webhook → 企业微信 / 钉钉 / 飞书 / 自建系统 |
| **业务系统对接** | 盒子 ↔ ERP / CRM / QMS / MES（轻量数据） |
| **云端模型调用** | 盒子 → 智体云 OCR / ASR / LLM API |
| **数据归档** | 盒子 → 自建数据库 / 对象存储（如 MinIO） |
| **Webhook 反向接收** | 盒子作为服务端接收云端下发指令 |
| **数字人调用** | 数字人 Skill → HTTP API 输出视频 |
| **算网任务投递** | 客户端 → HTTP → 算网调度 |

---

## 6.3 对接步骤

### Step 1：接口梳理

```yaml
# 文档清单
api_list:
  - name: 企业微信告警推送
    method: POST
    endpoint: https://qyapi.weixin.qq.com/cgi-bin/webhook/send
    auth: ?key=xxxxx (URL query)
    body_schema: { msgtype: "markdown", markdown: {content: "..."} }
    response: { errcode: 0, errmsg: "ok" }
  - name: 钉钉告警推送
    method: POST
    endpoint: https://oapi.dingtalk.com/robot/send
    auth: ?access_token=xxxxx
    sign_required: true
    body_schema: { msgtype: "action_card", action_card: {...} }
  - name: MES 工单上传
    method: POST
    endpoint: https://mes.customer.com/api/v1/workorders
    auth: Bearer Token
    body_schema: { line: "L1", workpiece_id: "...", qc_result: "..." }
  - name: 智体云 LLM API
    method: POST
    endpoint: https://api.594agent.com/v1/chat/completions
    auth: Bearer Token
    body_schema: {model, messages, temperature}
```

### Step 2：HTTP 客户端配置（智体盒子）

```yaml
http_clients:
  - client_id: wechat-bot
    base_url: https://qyapi.weixin.qq.com/cgi-bin
    auth:
      type: query_param
      key: key
      value: "${wechat_webhook_key}"
    default_headers:
      Content-Type: application/json
      User-Agent: ZhiTiAIBox/1.0
    timeout_ms: 10000
    retry_policy:
      max_retries: 3
      backoff: [1000, 3000, 5000]
      retry_on_status: [408, 429, 500, 502, 503, 504]
    rate_limit:
      max_per_second: 10
      max_per_minute: 200

  - client_id: mes-api
    base_url: https://mes.customer.com/api/v1
    auth:
      type: bearer_token
      token: "${mes_token}"
      refresh_url: https://mes.customer.com/oauth/token
      refresh_interval_s: 3600
    default_headers:
      Content-Type: application/json
      X-API-Key: ${mes_api_key}
    timeout_ms: 15000

  - client_id: agi-cloud
    base_url: https://api.594agent.com/v1
    auth:
      type: bearer_token
      token: "${zhiti_api_key}"
    default_headers:
      X-Source: ai-box-pro
      X-Customer-ID: ${customer_id}
```

### Step 3：调用层（推送告警示例）

```python
# 智体盒子内 Python 伪代码
import httpx
import asyncio

async def push_wechat_alert(alarm: dict):
    client = httpx.AsyncClient(timeout=10.0)
    
    payload = {
        "msgtype": "markdown",
        "markdown": {
            "content": (
                f"## ⚠️ {alarm['severity']}告警\n"
                f"**设备**：{alarm['device_id']}\n"
                f"**位置**：{alarm['location']}\n"
                f"**类型**：{alarm['class']}\n"
                f"**时间**：{alarm['timestamp']}\n"
                f"[查看截图]({alarm['evidence_url']})"
            )
        }
    }
    
    for attempt in range(3):
        try:
            resp = await client.post(
                f"/webhook/send",
                params={"key": "${wechat_webhook_key}"},
                json=payload
            )
            if resp.status_code == 200:
                data = resp.json()
                if data.get("errcode") == 0:
                    return {"success": True, "msgid": "..."}
                raise Exception(f"API errcode {data.get('errcode')}")
            elif resp.status_code in (429, 500, 502, 503, 504):
                await asyncio.sleep(1 + attempt * 2)
            else:
                raise Exception(f"HTTP {resp.status_code}")
        except Exception as e:
            if attempt == 2:
                return {"success": False, "error": str(e)}
```

### Step 4：Webhook 接收（盒子作为服务端）

```yaml
# 应用场景：客户云端系统主动调用盒子 API
http_server:
  enabled: true
  bind: 0.0.0.0:8080
  tls:
    enabled: true
    cert: /etc/ssl/cert.pem
    key: /etc/ssl/key.pem
  auth:
    required: true
    type: api_key
    keys:
      - key: "${api_key_customer_A}"
        client: customer-A
        permissions: ["read", "write"]
      - key: "${api_key_admin}"
        client: admin
        permissions: ["read", "write", "admin"]
  routes:
    # 设备管理
    - method: GET
      path: /api/v1/devices
      handler: list_devices
    - method: GET
      path: /api/v1/devices/{device_id}
      handler: get_device
    - method: PUT
      path: /api/v1/devices/{device_id}/config
      handler: update_config
      body_schema:
        properties:
          skill_name: { type: string }
          threshold: { type: number, min: 0, max: 1 }
    # 告警
    - method: GET
      path: /api/v1/alarms
      handler: list_alarms
      params:
        - {name: from_time, type: datetime}
        - {name: to_time, type: datetime}
        - {name: severity, type: string, enum: [P0,P1,P2,P3]}
    - method: POST
      path: /api/v1/alarms/{alarm_id}/acknowledge
      handler: ack_alarm
    # Skill 管理
    - method: POST
      path: /api/v1/skills/{skill_name}/stop
      handler: stop_skill
    - method: POST
      path: /api/v1/skills/{skill_name}/start
      handler: start_skill
    - method: GET
      path: /api/v1/skills/{skill_name}/metrics
      handler: get_skill_metrics
    # 模型
    - method: POST
      path: /api/v1/models/{model_id}/update
      handler: update_model
```

### Step 5：Webhook 反向接收（云端 → 盒子推送）

```yaml
# 应用场景：智体云告警校验完成后推送盒子
webhook_receiver:
  enabled: true
  endpoint_path: /api/v1/webhook/zhiti-cloud
  auth: shared_secret + HMAC-SHA256
  signature_header: X-Zhiti-Signature
  handlers:
    - topic_pattern: "alarm_validate"
      action: trigger_push_for_real
    - topic_pattern: "skill_push"
      action: download_and_install_skill
    - topic_pattern: "model_update"
      action: download_and_install_model
```

---

## 6.4 配置示例

### 6.4.1 多通道告警推送（Hub-and-Spoke 模式）

```yaml
alert_hub:
  name: factory-alert-hub
  source: skill.alarms
  deduplication:
    enabled: true
    window_s: 60
  routing:
    - condition: severity == "P0"
      targets:
        - {type: wechat, channel: critical-group}
        - {type: dingtalk, channel: plant-manager}
        - {type: sms, recipients: ["+86..."]}
        - {type: voice_call, recipients: ["+86..."]}
    - condition: severity == "P1"
      targets:
        - {type: wechat, channel: safety-team}
        - {type: dingtalk, channel: safety-team}
    - condition: severity == "P2"
      targets:
        - {type: wechat, channel: control-room}
    - condition: severity == "P3"
      targets:
        - {type: dashboard, channel: ops-dashboard}
  batching:
    enabled: true
    max_batch_size: 10
    max_batch_interval_s: 30
```

### 6.4.2 SaaS 业务系统对接示例

```python
# 智体盒子 × 客户 ERP 对接
import httpx

async def sync_qc_to_erp(qc_record):
    """上传 QC 结果到客户 ERP 系统"""
    client = httpx.AsyncClient(
        base_url="https://erp.customer.com/api/v1",
        headers={"Authorization": "Bearer xxx"}
    )
    
    # 1. 查询工单是否存在
    resp = await client.get(f"/workorders/{qc_record['workorder_id']}")
    if resp.status_code != 200:
        raise Exception("工单不存在或无权限")
    
    # 2. 上传 QC 结果
    resp = await client.post(
        "/quality-records",
        json={
            "workorder_id": qc_record['workorder_id'],
            "result": qc_record['result'],
            "ng_class": qc_record.get('ng_class'),
            "workpiece_id": qc_record['workpiece_id'],
            "timestamp": qc_record['timestamp'],
            "evidence": {
                "image_url": qc_record['image_url'],
                "video_url": qc_record.get('video_url'),
            },
            "inspector": "AI-Agent-CrayfishBox01",
            "algorithm_version": "industrial-qc v2.3.1",
        }
    )
    if resp.status_code != 201:
        raise Exception(f"上传失败：{resp.text}")
    return resp.json()['id']
```

### 6.4.3 文件上传 / 下载（大文件流式）

```python
# AI 模型权重 OTA 下载
import httpx

async def download_model(model_url: str, save_path: str):
    """流式下载大模型（GB 级）"""
    async with httpx.AsyncClient(timeout=httpx.Timeout(connect=10, read=300, write=10, pool=10)) as client:
        async with client.stream("GET", model_url) as resp:
            resp.raise_for_status()
            total = int(resp.headers.get("content-length", 0))
            downloaded = 0
            with open(save_path, "wb") as f:
                async for chunk in resp.aiter_bytes(chunk_size=64*1024):
                    f.write(chunk)
                    downloaded += len(chunk)
                    progress = downloaded / total * 100
                    if progress % 10 < 1:
                        print(f"已下载 {progress:.1f}%")
    return save_path
```

### 6.4.4 GraphQL 对接（高级）

```python
# 适用场景：客户系统是 GraphQL（部分新系统支持）
import httpx

async def fetch_alarms_graphql(cursor=None, limit=50):
    query = """
    query alarms($cursor: String, $limit: Int!) {
      alarms(after: $cursor, first: $limit) {
        edges {
          node {
            id
            deviceId
            severity
            eventClass
            timestamp
            evidenceUrl
          }
        }
        pageInfo {
          endCursor
          hasNextPage
        }
      }
    }
    """
    
    variables = {"cursor": cursor, "limit": limit}
    
    async with httpx.AsyncClient() as client:
        resp = await client.post(
            "https://api.customer.com/graphql",
            json={"query": query, "variables": variables},
            headers={"Authorization": "Bearer xxx"}
        )
        return resp.json()
```

---

## 6.5 常见问题与解决

| 问题 | 现象 | 根因 | 解决方案 |
|------|------|------|---------|
| **401 Unauthorized** | Token 无效 | 1. Token 过期 2. Token 错 3. 未带 Token | 刷新 Token；查 Authorization 头格式 |
| **403 Forbidden** | 鉴权失败用户有，但无权限 | RBAC 权限不够 | 联系 API 提供方；检查 scope |
| **404 Not Found** | 资源不存在 | 1. URL 错 2. ID 错 3. 已删 | 验证 URL/ID |
| **429 Too Many Requests** | 触发限流 | 超过速率限制 | 实施退避；启用 rate_limit 重试 |
| **500 / 502 / 503** | 服务端错 | Server 内部异常 | 自动重试；联系 API 方 |
| **504 Gateway Timeout** | 网关超时 | 慢接口或后端阻塞 | 扩大 timeout；联系运营方 |
| **请求超时** | 客户端超时 | 网络慢或服务慢 | 提高 timeout（连接 vs 读取分开） |
| **CORS 错误** | 浏览器跨域 | 浏览器安全策略 | 加 CORS 头（仅 Web 服务器场景） |
| **证书无效** | TLS 握手失败 | 1. SSL 证书过期 2. 自签证书 | 用受信证书；或禁用校验（仅内网） |
| **502 Bad Gateway** | 网关返回错 | 反向代理断 | 查上游服务；改直连验证 |
| **JSON 解析失败** | 请求失败 | 字段类型不对 | 用 Pydantic 模型验证；服务端校验 |
| **SSL 握手慢** | HTTPS 慢 | 1. SNI 错 2. 证书链不全 3. 服务器硬件慢 | 排查证书链；用 curl -vvv |

---

## 6.6 参考资料

- **RESTful API 最佳实践**：
  - Microsoft API Design Guidelines
  - Google API Design Guide
  - 阿里云 API Design Guide
- **HTTP 规范 RFC**：
  - RFC 7230-7235（HTTP/1.1）
  - RFC 7540（HTTP/2）
  - RFC 9110（HTTP Semantics）
- **OpenAPI 规范**：https://swagger.io/specification/
- **JSON Schema 校验**：https://json-schema.org/
- **Postman**：https://www.postman.com/
- **curl 教程**：https://everything.curl.dev/
- **httpx 库（Python 异步）**：https://www.python-httpx.org/
- **企业微信 API 文档**：https://developer.work.weixin.qq.com/document/
- **钉钉开放平台**：https://open.dingtalk.com/document/
- **飞书开放平台**：https://open.feishu.cn/document/
- **智体联邦知识库**（kb_id: `XrneKkrCkkdLgfe-lti6VAiwoipSAe7CsltatLHrAAs=`）→ 搜"HTTP API"获取更多案例

---

# §7. 协议选型决策树

```
                   ┌──────────────────────────────────────┐
                   │  客户需要什么类型的对接？                │
                   └──────────────────────────────────────┘
                                    │
            ┌───────────────────┬───┴──────┬─────────────────────┐
            ▼                   ▼          ▼                     ▼
        视频流              工业设备    业务系统/推送            IoT/状态
            │                   │          │                     │
        RTSP + ONVIF     OPC UA 首选    HTTP API 首选      MQTT 首选
        (老摄像头用         Modbus TCP    (ERP/CRM/钉钉/      (轻量消息
         RTSP 兜底)        (老 PLC 用)    企业微信)            跨设备)
                          Modbus 兜底
```

**决策要点**：
1. **视频**：新摄像头先 ONVIF 发现，老摄像头用 RTSP 兜底；存录像用 RTSP。
2. **工业**：新 PLC 用 OPC UA；老 PLC / 国产 PLC / 工业仪表用 Modbus TCP；信创场景必须 OPC UA。
3. **业务**：HTTP API 是首选；推送通道（微信/钉钉/SMS）都是 HTTP Webhook；用 MQTT 中转更可靠。
4. **IoT**：MQTT 是首选；小规模用 HTTP 也可。
5. **混合场景**：网关模式 + 多协议混用（如 Modbus + OPC UA 桥接；MQTT + HTTP 推送）。

---

# §8. 对接项目常见组合示例

| 场景 | 协议组合 |
|------|---------|
| **工业质检** | RTSP + OPC UA + HTTP API + 企业微信 Webhook |
| **安全监测** | RTSP + ONVIF + MQTT + HTTP API + 钉钉 Webhook |
| **货架空位** | RTSP + HTTP API + 企业微信 Webhook |
| **AI 店长** | RTSP + HTTP API（POS 收银对接）+ HTTP API（推送）|
| **政企内网** | ONVIF + OPC UA + Modbus TCP + LDAP/SSO + HTTP API（内网）|
| **算网节点** | MQTT + HTTP API + HTTP Webhook |
| **数字人生产** | HTTP API（数字人生成）+ RTSP 推流 / HTTP 文件下载 + MQTT 订阅 |

---

# §9. 协议对接安全清单

| # | 检查项 | 标准 | 必填 |
|---|--------|------|------|
| 1 | 鉴权（认证） | 必须用 Token / 证书 / OAuth2 | ✓ |
| 2 | 加密传输 | 内网可用明文；外网必须 TLS | ✓ |
| 3 | 最小权限 | 每个服务账号只给所需权限（RBAC） | ✓ |
| 4 | 输入校验 | 服务端校验所有输入字段 | ✓ |
| 5 | 速率限制 | 所有 API 启用 Rate Limiting | ✓ |
| 6 | 审计日志 | 所有调用记录审计日志 | ✓ |
| 7 | 超时控制 | 所有外部调用必须有 timeout | ✓ |
| 8 | 重试策略 | 仅幂等请求可重试 | ✓ |
| 9 | 降级策略 | 关键路径有 fallback | ✓ |
| 10 | 凭据存储 | 密码/Token 用 Vault / KMS / Secret 管理 | ✓ |

---

# §10. 排查速查表（综合）

| 协议 | 排查工具 | 命令/方法 |
|------|---------|-----------|
| **RTSP** | VLC / ffplay / ffprobe | `ffprobe rtsp://...` |
| **ONVIF** | ONVIF Device Manager | GUI 工具 |
| **OPC UA** | UA Expert / Prosys Browser / Python opcua | `python -c "from opcua import Client; ..."` |
| **Modbus TCP** | MBPoll / pymodbus / libmodbus | `mbpoll -m tcp -a 1 -t 4 -r 1 -c 5 IP` |
| **MQTT** | mosquitto-clients / MQTT Box / MQTTX | `mosquitto_sub -h IP -t topic -v` |
| **HTTP API** | curl / Postman / httpie | `curl -v -X POST -H 'Auth...' URL` |

---

> **协议对接是 FDE 工作的"硬功夫"。掌握这 6 大协议可覆盖 90% 客户场景。**
> **遇到生僻协议（Profibus / EtherCAT / BACnet / DNP3 / IEC 61850 等）时，可联系智体技术支持或通过网关适配。**
> **本指南将随客户项目沉淀持续迭代，每个完成的项目应贡献至少 1 条协议实战经验。**

---

## 附录：智体共合协议推荐

| 协议 | 智体共合产品支持 | 推荐理由 |
|------|----------------|---------|
| RTSP | ★★★★★ 全产品 | 视频基础协议 |
| ONVIF | ★★★★ 盒子 Pro / Enterprise | 多厂商兼容 |
| OPC UA | ★★★★ 盒子 Pro / Enterprise / 信创 | 工业标准 + 信创合规 |
| Modbus TCP | ★★★ 盒子 / 网关 | 老 PLC 兜底 |
| MQTT | ★★★ 盒子 / 算网节点 | IoT 标准 |
| HTTP API | ★★★★★ 全产品 + 智体云 | 万能通用 |

---

> **文档维护**：zhiti-fde-expert/references/protocol-integration-guide.md
> **最后更新**：与版本号同步（OpenClaw v1.0+）
> **反馈渠道**：support@594agent.com 或 Agent 俱乐部技术问答
