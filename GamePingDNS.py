"""
GamePingDNS - Find the fastest DNS servers for gaming
Copyright (c) 2025 ice
https://github.com/ice-exe
"""
import os
import sys
import time
import json
import socket
import platform
import subprocess
import statistics
from concurrent.futures import ThreadPoolExecutor
from typing import Dict, List, Tuple, Optional, Union
from pathlib import Path
try:
    from rich.console import Console
    from rich.table import Table
    from rich.progress import Progress, TextColumn, BarColumn, TaskProgressColumn, TimeRemainingColumn, SpinnerColumn
    from rich.panel import Panel
    from rich.text import Text
    from rich.layout import Layout
    from rich.live import Live
    from rich.style import Style
    from rich.theme import Theme
    from rich.prompt import Prompt, Confirm
    from rich.box import ROUNDED, HEAVY, DOUBLE
    from rich.markdown import Markdown
    test_console = Console()
    RICH_AVAILABLE = True
except (ImportError, Exception) as e:
    RICH_AVAILABLE = False
    print(f"Rich library issue: {str(e)}")
    print("Continuing with basic console output...\n")
APP_VERSION = "1.1.0"
SETTINGS_FILE = os.path.join(os.path.dirname(os.path.abspath(__file__)), "settings.json")
DEFAULT_SETTINGS = {
    "ping_count": 10,
    "timeout_ms": 1000,
    "max_workers": 10,
    "custom_dns_servers": {},
    "show_all_servers": True,
    "dark_mode": True
}
DEFAULT_DNS_SERVERS = {
    "Google Primary": "8.8.8.8",
    "Google Secondary": "8.8.4.4",
    "Cloudflare Primary": "1.1.1.1",
    "Cloudflare Secondary": "1.0.0.1",
    "Quad9 Primary": "9.9.9.9",
    "Quad9 Secondary": "149.112.112.112",
    "OpenDNS Primary": "208.67.222.222",
    "OpenDNS Secondary": "208.67.220.220",
    "Level3": "4.2.2.2",
    "Comodo Secure DNS": "8.26.56.26",
    "AdGuard DNS": "94.140.14.14",
    "CleanBrowsing": "185.228.168.9",
    "Alternate DNS": "76.76.19.19",
    "NextDNS": "45.90.28.167",
    "Norton ConnectSafe": "199.85.126.10",
}
custom_theme = Theme({
    "info": "dim cyan",
    "warning": "yellow", 
    "danger": "bold red",
    "success": "bold green",
    "title": "bold cyan",
    "subtitle": "italic cyan",
    "highlight": "bold magenta",
    "gold": "#FFD700",
    "silver": "#C0C0C0", 
    "bronze": "#CD7F32",
    "button": "bold white on blue",
    "button.focused": "bold white on dark_blue",
    "menu": "cyan",
    "menu.selected": "bold cyan",
}) if RICH_AVAILABLE else None

console = Console(theme=custom_theme) if RICH_AVAILABLE else None


def load_settings():
    settings = DEFAULT_SETTINGS.copy()
    try:
        if os.path.exists(SETTINGS_FILE):
            with open(SETTINGS_FILE, 'r') as f:
                user_settings = json.load(f)
                settings.update(user_settings)
    except Exception as e:
        if RICH_AVAILABLE:
            console.print(f"[warning]Error loading settings: {str(e)}[/warning]")
        else:
            print(f"Warning: Error loading settings: {str(e)}")
    return settings


def save_settings(settings):
    try:
        with open(SETTINGS_FILE, 'w') as f:
            json.dump(settings, f, indent=4)
        return True
    except Exception as e:
        if RICH_AVAILABLE:
            console.print(f"[danger]Error saving settings: {str(e)}[/danger]")
        else:
            print(f"Error saving settings: {str(e)}")
        return False


def get_dns_servers(settings):
    dns_servers = DEFAULT_DNS_SERVERS.copy()
    if settings.get("custom_dns_servers"):
        dns_servers.update(settings["custom_dns_servers"])
    return dns_servers


def is_admin():
    try:
        if platform.system() == "Windows":
            import ctypes
            return ctypes.windll.shell32.IsUserAnAdmin() != 0
        else:
            return os.geteuid() == 0
    except Exception:
        return False


def print_header():
    if RICH_AVAILABLE:
        title = Text("GamePingDNS", style="bold cyan underline")
        version_text = Text(f"v{APP_VERSION}", style="cyan")
        subtitle = Text(" - Find the fastest DNS servers for gaming", style="italic cyan")
        author = Text("Copyright (c) 2025 ice - https://github.com/ice-exe", style="dim cyan")
        
        header_text = Text.assemble(
            title, "\n\n",
            version_text, subtitle, "\n",
            author
        )
        
        console.print(Panel.fit(
            header_text,
            border_style="cyan",
            box=HEAVY,
            title="[bold cyan]DNS Performance Analyzer[/bold cyan]",
            subtitle="[dim cyan]For Optimal Gaming Experience[/dim cyan]",
            padding=(1, 4)
        ))
        console.print("")
    else:
        print(f"=== GamePingDNS v{APP_VERSION} ===")
        print("Find the fastest DNS servers for gaming")
        print("Copyright (c) 2025 ice - https://github.com/ice-exe")
        print("")


def ping(host, count=10, timeout_ms=1000):
    ping_param = "-n" if platform.system().lower() == "windows" else "-c"
    timeout_param = "-w" if platform.system().lower() == "windows" else "-W"
    timeout_value = str(timeout_ms) if platform.system().lower() == "windows" else str(timeout_ms // 1000)
    
    try:
        if platform.system().lower() == "windows":
            command = ["ping", ping_param, str(count), timeout_param, timeout_value, host]
        else:
            command = ["ping", ping_param, str(count), timeout_param, timeout_value, host]
        
        result = subprocess.run(
            command,
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            text=True,
            check=False,
            timeout=count * (timeout_ms / 1000) * 1.5
        )
        
        if result.returncode != 0:
            return None
        
        output = result.stdout
        times = []
        
        for line in output.splitlines():
            if "time=" in line or "time<" in line:
                try:
                    if "time=" in line:
                        time_str = line.split("time=")[1].split()[0].strip("ms")
                    else:
                        time_str = line.split("time<")[1].split()[0].strip("ms")
                    
                    times.append(float(time_str))
                except (IndexError, ValueError):
                    continue
        
        if times:
            packet_loss = 1 - (len(times) / count)
            return {
                "min": min(times) if times else None,
                "max": max(times) if times else None,
                "avg": statistics.mean(times) if times else None,
                "median": statistics.median(times) if times else None,
                "stdev": statistics.stdev(times) if len(times) > 1 else 0,
                "packet_loss": packet_loss,
                "jitter": max(times) - min(times) if len(times) > 1 else 0,
                "samples": len(times)
            }
        
        return None
    except subprocess.TimeoutExpired:
        return None
    except Exception as e:
        if RICH_AVAILABLE:
            console.print(f"[red]Error pinging {host}: {str(e)}[/red]")
        else:
            print(f"Error pinging {host}: {str(e)}")
        return None


def test_dns_server(server_name, server_ip, ping_count=10, timeout_ms=1000):
    try:
        sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        sock.settimeout(timeout_ms / 1000)
        result = sock.connect_ex((server_ip, 53))
        sock.close()
        
        if result != 0:
            return server_name, server_ip, None
        
        ping_results = ping(server_ip, ping_count, timeout_ms)
        return server_name, server_ip, ping_results
    except Exception as e:
        if RICH_AVAILABLE:
            console.print(f"[red]Error testing {server_name} ({server_ip}): {str(e)}[/red]")
        else:
            print(f"Error testing {server_name} ({server_ip}): {str(e)}")
        return server_name, server_ip, None


def test_all_dns_servers(dns_servers, settings):
    results = []
    ping_count = settings.get("ping_count", 10)
    timeout_ms = settings.get("timeout_ms", 1000)
    max_workers = min(settings.get("max_workers", 10), len(dns_servers))
    
    if RICH_AVAILABLE:
        with Progress(
            SpinnerColumn(),
            TextColumn("[bold cyan]{task.description}[/bold cyan]"),
            BarColumn(bar_width=None, style="cyan", complete_style="green"),
            TaskProgressColumn(),
            TimeRemainingColumn(),
            console=console,
            expand=True
        ) as progress:
            task = progress.add_task("Testing DNS servers...", total=len(dns_servers))
            
            with ThreadPoolExecutor(max_workers=max_workers) as executor:
                future_to_server = {executor.submit(test_dns_server, name, ip, ping_count, timeout_ms): (name, ip) 
                                   for name, ip in dns_servers.items()}
                
                for future in future_to_server:
                    name, ip, result = future.result()
                    results.append((name, ip, result))
                    progress.update(task, advance=1)
                    
            if len(results) > 0:
                progress.update(task, description="[success]Testing complete![/success]")
                time.sleep(0.5)
    else:
        print(f"Testing {len(dns_servers)} DNS servers...")
        
        with ThreadPoolExecutor(max_workers=max_workers) as executor:
            future_to_server = {executor.submit(test_dns_server, name, ip, ping_count, timeout_ms): (name, ip) 
                               for name, ip in dns_servers.items()}
            
            completed = 0
            for future in future_to_server:
                name, ip, result = future.result()
                results.append((name, ip, result))
                completed += 1
                print(f"Progress: {completed}/{len(dns_servers)}")
    
    return results


def display_results(results, settings):
    valid_results = [(name, ip, data) for name, ip, data in results if data is not None]
    sorted_results = sorted(valid_results, key=lambda x: (x[2]["avg"], x[2]["jitter"]))
    
    if RICH_AVAILABLE:
        table = Table(
            title="DNS Server Test Results", 
            caption="Sorted by Latency (Lower is Better)",
            box=ROUNDED,
            header_style="bold cyan",
            border_style="cyan",
            expand=True
        )
        
        table.add_column("Rank", justify="right", style="cyan", no_wrap=True, width=5)
        table.add_column("Provider", style="green")
        table.add_column("IP Address", style="blue")
        table.add_column("Avg (ms)", justify="right")
        table.add_column("Min (ms)", justify="right")
        table.add_column("Max (ms)", justify="right")
        table.add_column("Jitter", justify="right")
        table.add_column("Packet Loss", justify="right")
        
        for i, (name, ip, data) in enumerate(sorted_results, 1):
            packet_loss = f"{data['packet_loss']*100:.1f}%"
            
            if i <= 3:
                rank_style = "[gold]" if i == 1 else "[silver]" if i == 2 else "[bronze]"
                avg_style = "[bold green]" if i == 1 else "[green]" if i <= 3 else ""
                
                table.add_row(
                    f"{rank_style}{i}[/]",
                    f"{rank_style}{name}[/]",
                    ip,
                    f"{avg_style}{data['avg']:.2f}[/]",
                    f"{data['min']:.2f}",
                    f"{data['max']:.2f}",
                    f"{data['jitter']:.2f}",
                    packet_loss
                )
            else:
                if not settings.get("show_all_servers", True) and i > 5:
                    continue
                table.add_row(
                    str(i),
                    name,
                    ip,
                    f"{data['avg']:.2f}",
                    f"{data['min']:.2f}",
                    f"{data['max']:.2f}",
                    f"{data['jitter']:.2f}",
                    packet_loss
                )
        
        console.print(Panel.fit(
            table,
            title="[title]Results[/title]",
            border_style="cyan",
            padding=(1, 1)
        ))
        
        failed = [(name, ip) for name, ip, data in results if data is None]
        if failed:
            failed_table = Table(box=ROUNDED, border_style="red", header_style="bold red")
            failed_table.add_column("Provider", style="red")
            failed_table.add_column("IP Address", style="red")
            
            for name, ip in failed:
                failed_table.add_row(name, ip)
                
            console.print(Panel.fit(
                failed_table,
                title="[danger]Failed to Test[/danger]",
                border_style="red",
                padding=(1, 1)
            ))
    else:
        print("\nDNS Server Test Results (Sorted by Latency)")
        print("-" * 80)
        print(f"{'Rank':<5}{'Provider':<25}{'IP Address':<18}{'Avg (ms)':<10}{'Min (ms)':<10}{'Max (ms)':<10}{'Jitter':<10}{'Loss':<8}")
        print("-" * 80)
        
        for i, (name, ip, data) in enumerate(sorted_results, 1):
            if not settings.get("show_all_servers", True) and i > 5:
                continue
            packet_loss = f"{data['packet_loss']*100:.1f}%"
            print(f"{i:<5}{name:<25}{ip:<18}{data['avg']:<10.2f}{data['min']:<10.2f}{data['max']:<10.2f}{data['jitter']:<10.2f}{packet_loss:<8}")
        
        failed = [(name, ip) for name, ip, data in results if data is None]
        if failed:
            print("\nFailed to test these servers:")
            for name, ip in failed:
                print(f"• {name} ({ip})")


def recommend_dns(results):
    valid_results = [(name, ip, data) for name, ip, data in results if data is not None]
    
    if not valid_results:
        if RICH_AVAILABLE:
            console.print("[bold red]No valid DNS server results to make recommendations.[/bold red]")
        else:
            print("\nNo valid DNS server results to make recommendations.")
        return
    
    sorted_results = sorted(valid_results, key=lambda x: (x[2]["avg"], x[2]["jitter"]))
    best_name, best_ip, best_data = sorted_results[0]
    best_provider = best_name.split()[0]
    
    secondary = None
    for name, ip, data in sorted_results[1:]:
        current_provider = name.split()[0]
        if current_provider != best_provider:
            secondary = (name, ip, data)
            break
    
    if secondary is None and len(sorted_results) > 1:
        secondary = sorted_results[1]
    
    if RICH_AVAILABLE:
        recommendation = []
        recommendation.append(f"[success]Primary DNS:[/success] {best_ip} ({best_name})")
        
        if secondary:
            sec_name, sec_ip, _ = secondary
            recommendation.append(f"[success]Secondary DNS:[/success] {sec_ip} ({sec_name})")
        
        recommendation.append("")
        recommendation.append("[info]Note: Using DNS servers with low latency and jitter can help reduce lag in gaming.[/info]")
        
        console.print(Panel(
            "\n".join(recommendation),
            title="[title]Recommended DNS Configuration for Gaming[/title]",
            border_style="green",
            box=HEAVY,
            padding=(1, 2)
        ))
    else:
        print("\nRecommended DNS Configuration for Gaming:")
        print(f"Primary DNS: {best_ip} ({best_name})")
        
        if secondary:
            sec_name, sec_ip, _ = secondary
            print(f"Secondary DNS: {sec_ip} ({sec_name})")
        
        print("\nNote: Using DNS servers with low latency and jitter can help reduce lag in gaming.")


def settings_menu():
    if not RICH_AVAILABLE:
        print("Settings menu requires the rich library. Please install it with: pip install rich")
        return None
    
    settings = load_settings()
    
    while True:
        console.clear()
        print_header()
        
        console.print("[title]Settings Menu[/title]\n")
        
        console.print("[menu]1.[/menu] Ping Count: [highlight]{}[/highlight]".format(settings["ping_count"]))
        console.print("[menu]2.[/menu] Timeout (ms): [highlight]{}[/highlight]".format(settings["timeout_ms"]))
        console.print("[menu]3.[/menu] Max Workers: [highlight]{}[/highlight]".format(settings["max_workers"]))
        console.print("[menu]4.[/menu] Show All Servers: [highlight]{}[/highlight]".format("Yes" if settings["show_all_servers"] else "No"))
        console.print("[menu]5.[/menu] Manage Custom DNS Servers")
        console.print("[menu]6.[/menu] Save Settings")
        console.print("[menu]7.[/menu] Reset to Defaults")
        console.print("[menu]0.[/menu] Return to Main Menu\n")
        
        choice = Prompt.ask("Select an option", choices=["0", "1", "2", "3", "4", "5", "6", "7"], default="0")
        
        if choice == "0":
            return settings
        elif choice == "1":
            ping_count = Prompt.ask("Enter ping count", default=str(settings["ping_count"]))
            try:
                settings["ping_count"] = int(ping_count)
            except ValueError:
                console.print("[danger]Invalid value. Using previous value.[/danger]")
                time.sleep(1)
        elif choice == "2":
            timeout = Prompt.ask("Enter timeout in milliseconds", default=str(settings["timeout_ms"]))
            try:
                settings["timeout_ms"] = int(timeout)
            except ValueError:
                console.print("[danger]Invalid value. Using previous value.[/danger]")
                time.sleep(1)
        elif choice == "3":
            workers = Prompt.ask("Enter maximum number of workers", default=str(settings["max_workers"]))
            try:
                settings["max_workers"] = int(workers)
            except ValueError:
                console.print("[danger]Invalid value. Using previous value.[/danger]")
                time.sleep(1)
        elif choice == "4":
            settings["show_all_servers"] = not settings["show_all_servers"]
        elif choice == "5":
            manage_custom_dns(settings)
        elif choice == "6":
            if save_settings(settings):
                console.print("[success]Settings saved successfully![/success]")
            else:
                console.print("[danger]Failed to save settings![/danger]")
            time.sleep(1)
        elif choice == "7":
            if Confirm.ask("Are you sure you want to reset all settings to defaults?"):
                settings = DEFAULT_SETTINGS.copy()
                console.print("[success]Settings reset to defaults![/success]")
                time.sleep(1)
    
    return settings


def manage_custom_dns(settings):
    if not RICH_AVAILABLE:
        print("Custom DNS management requires the rich library. Please install it with: pip install rich")
        return
    
    while True:
        console.clear()
        console.print("[title]Manage Custom DNS Servers[/title]\n")
        
        if not settings.get("custom_dns_servers"):
            settings["custom_dns_servers"] = {}
        
        if settings["custom_dns_servers"]:
            table = Table(box=ROUNDED)
            table.add_column("Name")
            table.add_column("IP Address")
            
            for name, ip in settings["custom_dns_servers"].items():
                table.add_row(name, ip)
            
            console.print(table)
        else:
            console.print("[info]No custom DNS servers configured.[/info]\n")
        
        console.print("[menu]1.[/menu] Add Custom DNS Server")
        console.print("[menu]2.[/menu] Remove Custom DNS Server")
        console.print("[menu]0.[/menu] Back to Settings\n")
        
        choice = Prompt.ask("Select an option", choices=["0", "1", "2"], default="0")
        
        if choice == "0":
            break
        elif choice == "1":
            name = Prompt.ask("Enter DNS server name")
            if not name:
                continue
                
            ip = Prompt.ask("Enter DNS server IP address")
            if not ip:
                continue
                
            settings["custom_dns_servers"][name] = ip
            console.print(f"[success]Added {name} ({ip})[/success]")
            time.sleep(1)
        elif choice == "2":
            if not settings["custom_dns_servers"]:
                console.print("[warning]No custom DNS servers to remove.[/warning]")
                time.sleep(1)
                continue
                
            names = list(settings["custom_dns_servers"].keys())
            choices = [str(i) for i in range(len(names))]
            
            for i, name in enumerate(names):
                console.print(f"[menu]{i}.[/menu] {name} ({settings['custom_dns_servers'][name]})")
                
            idx = Prompt.ask("Select server to remove", choices=choices)
            name_to_remove = names[int(idx)]
            
            if Confirm.ask(f"Are you sure you want to remove {name_to_remove}?"):
                del settings["custom_dns_servers"][name_to_remove]
                console.print(f"[success]Removed {name_to_remove}[/success]")
                time.sleep(1)


def main_menu():
    if not RICH_AVAILABLE:
        return None
    
    settings = load_settings()
    
    while True:
        console.clear()
        print_header()
        
        console.print("[title]Main Menu[/title]\n")
        console.print("[menu]1.[/menu] Run DNS Test")
        console.print("[menu]2.[/menu] Settings")
        console.print("[menu]0.[/menu] Exit\n")
        
        choice = Prompt.ask("Select an option", choices=["0", "1", "2"], default="1")
        
        if choice == "0":
            return None
        elif choice == "1":
            return settings
        elif choice == "2":
            settings = settings_menu()


def main():
    try:
        settings = None
        
        if RICH_AVAILABLE:
            settings = main_menu()
            if settings is None:
                sys.exit(0)
        else:
            settings = load_settings()
        
        print_header()
        
        if not is_admin():
            if RICH_AVAILABLE:
                console.print("[warning]Warning: This script may work better with administrator privileges.[/warning]")
            else:
                print("Warning: This script may work better with administrator privileges.")
        
        dns_servers = get_dns_servers(settings)
        results = test_all_dns_servers(dns_servers, settings)
        display_results(results, settings)
        recommend_dns(results)
        
        if RICH_AVAILABLE:
            console.print("\n[button]Press Enter to exit[/button]")
            input()
        
    except KeyboardInterrupt:
        if RICH_AVAILABLE:
            console.print("\n[bold red]Test interrupted by user.[/bold red]")
        else:
            print("\nTest interrupted by user.")
        sys.exit(1)
    except Exception as e:
        if RICH_AVAILABLE:
            console.print(f"\n[bold red]An error occurred: {str(e)}[/bold red]")
            import traceback
            console.print(f"[dim]{traceback.format_exc()}[/dim]")
        else:
            print(f"\nAn error occurred: {str(e)}")
            import traceback
            print(traceback.format_exc())
        sys.exit(1)


if __name__ == "__main__":
    main()
