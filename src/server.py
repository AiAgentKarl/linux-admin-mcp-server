"""Linux Admin MCP Server — AI-Zugriff auf Linux-Systemverwaltung"""
import sys
from fastmcp import FastMCP

from src.tools.system import (
    get_system_info,
    get_disk_usage,
    get_memory_usage,
    run_health_check,
)
from src.tools.services import (
    list_services,
    get_service_status,
    manage_service,
    get_service_logs,
)
from src.tools.processes import (
    list_processes,
    find_process,
    get_top_consumers,
)
from src.tools.network import (
    get_network_interfaces,
    get_open_ports,
    get_active_connections,
    check_dns_resolution,
)

# FastMCP Server initialisieren
mcp = FastMCP(
    "linux-admin-mcp-server",
    instructions=(
        "Linux system administration MCP server. Provides tools for managing "
        "systemd services, monitoring processes, checking disk/memory usage, "
        "inspecting network configuration, and running system health checks. "
        "Requires root/sudo for service management actions (start/stop/enable/disable). "
        "All other tools work as a regular user."
    ),
)


# --- System-Tools ---

@mcp.tool()
def system_info() -> dict:
    """
    Gibt allgemeine System-Informationen zurück.
    Enthält: Hostname, Kernel-Version, CPU-Modell, RAM, Uptime, Architektur, OS-Release.
    Kein sudo erforderlich.
    """
    return get_system_info()


@mcp.tool()
def disk_usage() -> dict:
    """
    Zeigt Festplatten-Belegung aller gemounteten Laufwerke.
    Enthält: Filesystem, Größe, Belegung, verfügbar, Auslastungsprozent, Mountpoint.
    Kein sudo erforderlich.
    """
    return get_disk_usage()


@mcp.tool()
def memory_usage() -> dict:
    """
    Zeigt detaillierte RAM- und Swap-Nutzung.
    Enthält: Gesamt, verwendet, frei, verfügbar für RAM und Swap.
    Kein sudo erforderlich.
    """
    return get_memory_usage()


@mcp.tool()
def health_check() -> dict:
    """
    Führt einen vollständigen System-Health-Check durch.
    Prüft: Disk-Belegung über 80%, CPU-Load, RAM-Verfügbarkeit, Uptime.
    Gibt status='OK' oder 'WARNING' mit einer Liste der gefundenen Probleme zurück.
    Kein sudo erforderlich.
    """
    return run_health_check()


# --- Service-Tools ---

@mcp.tool()
def services_list(filter_state: str = "all") -> dict:
    """
    Listet systemd-Services auf.
    filter_state: 'all' (Standard), 'running', 'failed', 'inactive'
    Gibt max. 50 Services zurück mit Name, Status, Beschreibung.
    Kein sudo erforderlich.
    """
    return list_services(filter_state=filter_state)


@mcp.tool()
def service_status(service_name: str) -> dict:
    """
    Gibt den detaillierten Status eines systemd-Services zurück.
    service_name: Name des Services (z.B. 'nginx', 'postgresql', 'sshd')
    Enthält: aktiv/inaktiv, enabled/disabled, letzten Log-Output.
    Kein sudo erforderlich.
    """
    return get_service_status(service_name=service_name)


@mcp.tool()
def service_manage(service_name: str, action: str) -> dict:
    """
    Verwaltet einen systemd-Service.
    service_name: Name des Services (z.B. 'nginx', 'postgresql')
    action: 'start', 'stop', 'restart', 'reload', 'enable', 'disable'
    HINWEIS: Erfordert sudo-Rechte. Server muss als root laufen oder sudoers-Eintrag haben.
    """
    return manage_service(service_name=service_name, action=action)


@mcp.tool()
def service_logs(service_name: str, lines: int = 50) -> dict:
    """
    Gibt die letzten Log-Zeilen eines Services über journalctl zurück.
    service_name: Name des Services
    lines: Anzahl der Log-Zeilen (Standard: 50, max: 500)
    Kein sudo erforderlich.
    """
    return get_service_logs(service_name=service_name, lines=lines)


# --- Prozess-Tools ---

@mcp.tool()
def processes_list(sort_by: str = "cpu", limit: int = 20) -> dict:
    """
    Listet laufende Prozesse auf.
    sort_by: 'cpu' (Standard), 'memory', 'pid'
    limit: Anzahl der Prozesse (Standard: 20, max: 100)
    Kein sudo erforderlich.
    """
    return list_processes(sort_by=sort_by, limit=limit)


@mcp.tool()
def process_find(name: str) -> dict:
    """
    Sucht nach laufenden Prozessen anhand eines Namens oder Befehlsteils.
    name: Suchbegriff (z.B. 'nginx', 'python', 'postgres')
    Gibt PID und vollständigen Befehl zurück.
    Kein sudo erforderlich.
    """
    return find_process(name=name)


@mcp.tool()
def top_consumers() -> dict:
    """
    Zeigt die Top-5 CPU- und Memory-Verbraucher.
    Nützlich für schnelle Performance-Diagnose.
    Kein sudo erforderlich.
    """
    return get_top_consumers()


# --- Netzwerk-Tools ---

@mcp.tool()
def network_interfaces() -> dict:
    """
    Listet alle Netzwerk-Interfaces mit IP-Adressen auf.
    Enthält: Interface-Name, IPv4/IPv6-Adressen, Flags.
    Kein sudo erforderlich.
    """
    return get_network_interfaces()


@mcp.tool()
def open_ports() -> dict:
    """
    Listet alle Ports auf, die auf eingehende Verbindungen warten (LISTEN).
    Nützlich um zu sehen welche Services aktiv Verbindungen annehmen.
    Kein sudo erforderlich (ohne Prozess-Info).
    """
    return get_open_ports()


@mcp.tool()
def active_connections() -> dict:
    """
    Zeigt aktive Netzwerkverbindungen (ESTABLISHED).
    Gibt lokale und Remote-Adressen für bis zu 50 Verbindungen zurück.
    Kein sudo erforderlich.
    """
    return get_active_connections()


@mcp.tool()
def dns_lookup(hostname: str) -> dict:
    """
    Löst einen Hostnamen per DNS auf und gibt die IP-Adresse zurück.
    hostname: Zu auflösender Hostname (z.B. 'google.com', 'api.example.com')
    Kein sudo erforderlich.
    """
    return check_dns_resolution(hostname=hostname)


def main():
    """Server-Einstiegspunkt."""
    mcp.run(transport="stdio")


if __name__ == "__main__":
    main()
