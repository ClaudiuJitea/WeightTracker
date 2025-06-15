// Fasting Timer JavaScript

document.addEventListener('DOMContentLoaded', function() {
    try {
        // Check if we're on the fasting tracker page by looking for key elements
        const onFastingPage = Boolean(document.getElementById('fastingTimer') || 
                                      document.getElementById('startFastModal'));
        
        if (!onFastingPage) {
            // Skip execution if we're not on the fasting page
            return;
        }
        
        // Fasting timer functionality
        const fastingTimerElement = document.getElementById('fastingTimer');
        const fastingProgressElement = document.getElementById('fastingProgress');
        const progressBarElement = document.getElementById('progressBar');
        const startTimeElement = document.getElementById('fastStartTime');
        
        // Only run timer code if we have an active fast
        if (fastingTimerElement && startTimeElement) {
            try {
                const startTime = new Date(startTimeElement.dataset.startTime).getTime();
                const targetHours = parseFloat(startTimeElement.dataset.targetHours || 0);
                
                function updateTimer() {
                    const now = new Date().getTime();
                    const diff = Math.max(0, now - startTime) / 1000; // in seconds
                    
                    const hours = Math.floor(diff / 3600);
                    const minutes = Math.floor((diff % 3600) / 60);
                    
                    // Update timer display
                    if (fastingTimerElement) {
                        fastingTimerElement.textContent = `${String(hours).padStart(2, '0')}:${String(minutes).padStart(2, '0')}`;
                    }
                    
                    // Calculate and update progress if target hours exists
                    if (targetHours && fastingProgressElement && progressBarElement) {
                        const progress = Math.min(100, (diff / 3600 / targetHours) * 100);
                        fastingProgressElement.textContent = `${Math.round(progress)}% Complete`;
                        progressBarElement.style.width = `${progress}%`;
                    } else if (fastingProgressElement && progressBarElement) {
                        fastingProgressElement.textContent = `${hours}h ${minutes}m`;
                        progressBarElement.style.width = '100%';
                    }
                }
                
                // Update immediately and then every second
                updateTimer();
                setInterval(updateTimer, 1000);
            } catch (error) {
                console.error('Error initializing fasting timer:', error);
            }
        }
        
        // Toggle target hours input based on undefined checkbox
        const isUndefinedCheckbox = document.querySelector('input[name="is_undefined"]');
        
        // Only setup toggle if checkbox exists
        if (isUndefinedCheckbox) {
            const targetHoursContainer = document.getElementById('target_hours_container');
            const targetHoursInput = document.querySelector('input[name="target_hours"]');
            
            if (targetHoursContainer && targetHoursInput) {
                function toggleTargetHours() {
                    if (isUndefinedCheckbox.checked) {
                        targetHoursContainer.style.display = 'none';
                        targetHoursInput.value = '';
                    } else {
                        targetHoursContainer.style.display = 'block';
                    }
                }
                
                isUndefinedCheckbox.addEventListener('change', toggleTargetHours);
                toggleTargetHours(); // Initial state
            }
        }
    } catch (error) {
        console.error('Error in fasting timer script:', error);
        // Error is caught and logged, preventing script from breaking page
    }
}); 