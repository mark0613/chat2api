document.addEventListener('DOMContentLoaded', async function () {
    // 側邊欄切換功能
    const toggleSidebar = document.getElementById('toggleSidebar');
    const closeSidebar = document.getElementById('closeSidebar');
    const sidebar = document.querySelector('.sidebar');

    if (toggleSidebar && sidebar) {
        toggleSidebar.addEventListener('click', function () {
            sidebar.classList.toggle('show');
            sidebar.classList.toggle('hidden');
            sidebar.classList.toggle('md:block');
        });
    }

    if (closeSidebar && sidebar) {
        closeSidebar.addEventListener('click', function () {
            sidebar.classList.remove('show');
            sidebar.classList.add('hidden');
            sidebar.classList.add('md:block');
        });
    }

    // 使用者管理功能
    if (activeTab === 'users') {
        const usersTableBody = document.getElementById('usersTableBody');

        if (!usersTableBody) {
            console.error("Element with ID 'usersTableBody' not found.");
        } else {
            await loadUsers();
        }
    }

    // Token 管理功能
    if (activeTab === 'tokens') {
        const uploadForm = document.getElementById('uploadForm');
        const clearForm = document.getElementById('clearForm');
        const tokensList = document.getElementById('tokensList');
        const errorTokensList = document.getElementById('errorTokensList');
        const tokensCountEl = document.getElementById('tokensCount');
        const errorTokensCountEl = document.getElementById('errorTokensCount');

        if (!tokensList || !errorTokensList || !tokensCountEl || !errorTokensCountEl) {
            console.error("One or more Token list/count elements not found.");
        } else {
            await loadTokens();

            // 添加 Token 表單提交
            if (uploadForm) {
                const tokenInput = document.getElementById('tokenInput');
                const descriptionInput = document.getElementById('descriptionInput');

                if (!tokenInput) console.error("Element 'tokenInput' not found");
                if (!descriptionInput) console.warn("Element 'descriptionInput' not found");

                uploadForm.addEventListener('submit', async (e) => {
                    e.preventDefault();
                    if (!tokenInput || !tokenInput.value) {
                        showPopup('Token 不能為空', 'error');
                        return;
                    }

                    const formData = new FormData();
                    formData.append('token', tokenInput.value);
                    if (descriptionInput) {
                        formData.append('description', descriptionInput.value || '手動添加');
                    } else {
                        formData.append('description', '手動添加');
                    }


                    try {
                        const response = await fetch(`${apiBaseUrl}/api/token/add`, {
                            method: 'POST',
                            body: formData
                        });

                        if (response.ok) {
                            tokenInput.value = '';
                            if (descriptionInput) descriptionInput.value = '';
                            loadTokens(); // 重新載入列表
                            showPopup('Token 添加成功', 'success');
                        } else {
                            const errorData = await response.json();
                            throw new Error(errorData.detail || `添加失敗 (HTTP ${response.status})`);
                        }
                    } catch (error) {
                        console.error('Error adding token:', error);
                        showPopup(`添加 token 失敗: ${error.message}`, 'error');
                    }
                });
            } else {
                console.warn("Element with ID 'uploadForm' not found.");
            }

            // 清空所有 Tokens 表單提交 (使用 addEventListener)
            if (clearForm) {
                clearForm.addEventListener('submit', async (e) => {
                    e.preventDefault();
                    const confirmed = await showConfirm('確定要清空所有 Tokens 嗎？這個操作不可撤銷！');
                    if (confirmed) {
                        try {
                            await executeClearTokens();
                            // 成功消息由 executeClearTokens 處理
                        } catch (error) {
                            console.error('Error clearing tokens from form:', error);
                            showPopup(`清空失敗: ${error.message}`, 'error'); // 顯示執行錯誤
                        }
                    }
                });
            } else {
                console.warn("Element with ID 'clearForm' not found.");
            }
        }
    }
});