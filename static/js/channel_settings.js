// Channel settings functionality
document.addEventListener('DOMContentLoaded', function() {
    const settingsForm = document.getElementById('channel-settings-form');
    
    if (settingsForm) {
        settingsForm.addEventListener('submit', async function(e) {
            e.preventDefault();
            
            const channelName = document.getElementById('channel-name').value;
            const description = document.getElementById('channel-description').value;
            
            try {
                const response = await fetch('/channel/settings', {
                    method: 'POST',
                    headers: {
                        'Content-Type': 'application/json'
                    },
                    body: JSON.stringify({
                        channel_name: channelName,
                        description: description
                    })
                });
                
                const data = await response.json();
                
                if (data.success) {
                    alert('Настройки сохранены!');
                    window.location.href = `/channel/${data.username || 'current'}`;
                } else {
                    alert('Ошибка при сохранении: ' + (data.error || 'Неизвестная ошибка'));
                }
            } catch (error) {
                console.error('Settings error:', error);
                alert('Ошибка соединения с сервером');
            }
        });
    }
});

