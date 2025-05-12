# 🚀 GamePing DNS Optimizer

A powerful DNS testing tool designed specifically for gamers to find the fastest and most responsive DNS servers for optimal gaming performance.

![[DNS Tester](https://github.com/ice-exe/gameping-dns-optimizer/raw/main/assets/banner.png)](https://raw.githubusercontent.com/ice-exe/GamePing-DNS-Optimizer/refs/heads/main/results.png)

## 🎮 Overview

GamePing DNS Optimizer tests multiple popular DNS providers to determine which ones offer the lowest latency, jitter, and packet loss - the key metrics that affect your gaming experience. The tool automatically ranks DNS servers based on their overall gaming performance score and recommends the best primary and secondary DNS configurations for your system.

## ✨ Features

- **Gaming-Optimized Metrics**: Measures latency, jitter, and packet loss - the metrics that matter most for gaming
- **Comprehensive DNS Provider Testing**: Tests 14+ popular DNS providers including Google, Cloudflare, Quad9, OpenDNS, and more
- **Automatic Ranking System**: Displays results sorted by a specialized gaming performance score
- **Beautiful Console UI**: Rich, colorful terminal output with progress bars and formatted tables
- **Cross-Platform Support**: Works on Windows, macOS, and Linux

## 📋 Requirements

- Python 3.6+
- Internet connection
- `rich` library (automatically installed if missing)

## 🚀 Installation

1. Clone the repository or download the script:

```bash
git clone https://github.com/ice-exe/GamePingDNS
```

Alternatively, you can download the `dns_tester.py` file directly.

2. Make the script executable (Linux/macOS):

```bash
chmod +x dns_tester.py
```

## 💻 Usage

Run the script:

```bash
python dns_tester.py
```

The application will:
1. Check for the `rich` library and install it if needed
2. Prompt you for the number of pings per server (default: 10)
3. Test all DNS servers in parallel
4. Display results sorted by gaming performance
5. Provide recommendations for primary and secondary DNS servers

## 📊 Understanding the Results

The results are sorted by a "Gaming Score" which combines:
- **Average Latency**: Lower is better (50% weight)
- **Jitter**: Lower is better - measures consistency (30% weight)
- **Packet Loss**: Lower is better - measures reliability (20% weight)

A lower overall score indicates better potential gaming performance.

## 🔧 How to Change Your DNS Servers

### Windows

1. Open Network and Sharing Center
2. Click on your active connection
3. Click Properties
4. Select "Internet Protocol Version 4 (TCP/IPv4)"
5. Click Properties
6. Select "Use the following DNS server addresses"
7. Enter the recommended DNS servers
8. Click OK

### macOS

1. Open System Preferences
2. Click Network
3. Select your active connection
4. Click Advanced
5. Go to DNS tab
6. Click "+" to add DNS servers
7. Enter the recommended DNS servers
8. Click OK, then Apply

### Linux

The method varies by distribution. Generally:

1. Edit `/etc/resolv.conf` or use NetworkManager
2. Add `nameserver x.x.x.x` for each recommended DNS server
3. Save and restart networking service

## 📝 License

This project is licensed under the MIT License - see the comment section at the top of the script for details.

## 👨‍💻 Author

Created by [Ice](https://github.com/ice-exe)

## 🤝 Contributing

Contributions are welcome! Feel free to submit pull requests or open issues on the GitHub repository.
