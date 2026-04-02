/**
 * GPS and Google Maps functionality for Tshwane Report
 * Handles geolocation capture, address lookup, and map display
 * Uses Google Maps API with a draggable pin
 */

(function() {
    'use strict';

    // DOM Elements
    const gpsStatus = document.getElementById('gps-status');
    const mapCoords = document.getElementById('map-coords');
    const mapContainer = document.getElementById('map-container');
    const googleMapDiv = document.getElementById('google-map');
    const mapLink = document.getElementById('map-link');
    const openInGoogleMaps = document.getElementById('open-in-google-maps');
    const summaryAddress = document.getElementById('summary-address');
    const submitBtn = document.getElementById('submit-btn');
    const dragHint = document.getElementById('drag-hint');

    // Hidden form fields
    const latitudeInput = document.getElementById('id_latitude');
    const longitudeInput = document.getElementById('id_longitude');
    const addressInput = document.getElementById('id_address');

    // Global variables
    let map = null;
    let marker = null;
    let manualMode = false;

    /**
     * Initialize Google Map with draggable pin
     */
    function initGoogleMap(lat, lng) {
        if (!googleMapDiv || typeof google === 'undefined' || typeof google.maps === 'undefined') {
            console.warn('Google Maps API not loaded');
            return;
        }

        // Show map container
        if (mapContainer) {
            mapContainer.style.display = 'block';
        }

        // Show drag hint
        if (dragHint) {
            dragHint.style.display = 'block';
        }

        // Create map centered on location
        const position = new google.maps.LatLng(lat, lng);
        map = new google.maps.Map(googleMapDiv, {
            center: position,
            zoom: 17,
            mapTypeControl: false,
            streetViewControl: false,
            fullscreenControl: false
        });

        // Add draggable marker at location
        marker = new google.maps.Marker({
            position: position,
            map: map,
            draggable: true,
            animation: google.maps.Animation.DROP,
            title: 'Drag me to the exact fault location'
        });

        // Info window for marker
        const infoWindow = new google.maps.InfoWindow({
            content: '<div style="text-align:center;padding:4px;"><strong>Your Location</strong><br><small>Drag pin to exact fault location</small></div>'
        });
        infoWindow.open(map, marker);

        // Handle marker drag end
        google.maps.event.addListener(marker, 'dragend', function(event) {
            const newLat = event.latLng.lat();
            const newLng = event.latLng.lng();

            // Update form values
            if (latitudeInput) latitudeInput.value = newLat;
            if (longitudeInput) longitudeInput.value = newLng;

            // Update coordinates display
            if (mapCoords) {
                mapCoords.innerHTML = '<strong>Location updated!</strong><br><small>Lat: ' + newLat.toFixed(6) + ', Lng: ' + newLng.toFixed(6) + '</small>';
                mapCoords.className = 'gps-success';
            }

            // Update summary
            if (summaryAddress) {
                summaryAddress.textContent = newLat.toFixed(6) + ', ' + newLng.toFixed(6);
            }

            // Update map link
            if (mapLink && openInGoogleMaps) {
                openInGoogleMaps.href = 'https://www.google.com/maps?q=' + newLat + ',' + newLng;
            }

            // Reverse geocode new position
            reverseGeocode(newLat, newLng);

            // Close and reopen info window at new position
            infoWindow.close();
            infoWindow.setContent('<div style="text-align:center;padding:4px;"><strong>Pin moved</strong><br><small>Lat: ' + newLat.toFixed(6) + ', Lng: ' + newLng.toFixed(6) + '</small></div>');
            infoWindow.open(map, marker);
        });

        // Handle marker drag start
        google.maps.event.addListener(marker, 'dragstart', function() {
            infoWindow.close();
            if (mapCoords) {
                mapCoords.innerHTML = '📌 Dragging...';
            }
        });

        // Update map link
        if (mapLink && openInGoogleMaps) {
            mapLink.style.display = 'block';
            openInGoogleMaps.href = 'https://www.google.com/maps?q=' + lat + ',' + lng;
        }
    }

    // Expose for callback
    window.initGoogleMap = function() {
        // If we already have coordinates, init map with them
        if (latitudeInput && latitudeInput.value && longitudeInput && longitudeInput.value) {
            const lat = parseFloat(latitudeInput.value);
            const lng = parseFloat(longitudeInput.value);
            initGoogleMap(lat, lng);
        }
    };

    /**
     * Initialize GPS on page load
     */
    function init() {
        // Check if geolocation is available
        if (!('geolocation' in navigator)) {
            showError('Geolocation not supported by your browser');
            return;
        }

        // Auto-start GPS detection
        detectLocation();
    }

    /**
     * Detect user's location using Geolocation API
     */
    function detectLocation() {
        showLoading();

        navigator.geolocation.getCurrentPosition(
            onLocationSuccess,
            onLocationError,
            {
                enableHighAccuracy: true,
                timeout: 15000,
                maximumAge: 0
            }
        );
    }

    /**
     * Handle successful location detection
     */
    function onLocationSuccess(position) {
        const lat = position.coords.latitude;
        const lng = position.coords.longitude;

        // Update display
        if (mapCoords) {
            mapCoords.innerHTML = '<strong>Location captured!</strong><br><small>Lat: ' + lat.toFixed(6) + ', Lng: ' + lng.toFixed(6) + '</small>';
            mapCoords.className = 'gps-success';
        }

        // Set form values
        if (latitudeInput) latitudeInput.value = lat;
        if (longitudeInput) longitudeInput.value = lng;

        // Initialize Google Map
        initGoogleMap(lat, lng);

        // Try to get address
        reverseGeocode(lat, lng);

        // Enable submit button
        enableSubmit();

        // Update summary
        if (summaryAddress) {
            summaryAddress.textContent = 'GPS location captured';
        }
    }

    /**
     * Handle location detection errors
     */
    function onLocationError(error) {
        console.warn('Geolocation error:', error.message);

        let message = 'Could not detect location';
        switch (error.code) {
            case error.PERMISSION_DENIED:
                message = '❌ Location access denied. Please enable location services in your browser settings.';
                break;
            case error.POSITION_UNAVAILABLE:
                message = '❌ Location information unavailable. Please try again or enter address manually.';
                break;
            case error.TIMEOUT:
                message = '❌ Location request timed out. Please try again or enter address manually.';
                break;
        }

        showError(message);

        // Show manual entry option
        setTimeout(function() {
            toggleManual();
        }, 500);
    }

    /**
     * Reverse geocode coordinates to address using Nominatim
     */
    function reverseGeocode(lat, lng) {
        const url = 'https://nominatim.openstreetmap.org/reverse?format=json&lat=' + lat + '&lon=' + lng + '&zoom=18&addressdetails=1';

        fetch(url, {
            headers: {
                'Accept': 'application/json',
                'User-Agent': 'TshwaneReport/1.0'
            }
        })
        .then(function(response) { return response.json(); })
        .then(function(data) {
            if (data && data.display_name) {
                const address = data.display_name;

                // Update address input
                if (addressInput && !addressInput.value) {
                    addressInput.value = address;
                }

                // Update summary
                if (summaryAddress) {
                    summaryAddress.textContent = truncateAddress(address, 50);
                }

                // Update map coordinates display with address
                if (mapCoords) {
                    mapCoords.innerHTML = '<strong>Location found!</strong><br><small>' + truncateAddress(address, 60) + '</small>';
                }
            }
        })
        .catch(function(err) {
            console.warn('Reverse geocoding failed:', err);
        });
    }

    /**
     * Truncate address for display
     */
    function truncateAddress(address, maxLength) {
        if (address.length <= maxLength) return address;
        return address.substring(0, maxLength) + '...';
    }

    /**
     * Show loading state
     */
    function showLoading() {
        if (gpsStatus) {
            gpsStatus.innerHTML = '📡 Detecting your location...';
            gpsStatus.className = 'gps-loading';
        }
    }

    /**
     * Show error state
     */
    function showError(message) {
        if (gpsStatus) {
            gpsStatus.innerHTML = message + '<br><button type="button" onclick="retryGPS()" class="btn btn--sm btn--outline" style="margin-top:8px;">🔄 Retry GPS</button>';
            gpsStatus.className = 'gps-error';
        }
    }

    /**
     * Enable submit button
     */
    function enableSubmit() {
        if (submitBtn) {
            submitBtn.disabled = false;
            submitBtn.classList.remove('btn--disabled');
        }
    }

    /**
     * Toggle manual address input
     */
    window.toggleManual = function() {
        manualMode = !manualMode;
        const manualDiv = document.getElementById('manual-address');
        const manualBtn = document.querySelector('[onclick="toggleManual()"]');

        if (manualDiv) {
            manualDiv.style.display = manualMode ? 'block' : 'none';
        }

        if (manualBtn) {
            manualBtn.textContent = manualMode ? '📍 Use GPS instead' : '✏️ Enter address manually';
        }

        // If entering manual mode, enable submit
        if (manualMode) {
            enableSubmit();
        }
    };

    /**
     * Set manual address
     */
    window.setManualAddress = function(address) {
        if (addressInput) {
            addressInput.value = address;
        }
        if (summaryAddress) {
            summaryAddress.textContent = address || 'Manual address entered';
        }
        if (address && address.trim()) {
            enableSubmit();

            // Update hint text
            const submitHint = document.getElementById('submit-hint');
            if (submitHint) {
                submitHint.textContent = '✅ Address entered. You can now submit your report.';
                submitHint.style.color = 'var(--success-green, #28a745)';
            }

            // Update map display
            if (mapCoords) {
                mapCoords.innerHTML = '<strong>Manual address entered</strong><br><small>' + truncateAddress(address, 60) + '</small>';
                mapCoords.className = 'gps-success';
            }

            // Update GPS status
            if (gpsStatus) {
                gpsStatus.innerHTML = '✅ Address entered manually';
                gpsStatus.className = 'gps-success';
            }
        }
    };

    /**
     * Clear photo preview
     */
    window.clearPhoto = function() {
        const photoInput = document.getElementById('id_photo');
        const previewDiv = document.getElementById('photo-preview');
        const previewImg = document.getElementById('preview-img');

        if (photoInput) photoInput.value = '';
        if (previewDiv) previewDiv.style.display = 'none';
        if (previewImg) previewImg.src = '';
    };

    /**
     * Text-to-speech for simplified mode
     */
    window.speak = function(text) {
        if ('speechSynthesis' in window) {
            window.speechSynthesis.cancel();
            const utterance = new SpeechSynthesisUtterance(text);
            utterance.lang = 'en-ZA';
            utterance.rate = 0.9;
            window.speechSynthesis.speak(utterance);
        }
    };

    /**
     * Retry GPS detection
     */
    window.retryGPS = function() {
        detectLocation();
    };

    // Initialize on DOM ready
    if (document.readyState === 'loading') {
        document.addEventListener('DOMContentLoaded', init);
    } else {
        init();
    }

})();
