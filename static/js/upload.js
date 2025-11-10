// Upload functionality
document.addEventListener('DOMContentLoaded', function() {
    const uploadForm = document.getElementById('upload-form');
    const videoFileInput = document.getElementById('video-file');
    const fileInfo = document.getElementById('file-info');
    const submitBtn = document.getElementById('submit-btn');
    const uploadProgress = document.getElementById('upload-progress');
    
    // Handle file selection
    if (videoFileInput) {
        videoFileInput.addEventListener('change', function(e) {
            const file = e.target.files[0];
            const videoPreview = document.getElementById('video-preview');
            const videoPreviewContainer = document.getElementById('video-preview-container');
            const videoDuration = document.getElementById('video-duration');
            
            if (file && videoPreview && videoPreviewContainer && videoDuration) {
                // Проверяем, что это видео файл
                if (!file.type.startsWith('video/')) {
                    alert('Пожалуйста, выберите видео файл');
                    return;
                }
                
                // Показываем информацию о файле
                fileInfo.style.display = 'block';
                fileInfo.innerHTML = `
                    <p><strong>Выбранный файл:</strong> ${file.name}</p>
                    <p><strong>Размер:</strong> ${(file.size / 1024 / 1024).toFixed(2)} MB</p>
                    <p><strong>Тип:</strong> ${file.type}</p>
                `;
                
                // Очищаем старый URL, если он был (ПЕРЕД созданием нового)
                const oldSrc = videoPreview.src;
                if (oldSrc && oldSrc.startsWith('blob:')) {
                    URL.revokeObjectURL(oldSrc);
                }
                
                // Создаем новый URL для предпросмотра
                const videoURL = URL.createObjectURL(file);
                console.log('Created video URL:', videoURL);
                
                // Показываем контейнер предпросмотра
                videoPreviewContainer.style.display = 'block';
                videoDuration.textContent = 'Загрузка...';
                
                // Сбрасываем и устанавливаем новый источник
                videoPreview.pause();
                videoPreview.src = '';
                
                // Устанавливаем новый источник
                videoPreview.src = videoURL;
                
                // Загружаем видео
                videoPreview.load();
                
                // Получаем длительность видео
                const handleLoadedMetadata = function() {
                    console.log('Video metadata loaded');
                    const duration = videoPreview.duration;
                    if (duration && !isNaN(duration) && isFinite(duration)) {
                        const minutes = Math.floor(duration / 60);
                        const seconds = Math.floor(duration % 60);
                        const durationText = `${minutes}:${seconds.toString().padStart(2, '0')}`;
                        videoDuration.textContent = `Длительность: ${durationText}`;
                    } else {
                        videoDuration.textContent = 'Длительность: неизвестна';
                    }
                    videoPreview.removeEventListener('loadedmetadata', handleLoadedMetadata);
                };
                
                // Обработка ошибок
                const handleError = function(e) {
                    console.error('Video load error:', e, videoPreview.error);
                    let errorMsg = 'Ошибка загрузки видео';
                    if (videoPreview.error) {
                        switch(videoPreview.error.code) {
                            case 1:
                                errorMsg = 'Видео прервано';
                                break;
                            case 2:
                                errorMsg = 'Ошибка сети';
                                break;
                            case 3:
                                errorMsg = 'Ошибка декодирования';
                                break;
                            case 4:
                                errorMsg = 'Формат не поддерживается';
                                break;
                        }
                    }
                    videoDuration.textContent = errorMsg;
                    videoPreview.removeEventListener('error', handleError);
                };
                
                videoPreview.addEventListener('loadedmetadata', handleLoadedMetadata, { once: true });
                videoPreview.addEventListener('error', handleError, { once: true });
                
                // Также слушаем canplay для подтверждения, что видео готово
                videoPreview.addEventListener('canplay', function() {
                    console.log('Video can play');
                }, { once: true });
            } else {
                // Скрываем предпросмотр, если файл не выбран
                const oldSrc = videoPreview.src;
                videoPreviewContainer.style.display = 'none';
                videoPreview.src = '';
                if (oldSrc && oldSrc.startsWith('blob:')) {
                    URL.revokeObjectURL(oldSrc);
                }
            }
        });
    }
    
    // Обработка выбора превью (миниатюры)
    const thumbnailFileInput = document.getElementById('thumbnail-file');
    const thumbnailPreview = document.getElementById('thumbnail-preview');
    const thumbnailPreviewContainer = document.getElementById('thumbnail-preview-container');
    const removeThumbnailBtn = document.getElementById('remove-thumbnail');
    
    if (thumbnailFileInput && thumbnailPreview && thumbnailPreviewContainer) {
        thumbnailFileInput.addEventListener('change', function(e) {
            const file = e.target.files[0];
            
            if (file) {
                // Проверяем, что это изображение
                if (!file.type.startsWith('image/')) {
                    alert('Пожалуйста, выберите файл изображения');
                    thumbnailFileInput.value = '';
                    return;
                }
                
                // Проверяем размер (макс. 10MB)
                if (file.size > 10 * 1024 * 1024) {
                    alert('Размер изображения не должен превышать 10MB');
                    thumbnailFileInput.value = '';
                    return;
                }
                
                // Создаем URL для предпросмотра
                const imageURL = URL.createObjectURL(file);
                thumbnailPreview.src = imageURL;
                thumbnailPreviewContainer.style.display = 'block';
            }
        });
        
        // Удаление превью
        if (removeThumbnailBtn) {
            removeThumbnailBtn.addEventListener('click', function() {
                if (thumbnailPreview.src && thumbnailPreview.src.startsWith('blob:')) {
                    URL.revokeObjectURL(thumbnailPreview.src);
                }
                thumbnailPreview.src = '';
                thumbnailPreviewContainer.style.display = 'none';
                thumbnailFileInput.value = '';
            });
        }
    }
    
    // Очистка URL при закрытии страницы
    window.addEventListener('beforeunload', function() {
        const videoPreview = document.getElementById('video-preview');
        if (videoPreview && videoPreview.src && videoPreview.src.startsWith('blob:')) {
            URL.revokeObjectURL(videoPreview.src);
        }
        
        const thumbnailPreview = document.getElementById('thumbnail-preview');
        if (thumbnailPreview && thumbnailPreview.src && thumbnailPreview.src.startsWith('blob:')) {
            URL.revokeObjectURL(thumbnailPreview.src);
        }
    });
    
    // Handle form submission
    if (uploadForm) {
        uploadForm.addEventListener('submit', async function(e) {
            e.preventDefault();
            
            const formData = new FormData(uploadForm);
            const videoFile = videoFileInput.files[0];
            
            if (!videoFile) {
                alert('Пожалуйста, выберите видео файл');
                return;
            }
            
            submitBtn.disabled = true;
            submitBtn.textContent = 'Загрузка...';
            uploadProgress.style.display = 'block';
            uploadProgress.innerHTML = '<p>Загрузка видео, пожалуйста подождите...</p>';
            
            try {
                const response = await fetch('/upload', {
                    method: 'POST',
                    body: formData
                });
                
                const data = await response.json();
                
                if (data.success) {
                    // Очищаем предпросмотр перед переходом
                    const videoPreview = document.getElementById('video-preview');
                    if (videoPreview && videoPreview.src && videoPreview.src.startsWith('blob:')) {
                        URL.revokeObjectURL(videoPreview.src);
                    }
                    
                    uploadProgress.innerHTML = '<p style="color: green;">Видео успешно загружено!</p>';
                    setTimeout(() => {
                        window.location.href = `/watch/${data.video_id}`;
                    }, 2000);
                } else {
                    uploadProgress.innerHTML = `<p style="color: red;">Ошибка: ${data.error || 'Неизвестная ошибка'}</p>`;
                    submitBtn.disabled = false;
                    submitBtn.textContent = 'Загрузить видео';
                }
            } catch (error) {
                console.error('Upload error:', error);
                uploadProgress.innerHTML = `<p style="color: red;">Ошибка загрузки: ${error.message}</p>`;
                submitBtn.disabled = false;
                submitBtn.textContent = 'Загрузить видео';
            }
        });
    }
});

