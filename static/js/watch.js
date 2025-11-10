// Watch page functionality
document.addEventListener('DOMContentLoaded', function() {
    const videoPlayer = document.getElementById('video-player');
    const likeBtn = document.querySelector('.btn-like');
    const dislikeBtn = document.querySelector('.btn-dislike');
    const shareBtn = document.querySelector('.btn-share');
    const subscribeBtn = document.querySelector('.btn-subscribe');
    const watchLaterBtn = document.querySelector('.btn-watch-later');
    
    // Like functionality
    if (likeBtn) {
        likeBtn.addEventListener('click', async function(e) {
            e.stopPropagation();
            const videoId = this.getAttribute('data-video-id');
            
            try {
                const response = await fetch(`/api/like/${videoId}`, {
                    method: 'POST',
                    headers: {
                        'Content-Type': 'application/json'
                    },
                    body: JSON.stringify({ is_like: true })
                });
                
                const data = await response.json();
                
                if (data.success) {
                    const likeCount = likeBtn.querySelector('.like-count');
                    const dislikeCount = dislikeBtn.querySelector('.dislike-count');
                    
                    if (likeCount) likeCount.textContent = data.likes;
                    if (dislikeCount) dislikeCount.textContent = data.dislikes;
                    
                    // Обновляем активное состояние
                    if (likeBtn.classList.contains('active')) {
                        likeBtn.classList.remove('active');
                    } else {
                        likeBtn.classList.add('active');
                        dislikeBtn.classList.remove('active');
                    }
                }
            } catch (error) {
                console.error('Like error:', error);
            }
        });
    }
    
    // Dislike functionality
    if (dislikeBtn) {
        dislikeBtn.addEventListener('click', async function(e) {
            e.stopPropagation();
            const videoId = this.getAttribute('data-video-id');
            
            try {
                const response = await fetch(`/api/like/${videoId}`, {
                    method: 'POST',
                    headers: {
                        'Content-Type': 'application/json'
                    },
                    body: JSON.stringify({ is_like: false })
                });
                
                const data = await response.json();
                
                if (data.success) {
                    const likeCount = likeBtn.querySelector('.like-count');
                    const dislikeCount = dislikeBtn.querySelector('.dislike-count');
                    
                    if (likeCount) likeCount.textContent = data.likes;
                    if (dislikeCount) dislikeCount.textContent = data.dislikes;
                    
                    // Обновляем активное состояние
                    if (dislikeBtn.classList.contains('active')) {
                        dislikeBtn.classList.remove('active');
                    } else {
                        dislikeBtn.classList.add('active');
                        likeBtn.classList.remove('active');
                    }
                }
            } catch (error) {
                console.error('Dislike error:', error);
            }
        });
    }
    
    // Watch Later functionality
    if (watchLaterBtn) {
        watchLaterBtn.addEventListener('click', async function(e) {
            e.stopPropagation();
            const videoId = this.getAttribute('data-video-id');
            
            try {
                const response = await fetch(`/api/watch-later/${videoId}`, {
                    method: 'POST',
                    headers: {
                        'Content-Type': 'application/json'
                    }
                });
                
                const data = await response.json();
                
                if (data.success) {
                    if (data.added) {
                        this.textContent = '⏱️ Сохранено';
                        this.classList.add('active');
                    } else {
                        this.textContent = '⏱️ Сохранить';
                        this.classList.remove('active');
                    }
                }
            } catch (error) {
                console.error('Watch later error:', error);
            }
        });
    }
    
    // Share functionality
    if (shareBtn) {
        shareBtn.addEventListener('click', function(e) {
            e.stopPropagation();
            const url = window.location.href;
            if (navigator.share) {
                navigator.share({
                    title: document.title,
                    url: url
                });
            } else {
                navigator.clipboard.writeText(url).then(() => {
                    alert('Ссылка скопирована в буфер обмена!');
                });
            }
        });
    }
    
    // Subscribe functionality
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
    
    // Load comments
    loadComments();
});

function loadComments() {
    // TODO: Implement comments loading via API
    const commentsContainer = document.getElementById('comments-container');
    if (commentsContainer) {
        commentsContainer.innerHTML = '<p>Комментарии пока недоступны</p>';
    }
}

