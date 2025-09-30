document.addEventListener('DOMContentLoaded', function() {

    const alerts = document.querySelectorAll('.alert');
    alerts.forEach(alert => {
        setTimeout(() => {
            const bsAlert = new bootstrap.Alert(alert);
            bsAlert.close();
        }, 5000);
    });


    const countrySelect = document.getElementById('id_country');
    const stateSelect = document.getElementById('id_state');
    const districtSelect = document.getElementById('id_district');

    if (countrySelect) {
        countrySelect.addEventListener('change', function() {
            const countryId = this.value;
            if (countryId) {
                fetch(`/users/get-states/?country_id=${countryId}`)
                    .then(response => response.json())
                    .then(data => {
                        stateSelect.innerHTML = '<option value="">Select State</option>';
                        districtSelect.innerHTML = '<option value="">Select District</option>';
                        data.forEach(state => {
                            stateSelect.innerHTML += `<option value="${state.id}">${state.name}</option>`;
                        });
                    });
            }
        });
    }

    if (stateSelect) {
        stateSelect.addEventListener('change', function() {
            const stateId = this.value;
            if (stateId) {
                fetch(`/users/get-districts/?state_id=${stateId}`)
                    .then(response => response.json())
                    .then(data => {
                        districtSelect.innerHTML = '<option value="">Select District</option>';
                        data.forEach(district => {
                            districtSelect.innerHTML += `<option value="${district.id}">${district.name}</option>`;
                        });
                    });
            }
        });
    }


    const videoPlayer = document.getElementById('video-player');
    if (videoPlayer) {
        videoPlayer.addEventListener('timeupdate', function() {
            const currentTime = this.currentTime;
            const duration = this.duration;
            const progress = (currentTime / duration) * 100;

            // Update progress bar if exists
            const progressBar = document.getElementById('video-progress');
            if (progressBar) {
                progressBar.style.width = `${progress}%`;
            }
        });
    }
});


function formatTime(seconds) {
    const mins = Math.floor(seconds / 60);
    const secs = Math.floor(seconds % 60);
    return `${mins}:${secs.toString().padStart(2, '0')}`;
}