import re
with open("build_spa.py", "r") as f:
    content = f.read()

replacement = """        function navigate(screenId, state = {}) {
            document.querySelectorAll('.screen').forEach(s => s.classList.remove('active'));
            document.getElementById(screenId).classList.add('active');
            
            if (screenId === 'screen-company-sites') {
                window.currentCompany = state.company || 'Unknown';
                document.getElementById('company-sites-title').innerText = window.currentCompany;
                generateCompanyPins(window.currentCompany);
            }
            
            if (screenId === 'screen-site-detail') {
                const co = state.company || window.currentCompany;
                const sid = state.siteId || '1';
                document.getElementById('site-detail-dynamic-title').innerText = `Live sensor data — ${co}, Site #${sid}`;
            }

            if ((screenId === 'screen-geomap' || screenId === 'screen-company-sites') && window.__esMap) {
                setTimeout(() => window.__esMap.invalidateSize(), 100);
            }
        }"""

content = re.sub(r'        function navigate\(screenId, state = \{\}\) \{.*?        \}', replacement, content, flags=re.DOTALL)

with open("build_spa.py", "w") as f:
    f.write(content)
print("Patched successfully")
