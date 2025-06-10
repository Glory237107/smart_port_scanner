def format_report_table_html(scan_results):
    headers = []
    versions = []
    ports = []
    statuses = []
    details = []

    for port, result in scan_results.items():
        service = result.get('service', 'Unknown')
        version = service.split()[-1] if ' ' in service else 'Unknown'
        name = service.split()[0] if ' ' in service else service

        headers.append(name)
        versions.append(version)
        ports.append(str(port))

        vulns = result.get('vulnerabilities', [])
        if not vulns:
            statuses.append('<span style="color:green;">No vulnerabilities</span>')
            details.append("—")
        elif "Insufficient data" in vulns[0]:
            statuses.append('<span style="color:orange;"> Insufficient data</span>')
            details.append("Couldn’t query CVEs")
        elif "Error" in vulns[0]:
            statuses.append('<span style="color:red;">Error</span>')
            details.append(vulns[0])
        else:
            statuses.append(f'<span style="color:red;"> {len(vulns)} found</span>')
            details.append('<br>'.join(vulns[:5]) + ("<br>..." if len(vulns) > 5 else ""))

    html = """
    <html>
    <body>
    <h3 style="font-family:Arial;">Smart Scan Report</h3>
    <table border="1" cellpadding="8" cellspacing="0" style="border-collapse: collapse; font-family: Arial; font-size: 14px; border: 2px solid black;">
        <tr style="background-color: #007ACC; color: white;">
            <th>Service</th>""" + "".join(f"<th>{s}</th>" for s in headers) + """</tr>
        <tr style="background-color: #f9f9f9;">
            <td><b>Version</b></td>""" + "".join(f"<td style='color:#444;'>{v}</td>" for v in versions) + """</tr>
        <tr style="background-color: #ffffff;">
            <td><b>Port</b></td>""" + "".join(f"<td style='color:#333;'>{p}</td>" for p in ports) + """</tr>
        <tr style="background-color: #f9f9f9;">
            <td><b>Status</b></td>""" + "".join(f"<td>{s}</td>" for s in statuses) + """</tr>
        <tr style="background-color: #ffffff;">
            <td><b>Details</b></td>""" + "".join(f"<td style='color:#555;'>{d}</td>" for d in details) + """</tr>
    </table>
    </body>
    </html>
    """
    return html
