import socket
from concurrent.futures import ThreadPoolExecutor, as_completed

def scan_ports(target_ip, ports, threat_manager=None):
    open_ports = []
    print(f"🔍 Scanning {len(ports)} ports on {target_ip}...")

    def scan_single_port(port):
        s = socket.socket()
        s.settimeout(0.5)
        try:
            s.connect((target_ip, port))
            service = get_basic_service_name(port)
            if threat_manager:
                additional_info = {
                    'scan_method': 'socket_connect',
                    'response_time': 'fast',
                    'suspicious': is_suspicious_port(port)
                }
                threat_manager.process_scan_result(
                    ip=target_ip,
                    port=port,
                    service=service,
                    is_open=True,
                    additional_info=additional_info
                )
            print(f"✅ Port {port} open - {service}")
            return port
        except:
            return None
        finally:
            s.close()

    with ThreadPoolExecutor(max_workers=100) as executor:
        futures = [executor.submit(scan_single_port, port) for port in ports]
        for i, future in enumerate(as_completed(futures), 1):
            result = future.result()
            if result:
                open_ports.append(result)

            if i % 1000 == 0 or i == len(ports):
                print(f"📊 Progress: {i}/{len(ports)} ports scanned")

    return open_ports

def get_basic_service_name(port):
    common_services = {
        21: "FTP", 22: "SSH", 23: "Telnet", 25: "SMTP", 53: "DNS",
        80: "HTTP", 110: "POP3", 135: "RPC", 139: "NetBIOS", 143: "IMAP",
        443: "HTTPS", 445: "SMB", 993: "IMAPS", 995: "POP3S", 1433: "MS-SQL",
        1521: "Oracle", 3306: "MySQL", 3389: "RDP", 5432: "PostgreSQL", 5900: "VNC"
    }
    return common_services.get(port, f"Unknown-{port}")

def is_suspicious_port(port):
    suspicious_ports = [21, 22, 23, 135, 139, 445, 1433, 1521, 3306, 3389, 5900]
    return port in suspicious_ports

# 💡 NEW FUNCTION REQUIRED BY YOUR MAIN SCRIPT
def perform_scan(target_ip, ports, threat_manager=None):
    """
    Wrapper function to match external import calls
    """
    return scan_ports(target_ip, ports, threat_manager)
