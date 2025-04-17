function getIcon(type) {
    switch (type) {
        case 'success':
            return '<svg xmlns="http://www.w3.org/2000/svg" class="h-6 w-6 text-green-500" fill="none" viewBox="0 0 24 24" stroke="currentColor"><path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M5 13l4 4L19 7" /></svg>';
        case 'error':
            return '<svg xmlns="http://www.w3.org/2000/svg" class="h-6 w-6 text-red-500" fill="none" viewBox="0 0 24 24" stroke="currentColor"><path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M6 18L18 6M6 6l12 12" /></svg>';
        default:
            return '<svg xmlns="http://www.w3.org/2000/svg" class="h-6 w-6 text-blue-500" fill="none" viewBox="0 0 24 24" stroke="currentColor"><path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M13 16h-1v-4h-1m1-4h.01M21 12a9 9 0 11-18 0 9 9 0 0118 0z" /></svg>';
    }
}


document.addEventListener('DOMContentLoaded', function () {
    // 通知 Popup
    const customPopup = document.getElementById('customPopup');
    const popupMessage = document.getElementById('popupMessage');
    const popupIcon = document.getElementById('popupIcon');
    const closePopupButton = document.getElementById('closePopup');

    // 確認 Popup
    const confirmPopup = document.getElementById('confirmPopup');
    const confirmMessage = document.getElementById('confirmMessage');
    const confirmButton = document.getElementById('confirmYes');
    const cancelButton = document.getElementById('confirmNo');

    let _confirmResolve = null;

    function showPopup(message, type = 'info') {
        if (!customPopup || !popupMessage || !popupIcon) {
            console.error("Popup elements not found!");
            return;
        }

        popupMessage.textContent = message;
        popupIcon.innerHTML = getIcon(type);

        customPopup.style.display = 'flex';

        // 3秒後自動關閉
        const timer = setTimeout(() => {
            hidePopup();
        }, 3000);

        // 如果用戶點擊關閉，也要清除計時器
        // 使用 ._timer 儲存計時器ID，以便稍後清除
        customPopup._timer = timer;
    }

    function hidePopup() {
        if (customPopup) {
            if (customPopup._timer) {
                clearTimeout(customPopup._timer);
                customPopup._timer = null;
            }
            customPopup.style.display = 'none';
        }
    }

    // --- 確認 Popup 功能 ---
    function showConfirm(message) {
        // 返回一個 Promise，當用戶點擊確認或取消時解析
        return new Promise((resolve) => {
            if (!confirmPopup || !confirmMessage) {
                console.error("Confirm Popup elements not found!");
                resolve(false);
                return;
            }

            confirmMessage.textContent = message;
            _confirmResolve = resolve;
            confirmPopup.style.display = 'flex';
        });
    }

    function hideConfirm() {
        if (confirmPopup) {
            confirmPopup.style.display = 'none';
        }
        // 重置 resolve 函數，避免重複觸發
        _confirmResolve = null;
    }

    // --- 事件監聽器 ---
    // 關閉通知 Popup
    if (closePopupButton) {
        closePopupButton.addEventListener('click', hidePopup);
    } else {
        console.warn("Close popup button ('closePopup') not found.");
    }

    // 確認按鈕 (確認 Popup)
    if (confirmButton) {
        confirmButton.addEventListener('click', () => {
            if (_confirmResolve) {
                _confirmResolve(true);
            }
            hideConfirm();
        });
    } else {
        console.warn("Confirm button ('confirmYes') not found.");
    }

    // 取消按鈕 (確認 Popup)
    if (cancelButton) {
        cancelButton.addEventListener('click', () => {
            if (_confirmResolve) {
                _confirmResolve(false);
            }
            hideConfirm();
        });
    } else {
        console.warn("Cancel button ('confirmNo') not found.");
    }

    window.showPopup = showPopup;
    window.showConfirm = showConfirm;
});