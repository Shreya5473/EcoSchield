import os

def read_file(filepath):
    with open(filepath, 'r') as f:
        return f.read()

def extract_body_content(html):
    start = html.find('<body')
    start = html.find('>', start) + 1
    end = html.rfind('</body>')
    return html[start:end]

def extract_head_styles_and_scripts(html):
    start = html.find('<head>') + 6
    end = html.rfind('</head>')
    content = html[start:end]
    lines = content.split('\n')
    filtered = []
    for line in lines:
        if '<title>' not in line and '<meta' not in line:
            filtered.append(line)
    return '\n'.join(filtered)

dash_html = read_file('stitch_ecoshield_pollution_monitor/ecoshield_dashboard/code.html')
geomap_html = read_file('stitch_ecoshield_pollution_monitor/uae_regional_view_glassy_emerald_map/code.html')
detail_html = read_file('stitch_ecoshield_pollution_monitor/site_detail_abu_dhabi_hub/code.html')

dash_head = extract_head_styles_and_scripts(dash_html)
geomap_head = extract_head_styles_and_scripts(geomap_html)
detail_head = extract_head_styles_and_scripts(detail_html)

dash_body = extract_body_content(dash_html)
geomap_body = extract_body_content(geomap_html)
detail_body = extract_body_content(detail_html)

# Wire up Navbars
for body_ref in ['dash_body', 'geomap_body', 'detail_body']:
    locals()[body_ref] = locals()[body_ref].replace('href="#"', 'href="javascript:void(0)"')
    locals()[body_ref] = locals()[body_ref].replace('>Geo Map</a>', ' onclick="navigate(\'screen-geomap\')">Geo Map</a>')
    locals()[body_ref] = locals()[body_ref].replace('>Earth Pulse</a>', ' onclick="navigate(\'screen-dashboard\')">Earth Pulse</a>')

# Wire up the floating info pill on dashboard
dash_body = dash_body.replace('<div class="glass-panel rounded-full', '<div onclick="navigate(\'screen-geomap\')" class="glass-panel rounded-full')

# Add onclick to geomap company pins
geomap_body = geomap_body.replace('class="group absolute"', 'class="group absolute z-50" onclick="navigate(\'screen-company-sites\', {company: this.querySelector(\'div:nth-child(2)\').innerText})" ')

# Create company sites screen based on geomap
company_sites_body = geomap_body
pin_start = company_sites_body.find('<div class="group absolute')
if pin_start != -1:
    pin_end = company_sites_body.find('<!-- BEGIN: Floating Overlays -->')
    company_sites_body = company_sites_body[:pin_start] + '<div id="company-pins-container" class="absolute inset-0 z-40"></div>' + company_sites_body[pin_end:]

# Add breadcrumb/back button to company sites
breadcrumb = """
<div class="absolute top-4 left-4 z-50 flex items-center gap-2 text-[#34D399] bg-[#14202B]/90 px-4 py-2 rounded border border-[#34D399]/30 cursor-pointer hover:bg-[#14202B]" onclick="navigate('screen-geomap')">
    <svg class="w-4 h-4" fill="none" stroke="currentColor" viewBox="0 0 24 24"><path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M15 19l-7-7 7-7"></path></svg>
    <span class="font-bold text-sm tracking-wider">Back to Geo Map</span>
    <span class="text-gray-400 mx-2">|</span>
    <span class="text-white text-sm" id="company-sites-title">Company</span>
</div>
"""
company_sites_body = company_sites_body.replace('<!-- BEGIN: Map Area -->\n<section class="map-area">', '<!-- BEGIN: Map Area -->\n<section class="map-area">' + breadcrumb)

# Update Site Detail for dynamic header and back button
detail_body = detail_body.replace('Live sensor data — Abu Dhabi Hub, Sector 4', '<span id="site-detail-dynamic-title">Live sensor data — Abu Dhabi Hub, Sector 4</span>')
back_btn_detail = """
<div class="mb-4 cursor-pointer text-primary hover:text-white flex items-center gap-2 w-fit transition-colors" onclick="navigate('screen-company-sites', {company: window.currentCompany})">
    <span class="material-symbols-outlined text-[18px]">arrow_back</span>
    <span class="font-bold text-sm">Back to Company Sites</span>
</div>
"""
detail_body = detail_body.replace('<!-- Breadcrumbs -->', '<!-- Breadcrumbs -->\n' + back_btn_detail)


unified_html = f"""<!DOCTYPE html>
<html lang="en" class="dark">
<head>
    <meta charset="utf-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>EcoShield SPA</title>
    <script src="https://cdn.tailwindcss.com?plugins=forms,container-queries"></script>
    {dash_head}
    {geomap_head}
    {detail_head}
    <style>
        .screen {{ display: none; width: 100vw; height: 100vh; overflow: hidden; position: absolute; top:0; left:0; }}
        .screen.active {{ display: flex; flex-direction: column; }}
        #screen-site-detail.active {{ overflow-y: auto; overflow-x: hidden; }}
    </style>
</head>
<body class="bg-background text-on-surface m-0 p-0 overflow-hidden w-screen h-screen relative">

    <div id="screen-dashboard" class="screen active">
        {dash_body}
    </div>

    <div id="screen-geomap" class="screen" style="background-color: var(--bg-ocean);">
        {geomap_body}
    </div>

    <div id="screen-company-sites" class="screen" style="background-color: var(--bg-ocean);">
        {company_sites_body}
    </div>

    <div id="screen-site-detail" class="screen bg-[#0c1324]">
        {detail_body}
    </div>

    <script>
        window.currentCompany = '';
        
        function navigate(screenId, state = {{}}) {{
            document.querySelectorAll('.screen').forEach(s => s.classList.remove('active'));
            document.getElementById(screenId).classList.add('active');
            
            if (screenId === 'screen-company-sites') {{
                window.currentCompany = state.company || 'Unknown';
                document.getElementById('company-sites-title').innerText = window.currentCompany;
                generateCompanyPins(window.currentCompany);
            }}
            
            if (screenId === 'screen-site-detail') {{
                const co = state.company || window.currentCompany;
                const sid = state.siteId || '1';
                document.getElementById('site-detail-dynamic-title').innerText = `Live sensor data — ${{co}}, Site #${{sid}}`;
            }}
        }}

        function generateCompanyPins(companyName) {{
            const container = document.getElementById('company-pins-container');
            if(!container) return;
            container.innerHTML = '';
            
            for (let i = 1; i <= 40; i++) {{
                const left = 30 + Math.random() * 50; 
                const top = 20 + Math.random() * 60; 
                
                const pin = document.createElement('div');
                pin.className = 'absolute w-3 h-3 bg-black rounded-full border-2 border-gray-400 cursor-pointer hover:scale-[1.5] hover:bg-white hover:border-black transition-all shadow-lg pointer-events-auto';
                pin.style.left = left + '%';
                pin.style.top = top + '%';
                pin.title = `Site #${{i}}`;
                
                pin.onclick = (e) => {{
                    e.stopPropagation();
                    navigate('screen-site-detail', {{ company: companyName, siteId: i }});
                }};
                
                container.appendChild(pin);
            }}
        }}

        // Setup Globe Click
        document.addEventListener('DOMContentLoaded', () => {{
            // Wait for Three.js canvas to mount
            const checkCanvas = setInterval(() => {{
                const canvas = document.querySelector('#screen-dashboard canvas');
                if(canvas) {{
                    clearInterval(checkCanvas);
                    
                    let isDragging = false;
                    canvas.addEventListener('mousedown', () => {{ isDragging = false; }});
                    canvas.addEventListener('mousemove', () => {{ isDragging = true; }});
                    canvas.addEventListener('mouseup', () => {{
                        if (!isDragging) {{
                            navigate('screen-geomap');
                        }}
                    }});
                }}
            }}, 500);
        }});
    </script>
</body>
</html>
"""

with open('stitch_ecoshield_pollution_monitor/index.html', 'w') as f:
    f.write(unified_html)

print("SPA Built successfully!")
