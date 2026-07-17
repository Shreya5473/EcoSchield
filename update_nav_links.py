import os

files = [
    "stitch_ecoshield_pollution_monitor/ecoshield_dashboard/code.html",
    "stitch_ecoshield_pollution_monitor/site_detail_abu_dhabi_hub/code.html",
    "stitch_ecoshield_pollution_monitor/uae_regional_view_20_site_markers/code.html",
    "stitch_ecoshield_pollution_monitor/uae_regional_view_glassy_emerald_map/code.html"
]

for filepath in files:
    with open(filepath, 'r') as f:
        content = f.read()

    # Generic replace for AI Signals
    content = content.replace('href="#">AI Signals</a>', 'href="../ai_signals/code.html">AI Signals</a>')
    
    # Generic replace for Earth Pulse (if not the dashboard)
    if "ecoshield_dashboard" not in filepath:
        content = content.replace('href="#">Earth Pulse</a>', 'href="../ecoshield_dashboard/code.html">Earth Pulse</a>')
        
    # Generic replace for Geo Map (if not the geo map)
    if "uae_regional_view_glassy_emerald_map" not in filepath and "uae_regional_view_20_site_markers" not in filepath:
        content = content.replace('href="#">Geo Map</a>', 'href="../uae_regional_view_glassy_emerald_map/code.html">Geo Map</a>')

    with open(filepath, 'w') as f:
        f.write(content)

print("Nav links updated successfully.")
