# 🚀 GamePing DNS Optimizer

A powerful DNS benchmarking tool tailored for gamers, built to analyze and recommend the fastest DNS servers for low-latency, high-reliability online gaming.

![DNS Tester](https://github.com/ice-exe/gameping-dns-optimizer/raw/main/assets/banner.png)

## 🎮 Overview

**GamePing DNS Optimizer** tests multiple DNS providers using real-world metrics that matter most for gaming: **latency**, **jitter**, and **packet loss**. It ranks them using a performance-based scoring system and recommends the best configuration for your system.

## ✨ Features

* 🎯 **Gaming-Optimized Metrics**: Evaluates latency, jitter, and packet loss
* 🌐 **14+ Popular DNS Providers**: Includes Google, Cloudflare, Quad9, OpenDNS, AdGuard, and more
* 📈 **Automatic Ranking**: Sorts servers by average response time and jitter
* 🎨 **Rich Terminal UI**: Colorful, user-friendly output using the `rich` library
* ⚙️ **Settings Menu**: Customize ping count, timeout, workers, and add custom DNS servers
* 💻 **Cross-Platform**: Works on Windows, macOS, and Linux

## 📋 Requirements

* Python 3.6+
* Internet connection
* `rich` Python library (auto-installed on first run)

## 🚀 Installation

```bash
git clone https://github.com/ice-exe/GamePingDNS
cd GamePingDNS
```

Or download the standalone `GamePingDNS.py`.

## 🔧 Make Executable (Optional for Unix-like systems)

```bash
chmod +x GamePingDNS.py
```

## 💻 Usage

Run the tool:

```bash
python GamePingDNS.py
```

You'll be able to:

1. Select between **DNS Test**, **Settings**, or **Exit**
2. Configure ping parameters and custom servers via Settings
3. View ranked DNS results in a table
4. Get **Primary** and **Secondary** DNS recommendations

## 📊 How It Works

Each DNS server is tested with configurable pings, and scored based on:

* 🕒 **Latency (50%)**: Average response time in milliseconds
* 📉 **Jitter (30%)**: Consistency of response time
* ❌ **Packet Loss (20%)**: Stability and reliability of connection

Lower overall scores indicate better gaming DNS performance.

## 🧩 DNS Configuration Help

### Windows

1. Go to *Control Panel → Network and Sharing Center*
2. Click your active connection → *Properties*
3. Double-click *Internet Protocol Version 4 (TCP/IPv4)*
4. Choose *Use the following DNS server addresses*
5. Enter the suggested Primary and Secondary DNS
6. Click OK

### macOS

1. Open *System Preferences → Network*
2. Select your active connection → *Advanced → DNS*
3. Add new DNS servers with the "+" button
4. Click OK, then Apply

### Linux

Edit `/etc/resolv.conf` or use your Network Manager:

```bash
sudo nano /etc/resolv.conf
# Add:
nameserver x.x.x.x
nameserver y.y.y.y
```

## 🔄 Settings Overview

Accessible via the menu:

* Ping Count
* Timeout per ping
* Number of parallel workers
* Show all or only top servers
* Manage custom DNS servers
* Reset to defaults

Settings are saved to `~/.gamepingdns_settings.json`.

## 🛠 Example Output

```text
Rank | Provider        | IP Address     | Avg (ms) | Min | Max | Jitter | Loss
-------------------------------------------------------------------------------
1    | Cloudflare      | 1.1.1.1        | 8.24     | 7.9 | 9.1 | 1.2    | 0.0%
2    | Google Primary  | 8.8.8.8        | 10.87    | 9.2 | 12.5| 2.3    | 0.0%
```

✅ **Recommended DNS Configuration for Gaming**:

* Primary DNS: 1.1.1.1 (Cloudflare)
* Secondary DNS: 8.8.8.8 (Google)

## 📝 License

Licensed under the MIT License. See source code header for details.

## 👨‍💻 Author

Created by [Ice](https://github.com/ice-exe)

## 🤝 Contributing

Issues, suggestions, and pull requests are welcome on the GitHub repo!
