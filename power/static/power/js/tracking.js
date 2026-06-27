function getCookie(name) {
    let cookieValue = null;
    if (document.cookie && document.cookie !== '') {
        const cookies = document.cookie.split(';');
        for (let i = 0; i < cookies.length; i++) {
            const cookie = cookies[i].trim();
            if (cookie.substring(0, name.length + 1) === (name + '=')) {
                cookieValue = decodeURIComponent(cookie.substring(name.length + 1));
                break;
            }
        }
    }
    return cookieValue;
}

function initTrackingMap(config) {
    const map = L.map('tracking-map').setView(
        [config.outageLat || 28.6139, config.outageLng || 77.2090],
        13
    );

    L.tileLayer('https://{s}.tile.openstreetmap.org/{z}/{x}/{y}.png', {
        attribution: '&copy; OpenStreetMap contributors',
        maxZoom: 19,
    }).addTo(map);

    const outageIcon = L.divIcon({
        html: '<div style="background:#dc2626;width:32px;height:32px;border-radius:50%;border:3px solid white;box-shadow:0 2px 8px rgba(0,0,0,0.3);display:flex;align-items:center;justify-content:center;font-size:16px;">⚡</div>',
        className: '',
        iconSize: [32, 32],
        iconAnchor: [16, 16],
    });

    const electricianIcon = L.divIcon({
        html: '<div style="background:#1a56db;width:36px;height:36px;border-radius:50%;border:3px solid white;box-shadow:0 2px 8px rgba(0,0,0,0.3);display:flex;align-items:center;justify-content:center;font-size:18px;">🔧</div>',
        className: '',
        iconSize: [36, 36],
        iconAnchor: [18, 18],
    });

    const outageMarker = L.marker(
        [config.outageLat, config.outageLng],
        { icon: outageIcon }
    ).addTo(map).bindPopup('<b>Outage Location</b><br>' + (config.outageAddress || ''));

    let electricianMarker = null;
    let routeLine = null;

    function updateMap(data) {
        if (data.latitude && data.longitude) {
            if (electricianMarker) {
                electricianMarker.setLatLng([data.latitude, data.longitude]);
            } else {
                electricianMarker = L.marker(
                    [data.latitude, data.longitude],
                    { icon: electricianIcon }
                ).addTo(map).bindPopup('<b>' + data.electrician_name + '</b><br>📞 ' + data.electrician_phone);
            }

            if (routeLine) {
                map.removeLayer(routeLine);
            }
            routeLine = L.polyline(
                [[data.latitude, data.longitude], [data.outage_latitude, data.outage_longitude]],
                { color: '#1a56db', weight: 3, dashArray: '10, 10', opacity: 0.7 }
            ).addTo(map);

            const group = L.featureGroup([outageMarker, electricianMarker]);
            map.fitBounds(group.getBounds().pad(0.2));
        }

        const statusEl = document.getElementById('live-status');
        if (statusEl && data.status) {
            statusEl.textContent = data.status.replace(/_/g, ' ').replace(/\b\w/g, l => l.toUpperCase());
        }
    }

    function fetchLocation() {
        fetch(config.trackUrl)
            .then(r => r.json())
            .then(data => {
                if (!data.error) {
                    updateMap(data);
                }
            })
            .catch(err => console.error('Tracking error:', err));
    }

    fetchLocation();
    setInterval(fetchLocation, 3000);

    if (config.simulateUrl) {
        setInterval(() => {
            const formData = new FormData();
            formData.append('target_lat', config.outageLat);
            formData.append('target_lng', config.outageLng);
            fetch(config.simulateUrl, {
                method: 'POST',
                headers: { 'X-CSRFToken': getCookie('csrftoken') },
                body: formData,
            })
                .then(r => r.json())
                .then(data => {
                    if (!data.error) {
                        fetchLocation();
                    }
                });
        }, 4000);
    }
}

function initReportMap() {
    const mapEl = document.getElementById('report-map');
    if (!mapEl) return;

    const defaultLat = 28.6139;
    const defaultLng = 77.2090;

    const map = L.map('report-map').setView([defaultLat, defaultLng], 13);

    L.tileLayer('https://{s}.tile.openstreetmap.org/{z}/{x}/{y}.png', {
        attribution: '&copy; OpenStreetMap contributors',
        maxZoom: 19,
    }).addTo(map);

    let marker = L.marker([defaultLat, defaultLng], { draggable: true }).addTo(map);

    document.getElementById('id_latitude').value = defaultLat;
    document.getElementById('id_longitude').value = defaultLng;

    marker.on('dragend', function () {
        const pos = marker.getLatLng();
        document.getElementById('id_latitude').value = pos.lat.toFixed(6);
        document.getElementById('id_longitude').value = pos.lng.toFixed(6);
    });

    map.on('click', function (e) {
        marker.setLatLng(e.latlng);
        document.getElementById('id_latitude').value = e.latlng.lat.toFixed(6);
        document.getElementById('id_longitude').value = e.latlng.lng.toFixed(6);
    });

    if (navigator.geolocation) {
        navigator.geolocation.getCurrentPosition(function (pos) {
            const lat = pos.coords.latitude;
            const lng = pos.coords.longitude;
            map.setView([lat, lng], 15);
            marker.setLatLng([lat, lng]);
            document.getElementById('id_latitude').value = lat.toFixed(6);
            document.getElementById('id_longitude').value = lng.toFixed(6);
        });
    }
}

function initElectricianMap() {
    const mapEl = document.getElementById('electrician-map');
    if (!mapEl) return;

    const defaultLat = 28.6139;
    const defaultLng = 77.2090;

    const map = L.map('electrician-map').setView([defaultLat, defaultLng], 13);

    L.tileLayer('https://{s}.tile.openstreetmap.org/{z}/{x}/{y}.png', {
        attribution: '&copy; OpenStreetMap contributors',
        maxZoom: 19,
    }).addTo(map);

    let marker = L.marker([defaultLat, defaultLng], { draggable: true }).addTo(map);

    document.getElementById('id_current_latitude').value = defaultLat;
    document.getElementById('id_current_longitude').value = defaultLng;

    marker.on('dragend', function () {
        const pos = marker.getLatLng();
        document.getElementById('id_current_latitude').value = pos.lat.toFixed(6);
        document.getElementById('id_current_longitude').value = pos.lng.toFixed(6);
    });

    map.on('click', function (e) {
        marker.setLatLng(e.latlng);
        document.getElementById('id_current_latitude').value = e.latlng.lat.toFixed(6);
        document.getElementById('id_current_longitude').value = e.latlng.lng.toFixed(6);
    });
}

document.addEventListener('DOMContentLoaded', function () {
    initReportMap();
    initElectricianMap();
});
