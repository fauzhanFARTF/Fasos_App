# fasos/widgets.py
from django import forms
from django.utils.safestring import mark_safe


class SearchableLeafletWidget(forms.TextInput):
    """Widget GIS dengan Leaflet + Search menggunakan Nominatim"""
    
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
            <div id="{widget_id}_map" style="height: 450px; width: 100%; border: 1px solid #ccc; border-radius: 4px; position: relative;">
                <!-- Search Box -->
                <div style="position: absolute; top: 10px; left: 50px; z-index: 1000; background: white; padding: 5px; border-radius: 4px; box-shadow: 0 2px 5px rgba(0,0,0,0.3);">
                    <input type="text" id="{widget_id}_search" placeholder="Cari lokasi..." 
                           style="padding: 5px 10px; width: 250px; border: 1px solid #ddd; border-radius: 3px;">
                    <button type="button" id="{widget_id}_search_btn" 
                            style="padding: 5px 10px; background: #007bff; color: white; border: none; border-radius: 3px; cursor: pointer; margin-left: 5px;">
                        🔍 Cari
                    </button>
                </div>
            </div>
            <div style="margin-top: 5px; color: #666; font-size: 12px;">
                💡 Klik pada peta atau gunakan search box di atas untuk menentukan lokasi
            </div>
        </div>
        
        <script>
        window.addEventListener('load', function() {{
            console.log('🗺️ [SearchableLeafletWidget] Initializing for field: {name}');
            
            var widgetId = '{widget_id}';
            var mapContainer = document.getElementById(widgetId + '_map');
            var hiddenInput = document.getElementById(widgetId);
            var searchInput = document.getElementById(widgetId + '_search');
            var searchBtn = document.getElementById(widgetId + '_search_btn');
            
            if (!mapContainer || !hiddenInput) {{
                console.error('❌ Elements not found');
                return;
            }}
            
            console.log('✅ Elements found. Initializing Leaflet...');

            // Inisialisasi Peta
            var map = L.map(mapContainer).setView([-6.2088, 106.8456], 13);
            L.tileLayer('https://{{s}}.basemaps.cartocdn.com/light_all/{{z}}/{{x}}/{{y}}{{r}}.png', {{
                attribution: '&copy; OpenStreetMap &copy; CARTO',
                subdomains: 'abcd',
                maxZoom: 20
            }}).addTo(map);

            var marker = null;

            function updateCoords(lat, lng) {{
                hiddenInput.value = "POINT(" + lng + " " + lat + ")";
                if (marker) map.removeLayer(marker);
                marker = L.marker([lat, lng]).addTo(map);
                console.log('📍 Koordinat:', lat, lng);
            }}

            map.on('click', function(e) {{
                updateCoords(e.latlng.lat, e.latlng.lng);
            }});

            // Fungsi Search menggunakan Nominatim API
            async function searchLocation() {{
                var query = searchInput.value.trim();
                if (!query) {{
                    alert('Masukkan nama lokasi untuk dicari');
                    return;
                }}
                
                console.log('🔍 Searching for:', query);
                
                try {{
                    var response = await fetch('https://nominatim.openstreetmap.org/search?format=json&q=' + encodeURIComponent(query));
                    var data = await response.json();
                    
                    if (data.length > 0) {{
                        var lat = parseFloat(data[0].lat);
                        var lng = parseFloat(data[0].lon);
                        
                        console.log('✅ Found:', data[0].display_name);
                        updateCoords(lat, lng);
                        map.setView([lat, lng], 16);
                        
                        // Tampilkan popup
                        marker.bindPopup(data[0].display_name).openPopup();
                    }} else {{
                        alert('Lokasi tidak ditemukan. Coba kata kunci lain.');
                    }}
                }} catch (error) {{
                    console.error('❌ Search error:', error);
                    alert('Terjadi kesalahan saat mencari lokasi');
                }}
            }}

            // Event listener untuk search button
            if (searchBtn) {{
                searchBtn.addEventListener('click', searchLocation);
            }}
            
            // Event listener untuk Enter key
            if (searchInput) {{
                searchInput.addEventListener('keypress', function(e) {{
                    if (e.key === 'Enter') {{
                        e.preventDefault();
                        searchLocation();
                    }}
                }});
            }}

            // Load data awal
            if (hiddenInput.value && hiddenInput.value.startsWith('POINT(')) {{
                var coords = hiddenInput.value.replace('POINT(', '').replace(')', '').split(' ');
                if (coords.length === 2) {{
                    var lat = parseFloat(coords[1]);
                    var lng = parseFloat(coords[0]);
                    updateCoords(lat, lng);
                    map.setView([lat, lng], 15);
                }}
            }}
            
            // Sembunyikan input text
            hiddenInput.style.display = 'none';
        }});
        </script>
        """
        
        return mark_safe(html + init_html)