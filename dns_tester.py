import socket
import subprocess
import platform
import statistics
import time
import sys
import os
import argparse
from datetime import datetime
from typing import Dict, List, Tuple, Optional

VERSION = "1.0.0"

class Colors:
    HEADER = '\033[95m'
    BLUE = '\033[94m'
    CYAN = '\033[96m'
    GREEN = '\033[92m'
    YELLOW = '\033[93m'
    RED = '\033[91m'
    ENDC = '\033[0m'
    BOLD = '\033[1m'
    UNDERLINE = '\033[4m'
    BACKGROUND_BLUE = '\033[44m'
    BACKGROUND_GREEN = '\033[42m'
    BACKGROUND_YELLOW = '\033[43m'
    BACKGROUND_RED = '\033[41m'

DNS_SERVERS = {
    'Google': ['8.8.8.8', '8.8.4.4'],
    'Cloudflare': ['1.1.1.1', '1.0.0.1'],
    'OpenDNS': ['208.67.222.222', '208.67.220.220'],
    'Quad9': ['9.9.9.9', '149.112.112.112'],
    'AdGuard': ['94.140.14.14', '94.140.15.15'],
    'CleanBrowsing': ['185.228.168.9', '185.228.169.9'],
    'Comodo Secure': ['8.26.56.26', '8.20.247.20'],
    'Level3': ['4.2.2.1', '4.2.2.2'],
    'Norton Connect': ['199.85.126.10', '199.85.127.10'],
    'Verisign': ['64.6.64.6', '64.6.65.6']
}

DEFAULT_PING_COUNT = 10
DEFAULT_TIMEOUT = 1000  # ms

def is_admin() -> bool:
    """Check if the script is running with administrator privileges"""
    try:
        if platform.system() == 'Windows':
            return ctypes.windll.shell32.IsUserAnAdmin() != 0
        else:
            return os.geteuid() == 0
    except:
        return False

def clear_screen() -> None:
    """Clear the terminal screen based on the operating system"""
    os.system('cls' if platform.system() == 'Windows' else 'clear')

def print_header() -> None:
    """Print the application header"""
    clear_screen()
    width = 90
    print(f"{Colors.BACKGROUND_BLUE}{Colors.BOLD}{' ' * width}{Colors.ENDC}")
    print(f"{Colors.BACKGROUND_BLUE}{Colors.BOLD}{'DNS TESTER':^{width}}{Colors.ENDC}")
    print(f"{Colors.BACKGROUND_BLUE}{Colors.BOLD}{'Find the fastest DNS servers for optimal gaming experience':^{width}}{Colors.ENDC}")
    print(f"{Colors.BACKGROUND_BLUE}{Colors.BOLD}{f'v{VERSION}':^{width}}{Colors.ENDC}")
    print(f"{Colors.BACKGROUND_BLUE}{Colors.BOLD}{' ' * width}{Colors.ENDC}")
    print(f"{Colors.CYAN}Copyright © {datetime.now().year} Ice - https://github.com/ice-exe{Colors.ENDC}\n")

def print_progress_bar(progress: int, total: int, prefix: str = '', suffix: str = '', length: int = 50) -> None:
    """Print a progress bar"""
    filled_length = int(length * progress // total)
    bar = '█' * filled_length + '░' * (length - filled_length)
    percentage = f"{100 * (progress / float(total)):.1f}"
    
    if progress / total < 0.3:
        color = Colors.RED
    elif progress / total < 0.6:
        color = Colors.YELLOW
    elif progress / total < 0.9:
        color = Colors.CYAN
    else:
        color = Colors.GREEN
    
    print(f"\r{prefix} {color}|{bar}| {percentage}%{Colors.ENDC} {suffix}", end='\r')
    if progress == total:
        print()

def ping(host: str, count: int = 10, timeout: int = 1000) -> Tuple[Optional[float], Optional[float], Optional[float], int]:
    """Ping a host and return statistics"""
    try:
        param = '-n' if platform.system().lower() == 'windows' else '-c'
        timeout_param = '-w' if platform.system().lower() == 'windows' else '-W'
        timeout_value = str(timeout) if platform.system().lower() == 'windows' else str(timeout // 1000)
        
        command = ['ping', param, str(count), timeout_param, timeout_value, host]
        
        result = subprocess.run(command, text=True, capture_output=True, check=False)
        
        if result.returncode != 0:
            return None, None, None, 0
        
        output = result.stdout
        
        times = []
        packet_loss = 100  # Default to 100% loss
        
        if platform.system().lower() == 'windows':
            for line in output.splitlines():
                if 'time=' in line or 'time<' in line:
                    try:
                        time_str = line.split('time=')[1].split('ms')[0].strip() if 'time=' in line else '1'  # time<1ms case
                        times.append(float(time_str))
                    except (IndexError, ValueError):
                        pass
                if 'Lost = ' in line:
                    try:
                        loss_str = line.split('Lost = ')[1].split('(')[0].strip()
                        packet_loss = int(loss_str) * 100 // count
                    except (IndexError, ValueError):
                        pass
        else:  
            for line in output.splitlines():
                if 'time=' in line:
                    try:
                        time_str = line.split('time=')[1].split(' ms')[0].strip()
                        times.append(float(time_str))
                    except (IndexError, ValueError):
                        pass
                if 'packet loss' in line:
                    try:
                        loss_str = line.split('%')[0].split(' ')[-1].strip()
                        packet_loss = int(loss_str)
                    except (IndexError, ValueError):
                        pass
        
        if not times:
            return None, None, None, packet_loss
        
        avg_time = statistics.mean(times)
        min_time = min(times)
        jitter = statistics.stdev(times) if len(times) > 1 else 0
        
        return avg_time, min_time, jitter, packet_loss
    
    except Exception as e:
        print(f"\n{Colors.RED}Error pinging {host}: {str(e)}{Colors.ENDC}")
        return None, None, None, 100

def dns_lookup_test(dns_server: str, domains: List[str], timeout: int = 1000) -> Tuple[float, int]:
    """Test DNS lookup speed for a list of domains"""
    resolver = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    resolver.settimeout(timeout / 1000) 
    
    total_time = 0
    successful = 0
    
    for domain in domains:
        try:
            query_packet = b'\x00\x00\x01\x00\x00\x01\x00\x00\x00\x00\x00\x00'
            
            parts = domain.split('.')
            for part in parts:
                query_packet += bytes([len(part)]) + part.encode()
            
            query_packet += b'\x00\x00\x01\x00\x01'
            
            start_time = time.time()
            resolver.sendto(query_packet, (dns_server, 53))
            resolver.recvfrom(512)
            end_time = time.time()
            
            total_time += (end_time - start_time) * 1000  
            successful += 1
        except Exception:
            pass
    
    resolver.close()
    
    if successful == 0:
        return 0, 0
    
    return total_time / successful, (successful * 100) // len(domains)

def test_dns_servers(dns_servers: Dict[str, List[str]], ping_count: int = 10, timeout: int = 1000) -> List[Dict]:
    """Test all DNS servers and return results"""
    results = []
    popular_domains = ['google.com', 'youtube.com', 'facebook.com', 'amazon.com', 'netflix.com']
    
    total_servers = sum(len(servers) for servers in dns_servers.values())
    current = 0
    
    print(f"{Colors.CYAN}Testing DNS servers with {Colors.BOLD}{ping_count}{Colors.ENDC}{Colors.CYAN} pings per server...{Colors.ENDC}\n")
    
    for provider, servers in dns_servers.items():
        for server in servers:
            current += 1
            progress = current * 100 // total_servers
            
            # Print progress bar
            print_progress_bar(
                current, total_servers,
                prefix=f"{Colors.CYAN}Testing {Colors.BOLD}{server}{Colors.ENDC}{Colors.CYAN} ({provider}){Colors.ENDC}",
                suffix=f"{current}/{total_servers} servers",
                length=40
            )
            
            avg_time, min_time, jitter, packet_loss = ping(server, ping_count, timeout)
            dns_speed, dns_reliability = dns_lookup_test(server, popular_domains, timeout)
            
            results.append({
                'provider': provider,
                'server': server,
                'avg_ping': avg_time,
                'min_ping': min_time,
                'jitter': jitter,
                'packet_loss': packet_loss,
                'dns_speed': dns_speed,
                'dns_reliability': dns_reliability
            })
    
    print()  
    return results

def calculate_gaming_score(result: Dict) -> float:
    """Calculate a gaming suitability score (lower is better)"""
    if result['avg_ping'] is None or result['packet_loss'] >= 5:
        return float('inf')
    

    ping_score = result['min_ping'] * 0.4 if result['min_ping'] is not None else 100
    jitter_score = result['jitter'] * 3 * 0.3 if result['jitter'] is not None else 30
    packet_loss_score = result['packet_loss'] * 2 * 0.2
    dns_speed_score = result['dns_speed'] * 0.1 if result['dns_speed'] > 0 else 10
    
    return ping_score + jitter_score + packet_loss_score + dns_speed_score

def print_results(results: List[Dict]) -> None:
    """Print the test results in a formatted table"""
    
    for result in results:
        result['gaming_score'] = calculate_gaming_score(result)
    
    sorted_results = sorted(results, key=lambda x: x['gaming_score'])
    
    width = 100
    print(f"\n{Colors.BOLD}{'=' * width}{Colors.ENDC}")
    header = f"{Colors.BOLD}{Colors.BACKGROUND_BLUE}{'PROVIDER':<15} {'SERVER':<15} {'AVG PING':<10} {'MIN PING':<10} {'JITTER':<10} {'PACKET LOSS':<12} {'DNS SPEED':<10} {'SCORE':<10}{Colors.ENDC}"
    print(header)
    print(f"{Colors.BOLD}{'-' * width}{Colors.ENDC}")
    
    for result in sorted_results:
        if result['gaming_score'] == float('inf'):
            continue  
        
        if result['avg_ping'] is None:
            color = Colors.RED
        elif result['avg_ping'] < 20:
            color = Colors.GREEN
        elif result['avg_ping'] < 50:
            color = Colors.CYAN
        elif result['avg_ping'] < 100:
            color = Colors.YELLOW
        else:
            color = Colors.RED
        
        print(f"{color}{result['provider']:<15} {result['server']:<15} ", end="")
        
        if result['avg_ping'] is not None:
            print(f"{result['avg_ping']:<10.1f} {result['min_ping']:<10.1f} {result['jitter']:<10.2f} ", end="")
        else:
            print(f"{'N/A':<10} {'N/A':<10} {'N/A':<10} ", end="")
        
        if result['packet_loss'] == 0:
            print(f"{Colors.GREEN}{result['packet_loss']}%{color:<10} ", end="")
        elif result['packet_loss'] < 2:
            print(f"{Colors.YELLOW}{result['packet_loss']}%{color:<10} ", end="")
        else:
            print(f"{Colors.RED}{result['packet_loss']}%{color:<10} ", end="")
        

        print(f"{result['dns_speed']:<10.2f} {result['gaming_score']:<10.2f}{Colors.ENDC}")
    
    print(f"{Colors.BOLD}{'=' * width}{Colors.ENDC}\n")

def print_recommendations(results: List[Dict]) -> None:
    """Print DNS recommendations based on test results"""
    valid_results = [r for r in results if r['gaming_score'] != float('inf')]
    
    if not valid_results:
        print(f"{Colors.RED}No suitable DNS servers found. Please check your internet connection.{Colors.ENDC}")
        return
    
    sorted_results = sorted(valid_results, key=lambda x: x['gaming_score'])[:3]
    
    print(f"{Colors.GREEN}{Colors.BOLD}{Colors.BACKGROUND_GREEN} RECOMMENDATIONS FOR GAMING {Colors.ENDC}")
    print(f"{Colors.CYAN}Based on ping time, jitter, packet loss, and DNS lookup speed:{Colors.ENDC}\n")
    
    for i, result in enumerate(sorted_results, 1):
        print(f"{Colors.BOLD}{i}. {result['provider']} ({result['server']}){Colors.ENDC}")
        print(f"   Ping: {Colors.CYAN}{result['min_ping']:.1f}ms{Colors.ENDC} | ", end="")
        print(f"Jitter: {Colors.CYAN}{result['jitter']:.2f}ms{Colors.ENDC} | ", end="")
        print(f"Packet Loss: {Colors.CYAN}{result['packet_loss']}%{Colors.ENDC} | ", end="")
        print(f"DNS Speed: {Colors.CYAN}{result['dns_speed']:.2f}ms{Colors.ENDC}")
        print(f"   Gaming Score: {Colors.GREEN}{result['gaming_score']:.2f}{Colors.ENDC} (lower is better)\n")
    
    print(f"{Colors.YELLOW}{Colors.BOLD}HOW TO CHANGE YOUR DNS SETTINGS:{Colors.ENDC}")
    print(f"1. {Colors.CYAN}Windows:{Colors.ENDC} Control Panel > Network and Internet > Network Connections > Right-click your connection > Properties > IPv4 > Properties")
    print(f"2. {Colors.CYAN}macOS:{Colors.ENDC} System Preferences > Network > Advanced > DNS")
    print(f"3. {Colors.CYAN}Linux:{Colors.ENDC} Edit /etc/resolv.conf or use Network Manager\n")

def parse_arguments():
    """Parse command line arguments"""
    parser = argparse.ArgumentParser(description='DNS Tester - Find the fastest DNS servers for gaming')
    parser.add_argument('-p', '--pings', type=int, default=DEFAULT_PING_COUNT,
                        help=f'Number of pings per server (default: {DEFAULT_PING_COUNT})')
    parser.add_argument('-t', '--timeout', type=int, default=DEFAULT_TIMEOUT,
                        help=f'Timeout in milliseconds (default: {DEFAULT_TIMEOUT}ms)')
    parser.add_argument('-v', '--version', action='version', version=f'DNS Tester v{VERSION}')
    
    return parser.parse_args()

def show_menu() -> int:
    """Show the main menu and return the user's choice"""
    print(f"{Colors.BOLD}{Colors.CYAN}===== DNS TESTER MENU ====={Colors.ENDC}")
    print(f"1. {Colors.GREEN}Run DNS Tests{Colors.ENDC}")
    print(f"2. {Colors.YELLOW}Configure Test Settings{Colors.ENDC}")
    print(f"3. {Colors.CYAN}About{Colors.ENDC}")
    print(f"4. {Colors.RED}Exit{Colors.ENDC}")
    
    while True:
        try:
            choice = int(input(f"\n{Colors.BOLD}Enter your choice (1-4): {Colors.ENDC}"))
            if 1 <= choice <= 4:
                return choice
            else:
                print(f"{Colors.RED}Invalid choice. Please enter a number between 1 and 4.{Colors.ENDC}")
        except ValueError:
            print(f"{Colors.RED}Invalid input. Please enter a number.{Colors.ENDC}")

def configure_settings(ping_count: int, timeout: int) -> Tuple[int, int]:
    """Configure test settings and return new values"""
    clear_screen()
    print(f"{Colors.BOLD}{Colors.YELLOW}===== CONFIGURE TEST SETTINGS ====={Colors.ENDC}\n")
    
    print(f"Current settings:\n")
    print(f"1. Pings per server: {Colors.CYAN}{ping_count}{Colors.ENDC}")
    print(f"2. Timeout: {Colors.CYAN}{timeout}ms{Colors.ENDC}")
    print(f"3. {Colors.GREEN}Return to main menu{Colors.ENDC}")
    
    while True:
        try:
            choice = int(input(f"\n{Colors.BOLD}Enter your choice (1-3): {Colors.ENDC}"))
            
            if choice == 1:
                new_ping_count = int(input(f"Enter new ping count (5-100): "))
                if 5 <= new_ping_count <= 100:
                    ping_count = new_ping_count
                    print(f"{Colors.GREEN}Ping count updated to {ping_count}{Colors.ENDC}")
                else:
                    print(f"{Colors.RED}Invalid value. Ping count must be between 5 and 100.{Colors.ENDC}")
            
            elif choice == 2:
                new_timeout = int(input(f"Enter new timeout in milliseconds (500-5000): "))
                if 500 <= new_timeout <= 5000:
                    timeout = new_timeout
                    print(f"{Colors.GREEN}Timeout updated to {timeout}ms{Colors.ENDC}")
                else:
                    print(f"{Colors.RED}Invalid value. Timeout must be between 500 and 5000 ms.{Colors.ENDC}")
            
            elif choice == 3:
                break
            
            else:
                print(f"{Colors.RED}Invalid choice. Please enter a number between 1 and 3.{Colors.ENDC}")
        
        except ValueError:
            print(f"{Colors.RED}Invalid input. Please enter a number.{Colors.ENDC}")
    
    return ping_count, timeout

def show_about():
    """Show information about the application"""
    clear_screen()
    print(f"{Colors.BOLD}{Colors.CYAN}===== ABOUT DNS TESTER ====={Colors.ENDC}\n")
    print(f"DNS Tester v{VERSION}")
    print(f"Copyright © {datetime.now().year} Ice - https://github.com/ice-exe\n")
    
    print(f"{Colors.BOLD}Description:{Colors.ENDC}")
    print("DNS Tester is a tool designed to help gamers find the fastest and most reliable DNS servers")
    print("for optimal gaming experience. It tests multiple popular public DNS servers and provides")
    print("recommendations based on ping time, jitter, packet loss, and DNS lookup speed.\n")
    
    print(f"{Colors.BOLD}Features:{Colors.ENDC}")
    print("- Tests multiple popular public DNS servers")
    print("- Measures key performance metrics")
    print("- Calculates a gaming suitability score")
    print("- Provides color-coded results")
    print("- Offers recommendations for the best DNS servers\n")
    
    input(f"{Colors.GREEN}Press Enter to return to the main menu...{Colors.ENDC}")

def main() -> None:
    """Main function"""
    try:
        args = parse_arguments()
        ping_count = args.pings
        timeout = args.timeout
        
        while True:
            print_header()
            
            if not is_admin():
                print(f"{Colors.YELLOW}Warning: Running without administrator privileges may affect results.{Colors.ENDC}\n")
            
            choice = show_menu()
            
            if choice == 1:  
                clear_screen()
                print_header()
                
                results = test_dns_servers(DNS_SERVERS, ping_count, timeout)
                
                print_results(results)
                
                print_recommendations(results)
                
                input(f"\n{Colors.GREEN}Press Enter to return to the main menu...{Colors.ENDC}")
            
            elif choice == 2:  
                ping_count, timeout = configure_settings(ping_count, timeout)
            
            elif choice == 3:  
                show_about()
            
            elif choice == 4:  
                break
    
    except KeyboardInterrupt:
        print(f"\n\n{Colors.YELLOW}Test interrupted by user.{Colors.ENDC}")
    except Exception as e:
        print(f"\n{Colors.RED}An error occurred: {str(e)}{Colors.ENDC}")
    finally:
        clear_screen()
        print_header()
        print(f"\n{Colors.CYAN}Thank you for using DNS Tester!{Colors.ENDC}")
        time.sleep(1.5)

if __name__ == "__main__":
    if platform.system() == 'Windows':
        import ctypes
    main()