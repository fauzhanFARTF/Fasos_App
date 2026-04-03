# fasos/widgets.py
from django import forms
from django.utils.safestring import mark_safe


class SearchableLeafletWidget(forms.TextInput):
    """Widget GIS dengan Leaflet + Multi-Basemap + Search + Locate + Legend"""
    
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
        
        init_html = f"""
        <div style="margin-top: 10px;">
            <!-- ✅ Peta Lebar: min-width 750px -->
            <div id="{widget_id}_map" style="height: 450px; width: 100%; min-width: 750px; max-width: 100%; border: 1px solid #ccc; border-radius: 4px; position: relative;">
                
                <!-- Search Box (Atas Kiri) -->
                <div id="{widget_id}_search_container" style="position: absolute; top: 10px; left: 60px; z-index: 1000; background: white; padding: 5px; border-radius: 4px; box-shadow: 0 2px 5px rgba(0,0,0,0.3);">
                    <input type="text" id="{widget_id}_search" placeholder="Cari lokasi..." 
                           style="padding: 5px 10px; width: 250px; border: 1px solid #ddd; border-radius: 3px;">
                    <button type="button" id="{widget_id}_search_btn" 
                            style="padding: 5px 10px; background: #007bff; color: white; border: none; border-radius: 3px; cursor: pointer; margin-left: 5px;">🔍</button>
                </div>
                
                <!-- ✅ Control Buttons: VERTICAL di KIRI, di bawah Zoom -->
                <div id="{widget_id}_controls" style="position: absolute; top: 90px; left: 10px; z-index: 1000; display: flex; flex-direction: column; gap: 5px;">
                    <button type="button" id="{widget_id}_locate_btn" title="Gunakan lokasi saya"
                            style="width: 30px; height: 30px; background: white; border: 2px solid rgba(0,0,0,0.2); border-radius: 4px; cursor: pointer; font-size: 16px; box-shadow: 0 1px 5px rgba(0,0,0,0.4);">
                        📍
                    </button>
                    <button type="button" id="{widget_id}_edit_btn" title="Edit titik lokasi"
                            style="width: 30px; height: 30px; background: white; border: 2px solid rgba(0,0,0,0.2); border-radius: 4px; cursor: pointer; font-size: 16px; box-shadow: 0 1px 5px rgba(0,0,0,0.4);">
                        ✏️
                    </button>
                    <button type="button" id="{widget_id}_delete_btn" title="Hapus titik lokasi"
                            style="width: 30px; height: 30px; background: white; border: 2px solid rgba(0,0,0,0.2); border-radius: 4px; cursor: pointer; font-size: 16px; box-shadow: 0 1px 5px rgba(0,0,0,0.4);">
                        🗑️
                    </button>
                </div>
            </div>
            
            <!-- Legend HTML Container (Hidden by default, handled by Leaflet Control) -->
            <div id="{widget_id}_legend_html" style="display:none;">
                <h4 style="margin: 0 0 5px; color: #333; font-size: 13px; font-weight: bold; border-bottom: 1px solid #eee; padding-bottom: 3px;">
                    🗺️ Legenda Peta
                </h4>
                <div><span style="display:inline-block; width:12px; height:12px; background:#e74c3c; border-radius:50%; margin-right:6px;"></span> Titik Fasilitas</div>
                <div><span style="font-size:14px; margin-right:4px;">📍</span> Lokasi Anda (GPS)</div>
                <div><span style="font-size:14px; margin-right:4px;">🟡</span> Mode Edit (Seret)</div>
            </div>

            <div style="margin-top: 5px; color: #666; font-size: 12px;">
                💡 Klik peta untuk set lokasi | 📍 GPS | ️ Edit | 🗑️ Hapus | 📚 Ganti Basemap
            </div>
        </div>
        
        <script>
        window.addEventListener('load', function() {{
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
            
            if (!mapContainer || !hiddenInput) return;
            
            hiddenInput.type = 'hidden';
            hiddenInput.style.display = 'none';
            console.log('🗺️ [SearchableLeafletWidget] Ready');

            // Inisialisasi Peta
            var map = L.map(mapContainer).setView([-6.2088, 106.8456], 13);

            // 🌍 DEFINISI BASEMAPS
            var cartoLayer = L.tileLayer('https://{{s}}.basemaps.cartocdn.com/light_all/{{z}}/{{x}}/{{y}}{{r}}.png', {{
                attribution: '&copy; OpenStreetMap &copy; CARTO', subdomains: 'abcd', maxZoom: 20
            }});
            var satelliteLayer = L.tileLayer('https://server.arcgisonline.com/ArcGIS/rest/services/World_Imagery/MapServer/tile/{{z}}/{{y}}/{{x}}', {{
                attribution: 'Tiles &copy; Esri', maxZoom: 19
            }});
            var osmLayer = L.tileLayer('https://{{s}}.tile.openstreetmap.org/{{z}}/{{x}}/{{y}}.png', {{
                attribution: '&copy; OpenStreetMap contributors', maxZoom: 19
            }});

            cartoLayer.addTo(map);
            L.control.layers({{
                "🗺️ CartoDB (Bersih)": cartoLayer,
                "🛰️ Satellite (ESRI)": satelliteLayer,
                "🛣️ OpenStreetMap": osmLayer
            }}, null, {{ collapsed: true }}).addTo(map);
            
            // Scale Bar
            L.control.scale({{ position: 'bottomright', metric: true, imperial: true, maxWidth: 100 }}).addTo(map);

            // 🏆 TAMBAHKAN LEGENDA (Pojok Kiri Bawah)
            var legendContent = document.getElementById(widgetId + '_legend_html').innerHTML;
            var legend = L.control({{position: 'bottomleft'}});
            legend.onAdd = function (map) {{
                var div = L.DomUtil.create('div', 'info legend');
                div.innerHTML = legendContent;
                div.style.background = 'white';
                div.style.padding = '8px 10px';
                div.style.borderRadius = '5px';
                div.style.boxShadow = '0 0 15px rgba(0,0,0,0.2)';
                div.style.color = '#444';
                div.style.fontFamily = 'sans-serif';
                div.style.fontSize = '12px';
                div.style.lineHeight = '18px';
                return div;
            }};
            legend.addTo(map);

            // 🛠️ LOGIKA WIDGET
            var marker = null;
            var isEditMode = false;

            function updateCoords(lat, lng, source) {{
                if (!lat || !lng) return;
                hiddenInput.value = "POINT(" + lng + " " + lat + ")";
                if (marker) map.removeLayer(marker);
                marker = L.marker([lat, lng], {{draggable: false}}).addTo(map);
                
                marker.on('dragend', function(e) {{
                    var pos = e.target.getLatLng();
                    hiddenInput.value = "POINT(" + pos.lng + " " + pos.lat + ")";
                }});
                
                if (source !== 'edit_off' && source !== 'delete') {{
                    console.log('📍 Koordinat diset:', lat.toFixed(5), lng.toFixed(5));
                }}
            }}

            map.on('click', function(e) {{
                if (!isEditMode) updateCoords(e.latlng.lat, e.latlng.lng, 'click');
            }});

            // 🔍 Search
            async function searchLocation(e) {{
                if(e) e.stopPropagation();
                var query = searchInput.value.trim();
                if (!query) {{ alert('Masukkan nama lokasi'); return; }}
                try {{
                    var res = await fetch('https://nominatim.openstreetmap.org/search?format=json&q=' + encodeURIComponent(query));
                    var data = await res.json();
                    if (data.length > 0) {{
                        var lat = parseFloat(data[0].lat), lng = parseFloat(data[0].lon);
                        updateCoords(lat, lng, 'search');
                        map.flyTo([lat, lng], 16, {{animate: true, duration: 1.2}});
                        marker.bindPopup(data[0].display_name).openPopup();
                    }} else {{ alert('Lokasi tidak ditemukan'); }}
                }} catch (err) {{ console.error(err); alert('Error search'); }}
            }}
            
            searchBtn.addEventListener('click', e => {{ e.stopPropagation(); searchLocation(); }});
            searchInput.addEventListener('keypress', e => {{
                e.stopPropagation();
                if(e.key==='Enter') {{ e.preventDefault(); searchLocation(); }}
            }});
            searchContainer.addEventListener('click', e => e.stopPropagation());
            controlsDiv.addEventListener('click', e => e.stopPropagation());

            // 📍 Locate Me
            if (locateBtn) {{
                locateBtn.addEventListener('click', function(e) {{
                    e.stopPropagation();
                    if (!navigator.geolocation) {{ alert('Geolokasi tidak didukung'); return; }}
                    locateBtn.innerHTML = '⏳';
                    navigator.geolocation.getCurrentPosition(
                        pos => {{ 
                            var lat = pos.coords.latitude, lng = pos.coords.longitude;
                            updateCoords(lat, lng, 'gps');
                            map.flyTo([lat, lng], 17, {{animate: true, duration: 1.5}});
                            marker.bindPopup('📍 Lokasi Anda').openPopup();
                            locateBtn.innerHTML = '📍';
                        }},
                        err => {{ alert('Gagal: '+err.message); locateBtn.innerHTML = '📍'; }},
                        {{enableHighAccuracy: true, timeout: 10000}}
                    );
                }});
            }}

            // ✏️ Edit
            if (editBtn) {{
                editBtn.addEventListener('click', function(e) {{
                    e.stopPropagation();
                    if (!marker) {{ alert('Buat titik dulu di peta'); return; }}
                    isEditMode = !isEditMode;
                    if (isEditMode) {{
                        marker.dragging.enable();
                        editBtn.style.background = '#fff3cd';
                    }} else {{
                        marker.dragging.disable();
                        editBtn.style.background = 'white';
                    }}
                }});
            }}

            // 🗑️ Delete
            if (deleteBtn) {{
                deleteBtn.addEventListener('click', function(e) {{
                    e.stopPropagation();
                    if (!marker) {{ alert('Tidak ada titik'); return; }}
                    if (confirm('Hapus titik ini?')) {{
                        map.removeLayer(marker);
                        marker = null;
                        hiddenInput.value = '';
                        isEditMode = false;
                        editBtn.style.background = 'white';
                    }}
                }});
            }}

            // Load data awal
            if (hiddenInput.value && hiddenInput.value.startsWith('POINT(')) {{
                var c = hiddenInput.value.replace('POINT(', '').replace(')', '').split(' ');
                if (c.length === 2) updateCoords(parseFloat(c[1]), parseFloat(c[0]), 'init');
            }}
        }});
        </script>
        """
        
        return mark_safe(html + init_html)