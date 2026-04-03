"""Netzwerk-Tools: Interfaces, Verbindungen, Ports, DNS"""
import subprocess
from typing import Any


def _run(cmd: list[str], timeout: int = 10) -> tuple[int, str, str]:
    """Führt einen Befehl sicher aus."""
    try:
        result = subprocess.run(
            cmd,
            capture_output=True,
            text=True,
            timeout=timeout,
            check=False,
        )
        return result.returncode, result.stdout.strip(), result.stderr.strip()
    except subprocess.TimeoutExpired:
        return 1, "", "Timeout"
    except FileNotFoundError:
        return 1, "", f"Befehl nicht gefunden: {cmd[0]}"
    except Exception as e:
        return 1, "", str(e)


def get_network_interfaces() -> dict[str, Any]:
    """Gibt alle Netzwerk-Interfaces mit IP-Adressen zurück."""
    rc, stdout, stderr = _run(["ip", "addr", "show"])
    if rc != 0:
        # Fallback auf ifconfig
        rc, stdout, stderr = _run(["ifconfig", "-a"])

    interfaces = []
    current_iface = None

    for line in stdout.split("\n"):
        # Neue Interface-Zeile (beginnt mit Zahl und Doppelpunkt)
        if line and line[0].isdigit() and ": " in line:
            parts = line.split(": ")
            if len(parts) >= 2:
                current_iface = {
                    "name": parts[1].split("@")[0].split(" ")[0],
                    "flags": line.split("<")[1].split(">")[0] if "<" in line else "",
                    "addresses": [],
                }
                interfaces.append(current_iface)
        elif current_iface and "inet " in line:
            parts = line.strip().split()
            if len(parts) >= 2:
                current_iface["addresses"].append({
                    "type": "ipv4",
                    "address": parts[1],
                })
        elif current_iface and "inet6 " in line:
            parts = line.strip().split()
            if len(parts) >= 2:
                current_iface["addresses"].append({
                    "type": "ipv6",
                    "address": parts[1],
                })

    return {
        "interfaces": interfaces,
        "count": len(interfaces),
        "raw": stdout[:2000],  # Roh-Ausgabe kürzen
    }


def get_open_ports() -> dict[str, Any]:
    """Listet alle offenen Ports (LISTEN) auf."""
    # ss bevorzugen (moderner), Fallback auf netstat
    rc, stdout, stderr = _run(["ss", "-tlnp"])
    if rc != 0:
        rc, stdout, stderr = _run(["netstat", "-tlnp"])

    ports = []
    for line in stdout.split("\n"):
        if "LISTEN" in line or (rc != 0 and "tcp" in line.lower()):
            parts = line.split()
            if len(parts) >= 4:
                local_addr = parts[3] if rc == 0 else parts[3]
                ports.append({
                    "local_address": local_addr,
                    "raw": line.strip(),
                })

    return {
        "listening_ports": ports,
        "count": len(ports),
        "raw": stdout[:3000],
    }


def get_active_connections() -> dict[str, Any]:
    """Zeigt aktive Netzwerkverbindungen (ESTABLISHED)."""
    rc, stdout, stderr = _run(["ss", "-tnp", "state", "established"])
    if rc != 0:
        rc, stdout, stderr = _run(["netstat", "-tnp"])

    connections = []
    for line in stdout.split("\n")[1:]:  # Header überspringen
        if line.strip():
            parts = line.split()
            if len(parts) >= 5:
                connections.append({
                    "local": parts[3] if len(parts) > 3 else "",
                    "remote": parts[4] if len(parts) > 4 else "",
                    "raw": line.strip(),
                })

    return {
        "connections": connections[:50],
        "count": len(connections),
    }


def check_dns_resolution(hostname: str) -> dict[str, Any]:
    """Löst einen Hostnamen per DNS auf."""
    # Sicherheitscheck
    safe_chars = set("abcdefghijklmnopqrstuvwxyzABCDEFGHIJKLMNOPQRSTUVWXYZ0123456789-._")
    if not all(c in safe_chars for c in hostname):
        return {"error": f"Ungültiger Hostname: {hostname}"}

    rc, stdout, stderr = _run(["getent", "hosts", hostname])
    if rc == 0 and stdout:
        parts = stdout.split()
        return {
            "hostname": hostname,
            "resolved": True,
            "ip": parts[0] if parts else "unbekannt",
            "aliases": parts[1:],
        }

    # Fallback: nslookup
    rc2, stdout2, _ = _run(["nslookup", hostname])
    return {
        "hostname": hostname,
        "resolved": rc2 == 0,
        "output": stdout2[:500] if stdout2 else stderr[:200],
    }
