// Channel page functionality
document.addEventListener('DOMContentLoaded', function() {
    const subscribeBtn = document.querySelector('.btn-subscribe-channel');
    
    if (subscribeBtn) {
        subscribeBtn.addEventListener('click', async function(e) {
            e.stopPropagation();
            const channelName = this.getAttribute('data-channel');
            if (!channelName) return;
            
            try {
                const response = await fetch(`/api/subscribe/${channelName}`, {
                    method: 'POST',
                    headers: {
                        'Content-Type': 'application/json'
                    }
                });
                
                const data = await response.json();
                
                if (data.success) {
                    if (data.subscribed) {
                        this.textContent = 'Подписаны';
                        this.classList.add('subscribed');
                    } else {
                        this.textContent = 'Подписаться';
                        this.classList.remove('subscribed');
                    }
                }
            } catch (error) {
                console.error('Subscribe error:', error);
            }
        });
    }
});

