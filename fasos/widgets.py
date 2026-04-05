# fasos/widgets.py
from django import forms
from django.utils.safestring import mark_safe


class SearchableLeafletWidget(forms.TextInput):
    """Widget GIS dengan Leaflet - Map Click Locked, GPS & Search Only"""
    
    class Media:
        css = {
            "all": (
                "https://unpkg.com/leaflet@1.9.4/dist/leaflet.css",
            )
        }
        js = (
            "https://unpkg.com/leaflet@1.9.4/dist/leaflet.js",
        )

    def render(self, name, value, attrs=None, renderer=None):
        html = super().render(name, value, attrs, renderer)
        widget_id = attrs.get('id', name)
        
        custom_icon_html = '''<svg xmlns="http://www.w3.org/2000/svg" width="32" height="32" viewBox="0 0 24 24" fill="#e74c3c" stroke="#fff" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"><path d="M21 10c0 7-9 13-9 13s-9-6-9-13a9 9 0 0 1 18 0z"></path><circle cx="12" cy="10" r="3"></circle></svg>'''
        
        init_html = f"""
        <div style="margin-top: 10px;">
            <div id="{widget_id}_map" style="height: 450px; width: 100%; min-width: 750px; max-width: 100%; border: 1px solid #ccc; border-radius: 4px; position: relative;">
                
                <!-- Search Box -->
                <div id="{widget_id}_search_container" style="position: absolute; top: 10px; left: 60px; z-index: 1000; background: white; padding: 5px; border-radius: 4px; box-shadow: 0 2px 5px rgba(0,0,0,0.3);">
                    <input type="text" id="{widget_id}_search" placeholder="Cari lokasi..." 
                           style="padding: 5px 10px; width: 250px; border: 1px solid #ddd; border-radius: 3px;">
                    <button type="button" id="{widget_id}_search_btn" 
                            style="padding: 5px 10px; background: #007bff; color: white; border: none; border-radius: 3px; cursor: pointer; margin-left: 5px;">🔍</button>
                </div>
                
                <!-- Control Buttons -->
                <div id="{widget_id}_controls" style="position: absolute; top: 90px; left: 10px; z-index: 1000; display: flex; flex-direction: column; gap: 5px;">
                    <button type="button" id="{widget_id}_locate_btn" title="Gunakan lokasi saya (GPS)"
                            style="width: 30px; height: 30px; background: white; border: 2px solid rgba(0,0,0,0.2); border-radius: 4px; cursor: pointer; font-size: 16px; box-shadow: 0 1px 5px rgba(0,0,0,0.4);">📍</button>
                    <button type="button" id="{widget_id}_edit_btn" title="Edit titik lokasi (Drag)"
                            style="width: 30px; height: 30px; background: white; border: 2px solid rgba(0,0,0,0.2); border-radius: 4px; cursor: pointer; font-size: 16px; box-shadow: 0 1px 5px rgba(0,0,0,0.4);">✏️</button>
                    <button type="button" id="{widget_id}_delete_btn" title="Hapus titik lokasi"
                            style="width: 30px; height: 30px; background: white; border: 2px solid rgba(0,0,0,0.2); border-radius: 4px; cursor: pointer; font-size: 16px; box-shadow: 0 1px 5px rgba(0,0,0,0.4);">🗑️</button>
                </div>
            </div>
            
            <div style="margin-top: 5px; color: #666; font-size: 12px;">
                🔒 Klik peta dinonaktifkan | Gunakan 📍 GPS atau 🔍 Search untuk set lokasi | ✏️ Drag untuk fine-tune
            </div>
        </div>
        
        <script>
        (function() {{
            console.log('🗺️ [SearchableLeafletWidget] Initializing...');
            
            var widgetId = '{widget_id}';
            var mapContainer = document.getElementById(widgetId + '_map');
            var hiddenInput = document.getElementById(widgetId);
            var searchInput = document.getElementById(widgetId + '_search');
            var searchBtn = document.getElementById(widgetId + '_search_btn');
            var searchContainer = document.getElementById(widgetId + '_search_container');
            var controlsDiv = document.getElementById(widgetId + '_controls');
            var locateBtn = document.getElementById(widgetId + '_locate_btn');
            var editBtn = document.getElementById(widgetId + '_edit_btn');
            var deleteBtn = document.getElementById(widgetId + '_delete_btn');
            
            if (!mapContainer || !hiddenInput) {{
                console.error('❌ Map container atau hidden input tidak ditemukan!');
                return;
            }}
            
            hiddenInput.type = 'hidden';
            hiddenInput.style.display = 'none';
            
            // Inisialisasi Peta
            var map = L.map(mapContainer).setView([-6.2088, 106.8456], 13);
            
            var cartoLayer = L.tileLayer('https://{{s}}.basemaps.cartocdn.com/light_all/{{z}}/{{x}}/{{y}}{{r}}.png', {{
                attribution: '&copy; OpenStreetMap &copy; CARTO', subdomains: 'abcd', maxZoom: 20
            }});
            var satelliteLayer = L.tileLayer('https://server.arcgisonline.com/ArcGIS/rest/services/World_Imagery/MapServer/tile/{{z}}/{{y}}/{{x}}', {{
                attribution: 'Tiles &copy; Esri', maxZoom: 19
            }});
            
            cartoLayer.addTo(map);
            L.control.layers({{
                "🗺️ Peta Jalan": cartoLayer,
                "🛰️ Satelit": satelliteLayer
            }}, null, {{ collapsed: true }}).addTo(map);
            
            L.control.scale({{ position: 'bottomright', metric: true, maxWidth: 100 }}).addTo(map);
            
            var customIcon = L.divIcon({{
                className: 'custom-map-pin',
                html: '{custom_icon_html}',
                iconSize: [32, 32],
                iconAnchor: [16, 32],
                popupAnchor: [0, -32]
            }});
            
            var marker = null;
            var isEditMode = false;

            // 🔧 FUNGSI UPDATE KOORDINAT (Hanya dipanggil oleh GPS, Search, & Drag)
            function updateCoords(lat, lng, popupText) {{
                if (!lat || !lng) return;
                hiddenInput.value = "POINT(" + lng + " " + lat + ")";
                if (marker) map.removeLayer(marker);
                
                marker = L.marker([lat, lng], {{icon: customIcon, draggable: isEditMode}}).addTo(map);
                
                var latStr = lat.toFixed(5);
                var lngStr = lng.toFixed(5);
                marker.bindPopup(popupText || '<b>📍 Lokasi Diperbarui</b><br>Lat: ' + latStr + '<br>Lng: ' + lngStr).openPopup();
                
                marker.on('dragend', function(e) {{
                    var pos = e.target.getLatLng();
                    hiddenInput.value = "POINT(" + pos.lng + " " + pos.lat + ")";
                    marker.bindPopup('<b>✅ Lokasi Diperbarui (Drag)</b><br>Lat: ' + pos.lat.toFixed(5) + '<br>Lng: ' + pos.lng.toFixed(5)).openPopup();
                }});
                
                console.log('📍 Koordinat diset:', latStr, lngStr);
            }}

            // 🔒 KLIK PETA: SEPENUHNYA DIKUNCI
            map.on('click', function(e) {{
                console.log('🔒 Klik peta dinonaktifkan. Gunakan tombol 📍 GPS atau 🔍 Search.');
                // Tidak ada updateCoords di sini
            }});
            
            // 🔍 SEARCH FUNCTION
            async function searchLocation() {{
                var query = searchInput.value.trim();
                if (!query) {{ alert('Masukkan nama lokasi'); return; }}
                searchBtn.innerHTML = '⏳';
                try {{
                    var url = 'https://nominatim.openstreetmap.org/search?format=json&q=' + encodeURIComponent(query);
                    var res = await fetch(url);
                    var data = await res.json();
                    if (data.length > 0) {{
                        var lat = parseFloat(data[0].lat);
                        var lng = parseFloat(data[0].lon);
                        var name = data[0].display_name;
                        updateCoords(lat, lng, '<b>🔍 ' + name + '</b><br>Lat: ' + lat.toFixed(5) + '<br>Lng: ' + lng.toFixed(5));
                        map.flyTo([lat, lng], 16, {{animate: true, duration: 1.5}});
                    }} else {{
                        alert('Lokasi "' + query + '" tidak ditemukan.');
                    }}
                }} catch (err) {{
                    console.error('Search Error:', err);
                    alert('Gagal mencari lokasi.');
                }} finally {{
                    searchBtn.innerHTML = '🔍';
                }}
            }}
            
            if (searchBtn) searchBtn.addEventListener('click', function(e) {{ e.preventDefault(); e.stopPropagation(); searchLocation(); }});
            if (searchInput) searchInput.addEventListener('keypress', function(e) {{
                if(e.key === 'Enter') {{ e.preventDefault(); e.stopPropagation(); searchLocation(); }}
            }});
            
            if (searchContainer) {{
                searchContainer.addEventListener('click', function(e) {{ e.preventDefault(); e.stopPropagation(); }});
            }}
            
            // 📍 GPS LOCATE
            if (locateBtn) {{
                locateBtn.addEventListener('click', function(e) {{
                    e.preventDefault(); e.stopPropagation();
                    if (!navigator.geolocation) {{ alert('Browser tidak mendukung GPS'); return; }}
                    locateBtn.innerHTML = '⏳';
                    navigator.geolocation.getCurrentPosition(
                        pos => {{ 
                            updateCoords(pos.coords.latitude, pos.coords.longitude, '<b>📍 Lokasi Anda (GPS)</b><br>Akurasi: ' + Math.round(pos.coords.accuracy) + 'm');
                            map.flyTo([pos.coords.latitude, pos.coords.longitude], 17);
                            locateBtn.innerHTML = '📍';
                        }},
                        err => {{ alert('Gagal: ' + err.message); locateBtn.innerHTML = '📍'; }},
                        {{enableHighAccuracy: true, timeout: 10000}}
                    );
                }});
            }}
            
            // ✏️ EDIT (DRAG) TOGGLE
            if (editBtn) {{
                editBtn.addEventListener('click', function(e) {{
                    e.preventDefault(); e.stopPropagation();
                    if (!marker) {{ alert('Tentukan lokasi dulu via 📍 GPS atau 🔍 Search'); return; }}
                    
                    isEditMode = !isEditMode;
                    if (isEditMode) {{
                        marker.dragging.enable();
                        editBtn.style.background = '#fff3cd';
                        editBtn.title = 'Selesai Edit (Klik Lagi)';
                        marker.bindPopup('<b>✏️ Mode Edit ON</b><br>Seret marker untuk fine-tune').openPopup();
                    }} else {{
                        marker.dragging.disable();
                        editBtn.style.background = 'white';
                        editBtn.title = 'Edit Titik Lokasi (Drag)';
                        var pos = marker.getLatLng();
                        marker.bindPopup('<b>🔒 Mode Edit OFF</b><br>Lat: ' + pos.lat.toFixed(5) + '<br>Lng: ' + pos.lng.toFixed(5)).openPopup();
                    }}
                }});
            }}
            
            // 🗑️ DELETE
            if (deleteBtn) {{
                deleteBtn.addEventListener('click', function(e) {{
                    e.preventDefault(); e.stopPropagation();
                    if (!marker) return;
                    if (confirm('Hapus titik ini?')) {{
                        map.removeLayer(marker);
                        marker = null;
                        hiddenInput.value = '';
                        isEditMode = false;
                        if (editBtn) editBtn.style.background = 'white';
                    }}
                }});
            }}
            
            // 🟢 LOAD EXISTING DATA
            function loadExistingData() {{
                var existingValue = hiddenInput.value;
                if (existingValue && existingValue.includes('POINT')) {{
                    console.log('🔄 [Edit Mode] Loading existing data');
                    var match = existingValue.match(/POINT\\s*\\(\\s*([\\d.\\-]+)\\s+([\\d.\\-]+)\\s*\\)/);
                    if (match) {{
                        var lng = parseFloat(match[1]);
                        var lat = parseFloat(match[2]);
                        if (!isNaN(lat) && !isNaN(lng)) {{
                            setTimeout(function() {{
                                map.setView([lat, lng], 16);
                                marker = L.marker([lat, lng], {{icon: customIcon, draggable: false}}).addTo(map);
                                marker.bindPopup('<b>📍 Data Existing</b><br>Lat: ' + lat.toFixed(5) + '<br>Lng: ' + lng.toFixed(5)).openPopup();
                            }}, 300);
                        }}
                    }}
                }}
            }}
            
            if (document.readyState === 'loading') {{
                document.addEventListener('DOMContentLoaded', loadExistingData);
            }} else {{
                setTimeout(loadExistingData, 200);
            }}
        }})();
        </script>
        """
        
        return mark_safe(html + init_html)