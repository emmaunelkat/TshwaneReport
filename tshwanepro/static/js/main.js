/**
 * TshwaneReport - Main JavaScript
 */

(function() {
    'use strict';

    // ================================================
    // Language Configuration
    // ================================================
    const LANG = document.documentElement.lang || 'en';

    // ================================================
    // Text-to-Speech for Simplified Mode
    // ================================================
    window.speak = function(text) {
        if ('speechSynthesis' in window) {
            // Cancel any ongoing speech
            window.speechSynthesis.cancel();
            
            const utterance = new SpeechSynthesisUtterance(text);
            utterance.lang = LANG === 'zu' ? 'zu-ZA' :
                           LANG === 'st' ? 'st-ZA' :
                           LANG === 'af' ? 'af-ZA' : 'en-ZA';
            utterance.rate = 0.9;
            utterance.pitch = 1;
            window.speechSynthesis.speak(utterance);
        }
    };

    // ================================================
    // GPS Functions
    // ================================================
    window.getLocation = function() {
        if ('geolocation' in navigator) {
            navigator.geolocation.getCurrentPosition(
                function(position) {
                    const lat = position.coords.latitude;
                    const lng = position.coords.longitude;
                    
                    // Set form values
                    const latInput = document.getElementById('id_latitude');
                    const lngInput = document.getElementById('id_longitude');
                    
                    if (latInput) latInput.value = lat;
                    if (lngInput) lngInput.value = lng;
                    
                    // Show success
                    const gpsStatus = document.getElementById('gps-status');
                    if (gpsStatus) {
                        gpsStatus.textContent = 'Location captured';
                        gpsStatus.className = 'status-badge status-badge--success';
                    }
                    
                    // Reverse geocode
                    reverseGeocode(lat, lng);
                },
                function(error) {
                    console.warn('Geolocation error:', error);
                    const gpsStatus = document.getElementById('gps-status');
                    if (gpsStatus) {
                        gpsStatus.textContent = 'Location unavailable';
                        gpsStatus.className = 'status-badge status-badge--warning';
                    }
                }
            );
        }
    };

    function reverseGeocode(lat, lng) {
        const url = `https://nominatim.openstreetmap.org/reverse?format=json&lat=${lat}&lon=${lng}`;
        
        fetch(url)
            .then(response => response.json())
            .then(data => {
                if (data && data.display_name) {
                    const addressInput = document.getElementById('id_address');
                    if (addressInput) {
                        addressInput.value = data.display_name;
                    }
                }
            })
            .catch(err => {
                console.warn('Reverse geocoding failed:', err);
            });
    }

    // ================================================
    // Photo Preview
    // ================================================
    function initPhotoPreview() {
        const photoInput = document.getElementById('id_photo');
        const previewContainer = document.getElementById('photo-preview');
        const previewImg = document.getElementById('preview-img');
        const clearBtn = document.getElementById('clear-photo');

        if (photoInput && previewImg && previewContainer) {
            photoInput.addEventListener('change', function(event) {
                const file = event.target.files[0];
                if (file) {
                    const reader = new FileReader();
                    reader.onload = function(e) {
                        previewImg.src = e.target.result;
                        previewContainer.style.display = 'block';
                    };
                    reader.readAsDataURL(file);
                }
            });
        }

        if (clearBtn) {
            clearBtn.addEventListener('click', function() {
                if (photoInput) photoInput.value = '';
                if (previewContainer) previewContainer.style.display = 'none';
                if (previewImg) previewImg.src = '';
            });
        }
    }

    // ================================================
    // Form Validation
    // ================================================
    function initFormValidation() {
        const form = document.querySelector('form');
        if (!form) return;

        // Only apply location validation to report forms (not tracking forms)
        const latInput = document.getElementById('id_latitude');
        const lngInput = document.getElementById('id_longitude');
        const addressInput = document.getElementById('id_address');
        
        // If this is not a report form (no location fields), skip location validation
        const isReportForm = latInput && lngInput && addressInput;
        if (!isReportForm) return;

        form.addEventListener('submit', function(event) {
            // Check if location is provided (either GPS coordinates OR manual address)
            const hasGPS = latInput.value && lngInput.value;
            const hasManualAddress = addressInput.value.trim();

            if (!hasGPS && !hasManualAddress) {
                event.preventDefault();
                alert('Please capture your location using GPS or enter your address manually before submitting.');
                return false;
            }

            // Check if description is provided
            const descInput = document.getElementById('id_description');
            if (descInput && !descInput.value.trim()) {
                event.preventDefault();
                alert('Please provide a description of the issue.');
                descInput.focus();
                return false;
            }

            return true;
        });
    }

    // ================================================
    // GPS Overlay Functions
    // ================================================
    window.showGpsInfo = function() {
        const overlay = document.getElementById('gps-overlay');
        if (overlay) overlay.style.display = 'flex';
    };

    window.dismissOverlay = function() {
        const overlay = document.getElementById('gps-overlay');
        if (overlay) overlay.style.display = 'none';
    };

    window.allowLocation = function() {
        const overlay = document.getElementById('gps-overlay');
        if (overlay) overlay.style.display = 'none';
        if (typeof getLocation === 'function') {
            getLocation();
        }
    };

    // ================================================
    // Tracking Form
    // ================================================
    function initTrackingForm() {
        const searchForm = document.querySelector('.search-box');
        if (searchForm) {
            searchForm.addEventListener('submit', function(event) {
                const trackingInput = document.getElementById('tracking-id-input');
                if (trackingInput && !trackingInput.value.trim()) {
                    event.preventDefault();
                    alert('Please enter a tracking ID');
                    trackingInput.focus();
                }
            });
        }
    }

    // ================================================
    // Initialize on DOM Ready
    // ================================================
    function init() {
        initPhotoPreview();
        initFormValidation();
        initTrackingForm();

        // Auto-trigger GPS on report form pages
        const reportForm = document.querySelector('.report-form');
        if (reportForm) {
            setTimeout(function() {
                if (typeof getLocation === 'function') {
                    getLocation();
                }
            }, 1000);
        }
    }

    // Run on DOM ready
    if (document.readyState === 'loading') {
        document.addEventListener('DOMContentLoaded', init);
    } else {
        init();
    }

})();
