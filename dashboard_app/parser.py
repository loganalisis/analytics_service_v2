import re
from datetime import datetime
from django.db.models import Count
from .models import LogItems, LogEntry, LogSummary, RawItems

LOG_PATTERN = re.compile(
    r'(?P<ip>\S+) - - \[(?P<timestamp>.*?)\] "(?P<method>\S+) (?P<endpoint>\S+) HTTP/1.\d" (?P<status>\d{3}) (?P<size>\d+)'
)

def parse_log_line(line: str):
    match = LOG_PATTERN.match(line)
    if match:
        data = match.groupdict()
        timestamp = datetime.strptime(data["timestamp"].split()[0], "%d/%b/%Y:%H:%M:%S")
        return {
            "ip": data["ip"],
            "timestamp": timestamp,
            "method": data["method"],
            "endpoint": data["endpoint"],
            "status": int(data["status"]),
            "size": int(data["size"]),
        }
    return None


def process_logs_by_key(unique_key: str):
    """Fetch logs from DB using unique_key, parse and store structured analytics."""
    raw_logs = RawItems.objects.filter(key_name=unique_key)
    if not raw_logs.exists():
        return {"error": f"No logs found for key: {unique_key}"}

    log_entry = LogEntry.objects.filter(unique_key=unique_key)

    if not log_entry.exists():
        entries = []
        for raw in raw_logs:
            parsed = parse_log_line(raw.content)
            if parsed:
                entries.append(LogEntry(
                    unique_key=unique_key,
                    ip_address=parsed["ip"],
                    timestamp=parsed["timestamp"],
                    method=parsed["method"],
                    endpoint=parsed["endpoint"],
                    status_code=parsed["status"],
                    response_size=parsed["size"],
                ))

        LogEntry.objects.bulk_create(entries, ignore_conflicts=True)

        # --- Aggregation Metrics ---
        total = LogEntry.objects.filter(unique_key=unique_key).count()
        success = LogEntry.objects.filter(unique_key=unique_key, status_code__range=(200, 299)).count()
        client_err = LogEntry.objects.filter(unique_key=unique_key, status_code__range=(400, 499)).count()
        server_err = LogEntry.objects.filter(unique_key=unique_key, status_code__range=(500, 599)).count()
        top_ep = LogEntry.objects.filter(unique_key=unique_key).values("endpoint").annotate(c=Count("id")).order_by("-c").first()
        top_ip = LogEntry.objects.filter(unique_key=unique_key).values("ip_address").annotate(c=Count("id")).order_by("-c").first()

        method_counts_qs = LogEntry.objects.filter(unique_key=unique_key).values("method").annotate(count=Count("id")).order_by("-count")
        method_counts = {item["method"]: item["count"] for item in method_counts_qs}

        summary = LogSummary.objects.create(
            unique_key=unique_key,
            total_requests=total,
            success_count=success,
            client_error_count=client_err,
            server_error_count=server_err,
            top_endpoint=top_ep["endpoint"] if top_ep else "",
            top_ip=top_ip["ip_address"] if top_ip else "",
        )

        return {
            "unique_key": unique_key,
            "total": total,
            "success": success,
            "client_error": client_err,
            "server_error": server_err,
            "top_endpoint": top_ep["endpoint"] if top_ep else "",
            "top_ip": top_ip["ip_address"] if top_ip else "",
            "method_counts": method_counts
        }
    else:
        total = LogEntry.objects.filter(unique_key=unique_key).count()
        success = LogEntry.objects.filter(unique_key=unique_key, status_code__range=(200, 299)).count()
        client_err = LogEntry.objects.filter(unique_key=unique_key, status_code__range=(400, 499)).count()
        server_err = LogEntry.objects.filter(unique_key=unique_key, status_code__range=(500, 599)).count()
        top_ep = LogEntry.objects.filter(unique_key=unique_key).values("endpoint").annotate(c=Count("id")).order_by("-c").first()
        top_ip = LogEntry.objects.filter(unique_key=unique_key).values("ip_address").annotate(c=Count("id")).order_by("-c").first()

        method_counts_qs = LogEntry.objects.filter(unique_key=unique_key).values("method").annotate(count=Count("id")).order_by("-count")
        method_counts = {item["method"]: item["count"] for item in method_counts_qs}

        return {
            "unique_key": unique_key,
            "total": total,
            "success": success,
            "client_error": client_err,
            "server_error": server_err,
            "top_endpoint": top_ep["endpoint"] if top_ep else "",
            "top_ip": top_ip["ip_address"] if top_ip else "",
            "method_counts": method_counts
        }