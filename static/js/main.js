// Search functionality
document.addEventListener('DOMContentLoaded', function() {
    const searchInput = document.getElementById('search-input');
    const searchBtn = document.getElementById('search-btn');
    
    if (searchInput && searchBtn) {
        function performSearch() {
            const query = searchInput.value.trim();
            if (query) {
                window.location.href = `/?q=${encodeURIComponent(query)}`;
            }
        }
        
        searchBtn.addEventListener('click', performSearch);
        searchInput.addEventListener('keypress', function(e) {
            if (e.key === 'Enter') {
                performSearch();
            }
        });
    }
    
    // Search is handled server-side, no need for client-side API call
    
    // Category buttons
    const categoryButtons = document.querySelectorAll('.category-btn');
    categoryButtons.forEach(btn => {
        btn.addEventListener('click', function() {
            categoryButtons.forEach(b => b.classList.remove('active'));
            this.classList.add('active');
            // TODO: Implement category filtering
        });
    });

    // === Profile menu popup (Ютуб стиль) ===
    const profileMenuTrigger = document.querySelector('.profile-menu-trigger');
    const profilePopupMenu = profileMenuTrigger ? profileMenuTrigger.querySelector('.profile-popup-menu') : null;
    if (profileMenuTrigger && profilePopupMenu) {
        function openProfileMenu(e) {
            e.stopPropagation();
            profileMenuTrigger.classList.toggle('active');
        }
        profileMenuTrigger.addEventListener('click', openProfileMenu);
        // Клик вне меню — закрыть
        document.addEventListener('click', function(e) {
            if (!profileMenuTrigger.contains(e.target)) {
                profileMenuTrigger.classList.remove('active');
            }
        });
    }
});

function displaySearchResults(videos) {
    const videosGrid = document.getElementById('videos-grid');
    if (!videosGrid) return;
    
    if (videos.length === 0) {
        videosGrid.innerHTML = '<p>Видео не найдены</p>';
        return;
    }
    
    videosGrid.innerHTML = videos.map(video => `
        <div class="video-card" onclick="window.location.href='/watch/${video.id}'">
            <div class="video-thumbnail">
                ${video.thumbnail ? 
                    `<img src="${video.thumbnail}" alt="${video.title}">` : 
                    '<div class="default-thumbnail">🎬</div>'
                }
                <div class="video-duration">0:00</div>
            </div>
            <div class="video-info">
                <div class="video-author-avatar">
                    <div class="author-avatar-small">${video.author ? video.author[0].toUpperCase() : 'U'}</div>
                </div>
                <div class="video-details">
                    <h3 class="video-title" title="${escapeHtml(video.title)}">${escapeHtml(video.title)}</h3>
                    <p class="video-author">${escapeHtml(video.author || 'Неизвестный автор')}</p>
                    <p class="video-stats">${video.views || 0} просмотров</p>
                </div>
            </div>
        </div>
    `).join('');
}

function escapeHtml(text) {
    const div = document.createElement('div');
    div.textContent = text;
    return div.innerHTML;
}

