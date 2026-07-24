/**
 * EcoShield MapTiler live map via Leaflet (raster tiles).
 * Warm desert chrome — not dark-blue AI HUD.
 */
(function () {
  'use strict';

  const KEY = window.ECOSHIELD_MAPTILER_KEY;
  if (!KEY || typeof L === 'undefined') {
    console.warn('EcoShield map: MapTiler key or Leaflet missing');
    return;
  }

  const SITES = [
    { name: 'Bin Hamoodah', sector: 'Construction', lng: 54.52, lat: 24.48, risk: 'critical' },
    { name: 'Al Rostamani', sector: 'Logistics', lng: 55.18, lat: 25.12, risk: 'critical' },
    { name: 'Ghantoot Group', sector: 'Construction', lng: 54.55, lat: 24.42, risk: 'nominal' },
    { name: 'Al Naboodah', sector: 'Infrastructure', lng: 55.28, lat: 25.18, risk: 'elevated' },
    { name: 'Depa Interiors', sector: 'Fit-out', lng: 55.14, lat: 25.07, risk: 'elevated' },
    { name: 'Emirates Neon', sector: 'Manufacturing', lng: 55.35, lat: 24.95, risk: 'elevated' },
    { name: 'Infranet Corp', sector: 'Energy', lng: 55.51, lat: 25.41, risk: 'critical' },
    { name: 'Al Safa Industrial', sector: 'Manufacturing', lng: 55.22, lat: 25.15, risk: 'critical' },
    { name: 'TechNoCity', sector: 'Infrastructure', lng: 55.42, lat: 25.35, risk: 'elevated' },
    { name: 'Proscape', sector: 'Landscaping', lng: 55.27, lat: 25.2, risk: 'elevated' },
    { name: 'Suntech', sector: 'Energy', lng: 55.94, lat: 25.79, risk: 'nominal' },
    { name: 'Missan Group', sector: 'Construction', lng: 56.33, lat: 25.13, risk: 'critical' }
  ];

  const RISK_COLOR = {
    critical: '#C45C26',
    elevated: '#D4A017',
    nominal: '#3D7A5A'
  };

  const RISK_LABEL = {
    critical: 'Critical',
    elevated: 'Elevated',
    nominal: 'Nominal'
  };

  function tileUrl(mapId, ext) {
    return `https://api.maptiler.com/maps/${mapId}/{z}/{x}/{y}.${ext || 'png'}?key=${KEY}`;
  }

  function softenedSet() {
    try {
      return new Set(JSON.parse(localStorage.getItem('ecoshield_softened_pins') || '[]'));
    } catch (_) {
      return new Set();
    }
  }

  function pinColor(site) {
    const soft = softenedSet();
    if ([...soft].some((s) => site.name.includes(s) || s.includes(site.name))) {
      return '#E07A3A';
    }
    return RISK_COLOR[site.risk] || '#C45C26';
  }

  function init() {
    const el = document.getElementById('es-maptiler');
    if (!el) return;

    const terrain = L.tileLayer(tileUrl('streets-v2', 'png'), {
      tileSize: 512,
      zoomOffset: -1,
      minZoom: 5,
      maxZoom: 16,
      opacity: 1,
      attribution:
        '<a href="https://www.maptiler.com/copyright/">© MapTiler</a> <a href="https://www.openstreetmap.org/copyright">© OpenStreetMap</a>'
    });

    const outdoor = L.tileLayer(tileUrl('outdoor-v2', 'png'), {
      tileSize: 512,
      zoomOffset: -1,
      minZoom: 5,
      maxZoom: 16,
      opacity: 1,
      attribution: '© MapTiler © OpenStreetMap'
    });

    const satellite = L.tileLayer(tileUrl('hybrid', 'jpg'), {
      tileSize: 512,
      zoomOffset: -1,
      minZoom: 5,
      maxZoom: 16,
      opacity: 1,
      attribution: '© MapTiler © OpenStreetMap'
    });

    const map = L.map('es-maptiler', {
      center: [24.55, 54.9],
      zoom: 7,
      layers: [terrain],
      zoomControl: true,
      fadeAnimation: false,
      markerZoomAnimation: false,
      maxBounds: [
        [21.5, 50.5],
        [27.5, 58.5]
      ]
    });

    window.__esMap = map;
    el.classList.add('es-map-warm');

    // Emission heat as translucent circles (Leaflet-friendly)
    const heatLayer = L.layerGroup();
    SITES.filter((s) => s.risk !== 'nominal').forEach((s) => {
      const radius = s.risk === 'critical' ? 38000 : 26000;
      const color = s.risk === 'critical' ? '#C45C26' : '#D4A017';
      L.circle([s.lat, s.lng], {
        radius,
        color,
        weight: 0,
        fillColor: color,
        fillOpacity: 0.28
      }).addTo(heatLayer);
    });

    SITES.forEach((site) => {
      const color = pinColor(site);
      const icon = L.divIcon({
        className: 'es-leaflet-pin',
        html:
          `<div class="es-map-pin" style="position:relative;width:28px;height:36px">` +
          `<span class="es-map-pin-pulse" style="background:${color}"></span>` +
          `<span class="es-map-pin-dot" style="background:${color}"></span>` +
          `<span class="es-map-pin-label">${site.name}</span></div>`,
        iconSize: [28, 36],
        iconAnchor: [14, 36]
      });

      L.marker([site.lat, site.lng], { icon })
        .addTo(map)
        .bindPopup(
          `<strong>${site.name}</strong><br/><span style="color:#A89B88">${site.sector}</span><br/>` +
            `<em style="color:${color}">${RISK_LABEL[site.risk]} risk</em>`
        )
        .on('click', () => {
          // allow popup first; double-nav on popup link feel
        });

      // Navigate on pin double-click / popup title click via custom
    });

    // Click pin label area → site detail (delegate)
    el.addEventListener('click', (e) => {
      const pin = e.target.closest('.es-map-pin');
      if (!pin) return;
      const label = pin.querySelector('.es-map-pin-label');
      const name = label && label.textContent.trim();
      if (!name) return;
      // single click opens popup; use title attribute path via delay open detail from popup button
    });

    // Add "Open site" into each popup after open
    map.on('popupopen', (e) => {
      const content = e.popup.getContent();
      const match = content && content.match(/<strong>([^<]+)<\/strong>/);
      if (!match) return;
      const name = match[1];
      const wrap = e.popup.getElement();
      if (!wrap || wrap.querySelector('.es-open-site')) return;
      const btn = document.createElement('button');
      btn.className = 'es-open-site';
      btn.type = 'button';
      btn.textContent = 'Open site audit →';
      btn.style.cssText =
        'margin-top:8px;display:block;width:100%;padding:6px 8px;border:1px solid #C4A574;background:#2A241C;color:#E8C988;border-radius:4px;cursor:pointer;font-size:11px';
      btn.onclick = () => {
        location.href =
          '../site_detail_abu_dhabi_hub/code.html?company=' +
          encodeURIComponent(name) +
          '&site=1';
      };
      wrap.querySelector('.leaflet-popup-content')?.appendChild(btn);
    });

    map.fitBounds(
      [
        [22.6, 51.5],
        [26.2, 56.6]
      ],
      { padding: [40, 40] }
    );

    wireToggles(map, { terrain, outdoor, satellite, heatLayer });
    setTimeout(() => map.invalidateSize(), 200);
  }

  function wireToggles(map, layers) {
    const terrainBtn = document.getElementById('es-style-terrain');
    const satBtn = document.getElementById('es-style-satellite');
    const heatBtn = document.getElementById('es-style-heat');
    let heatOn = false;
    let activeBase = layers.terrain;

    function setActive(btn) {
      [terrainBtn, satBtn].forEach((b) => b && b.classList.remove('active'));
      if (btn) btn.classList.add('active');
    }

    function useBase(layer, btn, satMode) {
      map.removeLayer(activeBase);
      activeBase = layer;
      map.addLayer(activeBase);
      const box = document.getElementById('es-maptiler');
      box?.classList.toggle('es-map-warm', !satMode);
      box?.classList.toggle('es-map-sat', !!satMode);
      setActive(btn);
    }

    terrainBtn?.addEventListener('click', () => useBase(layers.terrain, terrainBtn, false));
    satBtn?.addEventListener('click', () => {
      useBase(layers.satellite, satBtn, true);
      if (!heatOn) {
        heatOn = true;
        map.addLayer(layers.heatLayer);
        heatBtn?.classList.add('active');
      }
    });
    heatBtn?.addEventListener('click', () => {
      heatOn = !heatOn;
      if (heatOn) map.addLayer(layers.heatLayer);
      else map.removeLayer(layers.heatLayer);
      heatBtn.classList.toggle('active', heatOn);
    });

    setActive(terrainBtn);
  }

  if (document.readyState === 'loading') {
    document.addEventListener('DOMContentLoaded', init);
  } else {
    init();
  }
})();
