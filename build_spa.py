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
    import re
    content = re.sub(r'<meta[^>]*>', '', content)
    content = re.sub(r'<title[^>]*>.*?</title>', '', content, flags=re.IGNORECASE)
    return content

dash_html = read_file('stitch_ecoshield_pollution_monitor/ecoshield_dashboard/code.html')
geomap_html = read_file('stitch_ecoshield_pollution_monitor/uae_regional_view_glassy_emerald_map/code.html')
detail_html = read_file('stitch_ecoshield_pollution_monitor/site_detail_abu_dhabi_hub/code.html')
ai_signals_html = read_file('stitch_ecoshield_pollution_monitor/ai_signals/code.html')

dash_head = extract_head_styles_and_scripts(dash_html)
geomap_head = extract_head_styles_and_scripts(geomap_html)
detail_head = extract_head_styles_and_scripts(detail_html)
ai_signals_head = extract_head_styles_and_scripts(ai_signals_html)

dash_body = extract_body_content(dash_html)
geomap_body = extract_body_content(geomap_html)
detail_body = extract_body_content(detail_html)
ai_signals_body = extract_body_content(ai_signals_html)

import re
def strip_header(html, is_fixed=False):
    replacement = '' if is_fixed else '<div class="h-16 shrink-0 w-full"></div>'
    return re.sub(r'<header.*?</header>', replacement, html, flags=re.DOTALL)

dash_body = strip_header(dash_body, is_fixed=True)
detail_body = strip_header(detail_body, is_fixed=True)
geomap_body = strip_header(geomap_body, is_fixed=False)

# AI Signals uses <nav class="fixed top-0..."> for its top header instead of <header>.
# DO NOT strip <header> from ai_signals, because its <header> is actually the internal filter bar!
ai_signals_body = re.sub(r'<!-- Top Navigation Bar -->\s*<nav class="fixed top-0[^>]*>.*?</nav>', '', ai_signals_body, flags=re.DOTALL)

shared_navbar = read_file('stitch_ecoshield_pollution_monitor/shared/navbar.html')

# Wire up Navbars
for body_ref in ['dash_body', 'geomap_body', 'detail_body', 'ai_signals_body']:
    locals()[body_ref] = locals()[body_ref].replace('href="#"', 'href="javascript:void(0)"')
    locals()[body_ref] = re.sub(r'href="\.\.[^"]+"', 'href="javascript:void(0)"', locals()[body_ref])
    locals()[body_ref] = locals()[body_ref].replace('>Geo Map</a>', ' onclick="navigate(\'screen-geomap\')">Geo Map</a>')
    locals()[body_ref] = locals()[body_ref].replace('>Earth Pulse</a>', ' onclick="navigate(\'screen-dashboard\')">Earth Pulse</a>')
    locals()[body_ref] = locals()[body_ref].replace('>AI Signals</a>', ' onclick="navigate(\'screen-ai-signals\')">AI Signals</a>')

# Wire up the floating info pill on dashboard
dash_body = dash_body.replace('<div class="glass-panel rounded-full', '<div onclick="navigate(\'screen-geomap\')" class="glass-panel rounded-full')

# Add onclick to geomap company pins
geomap_body = geomap_body.replace('class="group absolute"', 'class="group absolute z-50" onclick="navigate(\'screen-company-sites\', {company: this.querySelector(\'div:nth-child(2)\').innerText})" ')

# Create company sites screen based on geomap
company_sites_body = geomap_body
company_sites_body = company_sites_body.replace('id="es-maptiler"', 'id="es-maptiler-company"')
company_sites_body = company_sites_body.replace('<script src="../shared/ecoshield-map.js"></script>', '')
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

# Update Site Detail for dynamic header
detail_body = detail_body.replace('Live sensor data — Abu Dhabi Hub, Sector 4', '<span id="site-detail-dynamic-title">Live sensor data — Abu Dhabi Hub, Sector 4</span>')


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
    {ai_signals_head}
    <style>
        .screen {{ display: none; width: 100vw; height: 100vh; overflow: hidden; position: absolute; top:0; left:0; }}
        .screen.active {{ display: flex; flex-direction: column; }}
        #screen-site-detail.active {{ overflow-y: auto; overflow-x: hidden; }}
    </style>
</head>
<body class="bg-background text-on-surface m-0 p-0 overflow-hidden w-screen h-screen relative">
    
    {shared_navbar}

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

    <div id="screen-ai-signals" class="screen bg-[#0c1324] overflow-y-auto">
        {ai_signals_body}
    </div>

    <script>
        window.currentCompany = '';
        
        function navigate(screenId, state = {{}}) {{
            document.querySelectorAll('.screen').forEach(s => s.classList.remove('active'));
            document.getElementById(screenId).classList.add('active');
            
            // Update active state in navbar
            document.querySelectorAll('.es-nav-link').forEach(link => {{
                link.classList.remove('text-[#4edea3]', 'border-[#4edea3]');
                link.classList.add('text-[#bbcabf]', 'border-transparent');
            }});
            const activeLink = document.getElementById('nav-' + screenId) || document.getElementById('nav-screen-geomap'); // Fallback for company sites
            if (activeLink) {{
                activeLink.classList.remove('text-[#bbcabf]', 'border-transparent');
                activeLink.classList.add('text-[#4edea3]', 'border-[#4edea3]');
            }}

            if (screenId === 'screen-company-sites') {{
                window.currentCompany = state.company || 'Unknown';
                document.getElementById('company-sites-title').innerText = window.currentCompany;
                generateCompanyPins(window.currentCompany);
            }}
            
            if (screenId === 'screen-site-detail') {{
                const co = state.company || window.currentCompany;
                loadSiteDetails(co);
            }}

            if ((screenId === 'screen-geomap' || screenId === 'screen-company-sites') && window.__esMap) {{
                setTimeout(() => {{
                    window.__esMap.invalidateSize();
                    window.__esMap.fitBounds([
                      [22.6, 51.5],
                      [26.2, 56.6]
                    ], {{ padding: [40, 40] }});
                }}, 100);
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

        async function loadSiteDetails(companyName) {{
            document.getElementById('site-detail-dynamic-title').innerText = `Loading data for ${{companyName}}...`;
            try {{
                const compRes = await fetch('http://localhost:8000/api/companies');
                const companies = await compRes.json();
                const company = companies.find(c => c.name === companyName);
                if (!company) throw new Error('Company not found');
                
                const sitesRes = await fetch(`http://localhost:8000/api/companies/${{company.id}}/sites`);
                const sites = await sitesRes.json();
                if (!sites || sites.length === 0) throw new Error('No sites found for this company');
                const primarySiteId = sites[0].id;
                
                const detailRes = await fetch(`http://localhost:8000/api/sites/${{primarySiteId}}`);
                const siteData = await detailRes.json();
                
                document.getElementById('site-detail-dynamic-title').innerText = `Live sensor data — ${{companyName}}, ${{siteData.name}}`;
                const breadcrumbEl = document.getElementById('detail-company-breadcrumb');
                if (breadcrumbEl) breadcrumbEl.innerText = companyName.toUpperCase();
                document.getElementById('detail-risk-score').innerText = siteData.risk_breakdown.final_risk_score.toFixed(0);
                document.getElementById('detail-risk-tier').innerText = siteData.risk_breakdown.risk_tier;
                document.getElementById('detail-nox').innerText = (siteData.threshold_co2_kg / 100).toFixed(0); 
                
                const tierEl = document.getElementById('detail-risk-tier');
                const scoreEl = document.getElementById('detail-risk-score');
                tierEl.className = 'text-body-sm font-bold uppercase';
                scoreEl.className = 'text-headline-md font-bold';
                if (siteData.risk_breakdown.risk_tier === 'critical') {{
                    tierEl.classList.add('text-red-600');
                    scoreEl.classList.add('text-red-600');
                }} else if (siteData.risk_breakdown.risk_tier === 'elevated') {{
                    tierEl.classList.add('text-amber-600');
                    scoreEl.classList.add('text-amber-600');
                }} else {{
                    tierEl.classList.add('text-green-600');
                    scoreEl.classList.add('text-green-600');
                }}
                
                const tbody = document.getElementById('detail-equipment-table');
                if (tbody) {{
                    tbody.innerHTML = '';
                    siteData.equipment.forEach(eq => {{
                        const row = document.createElement('tr');
                        row.className = 'border-b border-slate-100 hover:bg-slate-50 transition-colors';
                        
                        let replacementHtml = `<div class="text-xs text-slate-400 font-bold uppercase italic">NO REPLACEMENT NEEDED</div>`;
                        if (eq.replacement_rec) {{
                            replacementHtml = `
                            <div class="flex items-center gap-2 text-emerald-600 bg-emerald-50 px-3 py-2 rounded-lg border border-emerald-100">
                                <span class="material-symbols-outlined text-[18px]">electric_bolt</span>
                                <span class="text-xs font-bold leading-tight">${{eq.replacement_rec.recommended_alternative}}<br/><span class="font-normal">(Save ${{eq.replacement_rec.co2_reduction_pct.toFixed(1)}}% CO2)</span></span>
                                <span class="material-symbols-outlined text-emerald-500 ml-auto">check_circle</span>
                            </div>`;
                        }}
                        
                        row.innerHTML = `
                            <td class="p-6 flex items-center gap-3">
                                <span class="material-symbols-outlined text-slate-400">precision_manufacturing</span>
                                <div>
                                    <div class="font-bold">${{eq.machine_type}}</div>
                                    <div class="text-xs text-slate-400">Active ${{eq.hours_active_7d}}h/wk</div>
                                </div>
                            </td>
                            <td class="p-4 font-data-mono">-</td>
                            <td class="p-4 font-data-mono">-</td>
                            <td class="p-4 font-data-mono">-</td>
                            <td class="p-4">
                                <span class="bg-slate-100 text-slate-700 px-2 py-1 rounded text-xs font-bold">Risk Data Pending</span>
                            </td>
                            <td class="p-4">${{replacementHtml}}</td>
                            <td class="p-4">
                                <button class="border-2 border-slate-200 text-slate-500 px-4 py-2 rounded font-bold text-xs hover:bg-slate-50 transition-colors uppercase">Review</button>
                            </td>
                        `;
                        tbody.appendChild(row);
                    }});
                }}
                
                const aiRes = await fetch('http://localhost:8000/api/ai-summary', {{
                    method: 'POST',
                    headers: {{ 'Content-Type': 'application/json' }},
                    body: JSON.stringify({{ site: companyName, machines: [], flaggedReplacements: siteData.equipment.filter(e => !!e.replacement_rec).length }})
                }});
                const aiData = await aiRes.json();
                const aiEl = document.getElementById('detail-ai-summary');
                if (aiEl) aiEl.innerText = aiData.summary;
                
            }} catch (err) {{
                console.error(err);
                document.getElementById('site-detail-dynamic-title').innerText = `Error loading data for ${{companyName}}`;
                const aiEl = document.getElementById('detail-ai-summary');
                if (aiEl) aiEl.innerText = "Failed to load insights.";
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
    f.write(unified_html.replace('../shared/', 'shared/'))

print("SPA Built successfully!")
