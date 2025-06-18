    #!/usr/bin/env python3
"""
Threat Manager - Integrates port scanner with IDS/IPS systems
Handles automatic blocking and alerting for detected threats
"""

import syslog
import subprocess
import json
import sqlite3
import os
from datetime import datetime
from typing import Dict, List, Optional

class ThreatManager:
    def __init__(self, config_path: str = None):
        """Initialize threat manager with configuration"""
        self.setup_logging()
        self.blocked_ips = set()
        self.threat_db_path = "/tmp/threats.db"
        self.setup_database()
        
        # Risk levels for different services
        self.high_risk_ports = [21, 22, 23, 135, 139, 445, 1433, 1521, 3306, 3389, 5432, 5900]
        self.medium_risk_ports = [25, 53, 80, 110, 143, 443, 993, 995]
        
    def setup_logging(self):
        """Setup syslog for threat logging"""
        syslog.openlog("smart_port_scanner", syslog.LOG_PID, syslog.LOG_LOCAL0)
        
    def setup_database(self):
        """Create threat tracking database"""
        conn = sqlite3.connect(self.threat_db_path)
        cursor = conn.cursor()
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS threats (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                ip TEXT,
                port INTEGER,
                service TEXT,
                severity TEXT,
                timestamp DATETIME DEFAULT CURRENT_TIMESTAMP,
                action_taken TEXT,
                blocked BOOLEAN DEFAULT FALSE
            )
        ''')
        conn.commit()
        conn.close()
        
    def assess_threat_level(self, port: int, service: str, additional_info: Dict = None) -> str:
        """Assess threat level based on port, service, and additional info"""
        if port in self.high_risk_ports:
            return "high"
        elif port in self.medium_risk_ports:
            return "medium"
        elif service and any(dangerous in service.lower() for dangerous in 
                           ['telnet', 'ftp', 'ssh', 'rdp', 'vnc', 'mysql', 'postgres']):
            return "high"
        else:
            return "low"
            
    def log_threat(self, ip: str, port: int, service: str, severity: str, 
                   additional_info: Dict = None) -> None:
        """Log threat to database and syslog"""
        # Log to database
        conn = sqlite3.connect(self.threat_db_path)
        cursor = conn.cursor()
        cursor.execute('''
            INSERT INTO threats (ip, port, service, severity, action_taken)
            VALUES (?, ?, ?, ?, ?)
        ''', (ip, port, service, severity, "logged"))
        conn.commit()
        conn.close()
        
        # Log to syslog for fail2ban
        message = f"THREAT_DETECTED ip={ip} port={port} service={service} severity={severity}"
        if additional_info:
            message += f" info={json.dumps(additional_info)}"
            
        if severity == "high":
            syslog.syslog(syslog.LOG_ALERT, message)
        elif severity == "medium":
            syslog.syslog(syslog.LOG_WARNING, message)
        else:
            syslog.syslog(syslog.LOG_INFO, message)
            
    def block_ip(self, ip: str, reason: str) -> bool:
        """Block IP using iptables"""
        if ip in self.blocked_ips:
            print(f" {ip} already blocked")
            return True
            
        try:
            # Add iptables rule
            cmd = f"sudo iptables -I INPUT -s {ip} -j DROP"
            result = subprocess.run(cmd.split(), check=True, capture_output=True, text=True)
            
            self.blocked_ips.add(ip)
            
            # Update database
            conn = sqlite3.connect(self.threat_db_path)
            cursor = conn.cursor()
            cursor.execute('''
                UPDATE threats SET blocked = TRUE, action_taken = ? 
                WHERE ip = ? AND blocked = FALSE
            ''', (f"BLOCKED: {reason}", ip))
            conn.commit()
            conn.close()
            
            # Log the block
            syslog.syslog(syslog.LOG_ALERT, f"IP_BLOCKED ip={ip} reason={reason}")
            print(f" BLOCKED: {ip} - {reason}")
            return True
            
        except subprocess.CalledProcessError as e:
            print(f" Failed to block {ip}: {e}")
            syslog.syslog(syslog.LOG_ERR, f"BLOCK_FAILED ip={ip} error={str(e)}")
            return False
            
    def process_scan_result(self, ip: str, port: int, service: str = "unknown", 
                           is_open: bool = True, additional_info: Dict = None) -> None:
        """Process a single scan result and take appropriate action"""
        if not is_open:
            return
            
        severity = self.assess_threat_level(port, service, additional_info)
        
        # Always log the threat
        self.log_threat(ip, port, service, severity, additional_info)
        
        # Print to console (maintaining your plaintext output)
        threat_emoji = {"high": "🔴", "medium": "🟡", "low": "🟢"}
        print(f"{threat_emoji[severity]} [{severity.upper()}] {ip}:{port} - {service}")
        
        # Auto-block high severity threats
        if severity == "high":
            reason = f"High-risk service detected: {service} on port {port}"
            self.block_ip(ip, reason)
        elif severity == "medium" and additional_info and additional_info.get('suspicious', False):
            reason = f"Suspicious activity: {service} on port {port}"
            self.block_ip(ip, reason)
            
    def get_threat_summary(self) -> Dict:
        """Get summary of detected threats"""
        conn = sqlite3.connect(self.threat_db_path)
        cursor = conn.cursor()
        
        # Get counts by severity
        cursor.execute('''
            SELECT severity, COUNT(*) FROM threats 
            GROUP BY severity
        ''')
        severity_counts = dict(cursor.fetchall())
        
        # Get blocked IPs count
        cursor.execute('SELECT COUNT(DISTINCT ip) FROM threats WHERE blocked = TRUE')
        blocked_count = cursor.fetchone()[0]
        
        # Get recent threats
        cursor.execute('''
            SELECT ip, port, service, severity, timestamp 
            FROM threats 
            ORDER BY timestamp DESC 
            LIMIT 10
        ''')
        recent_threats = cursor.fetchall()
        
        conn.close()
        
        return {
            'severity_counts': severity_counts,
            'blocked_ips': blocked_count,
            'recent_threats': recent_threats,
            'total_blocked_ips': len(self.blocked_ips)
        }
        
    def unblock_ip(self, ip: str) -> bool:
        """Unblock an IP address"""
        try:
            cmd = f"sudo iptables -D INPUT -s {ip} -j DROP"
            subprocess.run(cmd.split(), check=True)
            
            if ip in self.blocked_ips:
                self.blocked_ips.remove(ip)
                
            print(f" UNBLOCKED: {ip}")
            syslog.syslog(syslog.LOG_INFO, f"IP_UNBLOCKED ip={ip}")
            return True
            
        except subprocess.CalledProcessError as e:
            print(f" Failed to unblock {ip}: {e}")
            return False
            
    def cleanup(self):
        """Cleanup resources"""
        syslog.closelog()







class ThreatMonitor:
    """Real-time threat monitoring display"""
    
    def __init__(self, threat_manager: ThreatManager):
        self.threat_manager = threat_manager
        
    def display_live_threats(self):
        """Display live threat monitoring"""
        print("=" * 60)
        print("  SMART PORT SCANNER - THREAT MONITOR")
        print("=" * 60)
        
        try:
            while True:
                os.system('clear')  # Clear screen
                print(" LIVE THREAT MONITORING ")
                print("-" * 40)
                
                summary = self.threat_manager.get_threat_summary()
                
                print(f" Threat Summary:")
                for severity, count in summary['severity_counts'].items():
                    emoji = {"high": "🔴", "medium": "🟡", "low": "🟢"}.get(severity, "⚪")
                    print(f"   {emoji} {severity.title()}: {count}")
                    
                print(f"\n Blocked IPs: {summary['blocked_ips']}")
                
                print(f"\n Recent Threats:")
                for threat in summary['recent_threats'][:5]:
                    ip, port, service, severity, timestamp = threat
                    emoji = {"high": "🔴", "medium": "🟡", "low": "🟢"}.get(severity, "⚪")
                    print(f"   {emoji} {ip}:{port} - {service} ({timestamp})")
                
                print(f"\n Last Update: {datetime.now().strftime('%H:%M:%S')}")
                print("Press Ctrl+C to exit")
                
                import time
                time.sleep(2)
                
        except KeyboardInterrupt:
            print("\n Threat monitoring stopped")


if __name__ == "__main__":
    # Test the threat manager
    tm = ThreatManager()
    
    # Simulate some threats
    tm.process_scan_result("192.168.1.100", 22, "ssh", True)
    tm.process_scan_result("192.168.1.101", 80, "http", True)
    tm.process_scan_result("192.168.1.102", 3389, "rdp", True)
    
    # Show summary
    summary = tm.get_threat_summary()
    print("\nThreat Summary:", summary)
