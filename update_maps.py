import re
import json

with open('ecoshield_geo_map.html', 'r') as f:
    html_content = f.read()

# Extract EMIRATE_PATHS dictionary
match = re.search(r'const EMIRATE_PATHS\s*=\s*(\{.*?\});', html_content, re.DOTALL)
if not match:
    print("Could not find EMIRATE_PATHS")
    exit(1)

paths_data = json.loads(match.group(1))

new_paths_html = ""
path_template = '<path class="landmass" d="{}" fill="#D2B48C" stroke="#000000" stroke-width="2" style="fill: rgba(16, 185, 129, 0.4); stroke: #34D399; stroke-width: 1.5; filter: drop-shadow(0 0 15px rgba(52, 211, 153, 0.6));"></path>'
for emirate, data in paths_data.items():
    new_paths_html += path_template.format(data['d'])

old_path_regex = r'<path class="landmass" d="M 219\.5,695\.5.*?></path>'

def update_file(filepath, add_pin_clicks=False):
    with open(filepath, 'r') as f:
        content = f.read()
    
    # Replace path
    content = re.sub(old_path_regex, new_paths_html, content)
    
    # Replace pins to be clickable if requested
    if add_pin_clicks:
        content = content.replace('class="group absolute"', 'class="group absolute z-50 cursor-pointer" onclick="window.location.href=\'../uae_regional_view_20_site_markers/code.html?company=\' + encodeURIComponent(this.querySelector(\'div:nth-child(2)\').innerText)"')
    
    with open(filepath, 'w') as f:
        f.write(content)

update_file('stitch_ecoshield_pollution_monitor/uae_regional_view_glassy_emerald_map/code.html', add_pin_clicks=True)
update_file('stitch_ecoshield_pollution_monitor/uae_regional_view_20_site_markers/code.html', add_pin_clicks=False)

print("Map files updated successfully.")
