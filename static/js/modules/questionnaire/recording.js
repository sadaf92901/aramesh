// ============================================================
// ضبط صدا
// ============================================================

// ===== متغیرها =====
const mediaRecorders = {};
const audioChunks = {};
const audioBlobs = {};
const streams = {};
const recordingTimers = {};

// ============================================================
// توابع صادر شده
// ============================================================

export function startRecording(index) {
    const status = document.getElementById(`recordingStatus${index}`);
    const stopBtn = document.getElementById(`stopBtn${index}`);
    const recordBtn = document.getElementById(`recordBtn${index}`);

    if (!status) return;

    navigator.mediaDevices.getUserMedia({ audio: true })
        .then(stream => {
            streams[index] = stream;
            const mediaRecorder = new MediaRecorder(stream);
            mediaRecorders[index] = mediaRecorder;
            audioChunks[index] = [];

            mediaRecorder.ondataavailable = event => {
                audioChunks[index].push(event.data);
            };

            mediaRecorder.onstop = () => {
                const blob = new Blob(audioChunks[index], { type: 'audio/wav' });

                if (blob.size > 3 * 1024 * 1024) {
                    window.showToast('⚠️ حجم فایل صوتی بیشتر از ۵ مگابایت است', '⚠️', 'warning');
                    return;
                }

                audioBlobs[index] = blob;
                if (typeof window.saveAudioFile === 'function') {
                    window.saveAudioFile(index, blob);
                }

                const audioUrl = URL.createObjectURL(blob);
                const player = document.getElementById(`audioPlayback${index}`);
                if (player) {
                    player.src = audioUrl;
                    player.style.display = 'block';
                }

                status.textContent = '✅ ضبط شد!';
                status.className = 'recording-status success';
                stopBtn.disabled = true;
                recordBtn.classList.remove('btn-recording');
                if (recordingTimers[index]) clearInterval(recordingTimers[index]);
            };

            mediaRecorder.start();
            stopBtn.disabled = false;
            recordBtn.classList.add('btn-recording');
            status.textContent = '🔴 در حال ضبط...';
            status.className = 'recording-status recording';

            let seconds = 0;
            recordingTimers[index] = setInterval(() => {
                seconds++;
                const mins = Math.floor(seconds / 60);
                const secs = seconds % 60;
                status.textContent = `🔴 در حال ضبط... ${mins}:${secs < 10 ? '0' : ''}${secs}`;
            }, 1000);

            window.showToast('🎤 ضبط صدا شروع شد', '🎙️', 'info');
        })
        .catch(error => {
            window.showToast('❌ خطا: ' + error.message, '❌', 'error');
            status.textContent = '❌ خطا: ' + error.message;
            status.className = 'recording-status';
        });
}

export function stopRecording(index) {
    const status = document.getElementById(`recordingStatus${index}`);
    const recordBtn = document.getElementById(`recordBtn${index}`);

    if (mediaRecorders[index] && mediaRecorders[index].state !== 'inactive') {
        mediaRecorders[index].stop();
        if (streams[index]) {
            streams[index].getTracks().forEach(track => { track.stop(); });
            streams[index] = null;
        }
        if (status) {
            status.textContent = '⏹️ متوقف شد';
            status.className = 'recording-status';
        }
        if (recordBtn) recordBtn.classList.remove('btn-recording');
        if (recordingTimers[index]) {
            clearInterval(recordingTimers[index]);
            recordingTimers[index] = null;
        }
        window.showToast('⏹️ ضبط متوقف شد', '⏹️', 'info');
    }
}

export function getAudioBlob(index) {
    return audioBlobs[index] || null;
}

export function loadAllAudioFiles() {
    for (let i = 0; i < 3; i++) {
        if (typeof window.loadAudioFile === 'function') {
            window.loadAudioFile(i).then(blob => {
                if (blob) {
                    audioBlobs[i] = blob;
                    const audioUrl = URL.createObjectURL(blob);
                    const player = document.getElementById(`audioPlayback${i}`);
                    if (player) {
                        player.src = audioUrl;
                        player.style.display = 'block';
                        const status = document.getElementById(`recordingStatus${i}`);
                        if (status) {
                            status.textContent = '✅ ضبط شده (آفلاین)';
                            status.className = 'recording-status success';
                        }
                    }
                }
            }).catch(err => {
                console.log('No audio file for index', i);
            });
        }
    }
}

// ===== صادر کردن متغیرها برای دسترسی سایر ماژول‌ها =====
export { audioBlobs, recordingTimers };
