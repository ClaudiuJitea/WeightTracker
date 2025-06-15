// Weight Chart JavaScript

// Toggle edit form visibility
function toggleEdit(entryId) {
    const weightText = document.getElementById(`weight-${entryId}`);
    const editForm = document.getElementById(`edit-form-${entryId}`);
    
    weightText.classList.toggle('hidden');
    editForm.classList.toggle('hidden');
}

function initializeChart(chartWeights, chartDates, chartGoalLine) {
    console.log('Initializing chart with:', { chartWeights, chartDates, chartGoalLine });
    
    // Ensure we have arrays
    chartWeights = Array.isArray(chartWeights) ? chartWeights : [];
    chartDates = Array.isArray(chartDates) ? chartDates : [];
    chartGoalLine = Array.isArray(chartGoalLine) ? chartGoalLine : [];
    
    const isDarkMode = document.documentElement.classList.contains('dark');
    const canvas = document.getElementById('weightChart');
    const ctx = canvas.getContext('2d');
    
    // Set canvas dimensions to match its container
    const container = canvas.parentElement;
    canvas.width = container.clientWidth;
    canvas.height = container.clientHeight;
    
    // Check if we have valid data
    if (chartWeights.length === 0 || chartDates.length === 0) {
        // Display a message on the canvas when no data is available
        ctx.clearRect(0, 0, canvas.width, canvas.height);
        ctx.font = '16px Arial';
        ctx.fillStyle = isDarkMode ? '#D1D5DB' : '#374151';
        ctx.textAlign = 'center';
        ctx.textBaseline = 'middle';
        ctx.fillText('No weight data available. Add weight entries to see your progress chart.', canvas.width / 2, canvas.height / 2);
        return null;
    }
    
    // Ensure all arrays have the same length
    const maxLength = Math.max(chartWeights.length, chartDates.length, chartGoalLine.length);
    
    // Pad arrays if needed
    if (chartDates.length < maxLength) {
        // Generate placeholder dates if needed
        for (let i = chartDates.length; i < maxLength; i++) {
            chartDates.push(`Date ${i+1}`);
        }
    }
    
    if (chartWeights.length < maxLength) {
        chartWeights = chartWeights.concat(Array(maxLength - chartWeights.length).fill(null));
    }
    
    if (chartGoalLine.length < maxLength) {
        chartGoalLine = chartGoalLine.concat(Array(maxLength - chartGoalLine.length).fill(null));
    }
    
    // Filter out any null or undefined values for display check
    const filteredData = chartWeights.filter(weight => weight !== null && weight !== undefined);
    
    if (filteredData.length === 0) {
        ctx.clearRect(0, 0, canvas.width, canvas.height);
        ctx.font = '16px Arial';
        ctx.fillStyle = isDarkMode ? '#D1D5DB' : '#374151';
        ctx.textAlign = 'center';
        ctx.textBaseline = 'middle';
        ctx.fillText('No weight data available. Add weight entries to see your progress chart.', canvas.width / 2, canvas.height / 2);
        return null;
    }
    
    const datasets = [{
        label: 'Weight (kg)',
        data: chartWeights,
        borderColor: '#9333EA',
        backgroundColor: '#9333EA20',
        fill: true,
        tension: 0.1,
        spanGaps: true
    }];

    if (chartGoalLine.length > 0 && chartGoalLine.some(value => value !== null && value !== undefined)) {
        datasets.push({
            label: 'Weight Goal',
            data: chartGoalLine,
            borderColor: '#10B981',
            backgroundColor: 'transparent',
            borderDash: [5, 5],
            fill: false,
            tension: 0,
            spanGaps: true
        });
    }

    const chartConfig = {
        type: 'line',
        data: {
            labels: chartDates,
            datasets: datasets
        },
        options: {
            responsive: true,
            maintainAspectRatio: false,
            scales: {
                y: {
                    beginAtZero: false,
                    grid: {
                        color: isDarkMode ? 'rgba(255, 255, 255, 0.1)' : 'rgba(0, 0, 0, 0.1)'
                    },
                    ticks: {
                        color: isDarkMode ? '#D1D5DB' : '#374151',
                        font: {
                            size: 12
                        }
                    }
                },
                x: {
                    grid: {
                        color: isDarkMode ? 'rgba(255, 255, 255, 0.1)' : 'rgba(0, 0, 0, 0.1)'
                    },
                    ticks: {
                        color: isDarkMode ? '#D1D5DB' : '#374151',
                        font: {
                            size: 12
                        },
                        maxRotation: 45,
                        minRotation: 45
                    }
                }
            },
            plugins: {
                legend: {
                    display: true,
                    labels: {
                        color: isDarkMode ? '#D1D5DB' : '#374151',
                        font: {
                            size: 14
                        }
                    }
                },
                tooltip: {
                    callbacks: {
                        label: function(context) {
                            if (context.dataset.label === 'Weight Goal') {
                                return `Goal: ${context.raw !== null && context.raw !== undefined ? parseFloat(context.raw).toFixed(1) : 'N/A'} kg`;
                            }
                            return `Weight: ${context.raw !== null && context.raw !== undefined ? parseFloat(context.raw) : 'N/A'} kg`;
                        }
                    }
                }
            }
        }
    };

    return new Chart(ctx, chartConfig);
}

// Update chart colors when theme changes
function setupThemeToggle(weightChart) {
    // Check if the chart was successfully created
    if (!weightChart) return;
    
    const themeToggle = document.getElementById('theme-toggle');
    if (!themeToggle) return;
    
    themeToggle.addEventListener('click', function() {
        const isDarkMode = document.documentElement.classList.contains('dark');
        
        weightChart.options.scales.y.grid.color = isDarkMode ? 'rgba(255, 255, 255, 0.1)' : 'rgba(0, 0, 0, 0.1)';
        weightChart.options.scales.x.grid.color = isDarkMode ? 'rgba(255, 255, 255, 0.1)' : 'rgba(0, 0, 0, 0.1)';
        weightChart.options.scales.y.ticks.color = isDarkMode ? '#D1D5DB' : '#374151';
        weightChart.options.scales.x.ticks.color = isDarkMode ? '#D1D5DB' : '#374151';
        weightChart.options.plugins.legend.labels.color = isDarkMode ? '#D1D5DB' : '#374151';
        weightChart.update();
    });
} 