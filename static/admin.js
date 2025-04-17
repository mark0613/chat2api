document.addEventListener('DOMContentLoaded', function () {
    const userId = window.currentUserId;
    const apiPrefix = window.apiPrefix;
    const activeTab = window.activeTab;

    // 用戶管理相關函數
    window.executeToggleUserActive = async function (userId) {
        try {
            console.log('Toggling user active status for:', userId);
            const formData = new FormData();
            formData.append('active', 'toggle');

            const response = await fetch(`${apiBaseUrl}/api/admin/users/${userId}/update`, {
                method: 'POST',
                body: formData
            });

            if (!response.ok) {
                const errorData = await response.json();
                throw new Error(errorData.detail || '操作失敗');
            }

            const result = await response.json();
            if (result.status === 'success') {
                showPopup('用戶狀態已更新', 'success');
                if (window.loadUsers) window.loadUsers();
            } else {
                throw new Error('操作未成功完成');
            }
        } catch (error) {
            console.error('Error toggling user active status:', error);
            showPopup(`更新用戶狀態失敗: ${error.message}`, 'error');
        }
    };

    window.executeToggleUserRole = async function (userId) {
        try {
            console.log('Toggling user role for:', userId);
            const formData = new FormData();
            formData.append('role', 'toggle');

            const response = await fetch(`${apiBaseUrl}/api/admin/users/${userId}/update`, {
                method: 'POST',
                body: formData
            });

            if (!response.ok) {
                const errorData = await response.json();
                throw new Error(errorData.detail || '操作失敗');
            }

            const result = await response.json();
            if (result.status === 'success') {
                showPopup('用戶角色已更新', 'success');
                if (window.loadUsers) window.loadUsers();
            } else {
                throw new Error('操作未成功完成');
            }
        } catch (error) {
            console.error('Error toggling user role:', error);
            showPopup(`更新用戶角色失敗: ${error.message}`, 'error');
        }
    };

    // Token 相關函數
    window.executeMarkAsError = async function (tokenId) {
        try {
            console.log('Marking token as error:', tokenId);
            const url = `${apiBaseUrl}/api/token/mark-error/${tokenId}`;
            console.log('URL:', url);

            const response = await fetch(url, {
                method: 'POST'
            });

            if (response.ok) {
                if (window.loadTokens) window.loadTokens();
                showPopup('Token 已標記為錯誤', 'success');
            } else {
                const errorData = await response.json();
                showPopup(`錯誤: ${errorData.detail}`, 'error');
            }
        } catch (error) {
            console.error('Error marking token as error:', error);
            showPopup('標記 token 為錯誤時發生錯誤', 'error');
        }
    };

    window.executeDeleteToken = async function (tokenId) {
        try {
            console.log('Deleting token:', tokenId);
            const url = `${apiBaseUrl}/api/token/delete/${tokenId}`;
            console.log('URL:', url);

            const response = await fetch(url, {
                method: 'POST'
            });

            if (response.ok) {
                if (window.loadTokens) window.loadTokens();
                showPopup('Token 已刪除', 'success');
            } else {
                const errorData = await response.json();
                showPopup(`錯誤: ${errorData.detail}`, 'error');
            }
        } catch (error) {
            console.error('Error deleting token:', error);
            showPopup('刪除 token 時發生錯誤', 'error');
        }
    };

    window.executeClearTokens = async function () {
        try {
            console.log('Clearing all tokens');
            const response = await fetch(`${apiBaseUrl}/api/token/clear`, {
                method: 'POST'
            });

            if (response.ok) {
                if (window.loadTokens) window.loadTokens();
                showPopup('所有 Tokens 已清空', 'success');
            } else {
                const errorData = await response.json();
                showPopup(`錯誤: ${errorData.detail}`, 'error');
            }
        } catch (error) {
            console.error('Error clearing tokens:', error);
            showPopup('清空 tokens 時發生錯誤', 'error');
        }
    };

    // 側邊欄切換功能
    const toggleSidebar = document.getElementById('toggleSidebar');
    const closeSidebar = document.getElementById('closeSidebar');
    const sidebar = document.querySelector('.sidebar');

    if (toggleSidebar) {
        toggleSidebar.addEventListener('click', function () {
            sidebar.classList.toggle('show');
            sidebar.classList.toggle('hidden');
            sidebar.classList.toggle('md:block');
        });
    }

    if (closeSidebar) {
        closeSidebar.addEventListener('click', function () {
            sidebar.classList.remove('show');
            sidebar.classList.add('hidden');
            sidebar.classList.add('md:block');
        });
    }

    // 初始化變數
    let apiBaseUrl = "";
    if (apiPrefix && apiPrefix !== "None") {
        apiBaseUrl = `/${apiPrefix}`;
    }

    // 確認彈窗相關變數
    const confirmPopup = document.getElementById('confirmPopup');
    const confirmMessage = document.getElementById('confirmMessage');
    const confirmButton = document.getElementById('confirmYes');
    const cancelButton = document.getElementById('confirmNo');
    let currentAction = null;
    let currentUserId = userId;
    let currentTokenId = null;

    console.log('Current user ID:', currentUserId);

    // 自定義顯示彈窗的函數
    window.showPopup = function (message, type = 'info') {
        const popup = document.getElementById('customPopup');
        const popupMessage = document.getElementById('popupMessage');
        const popupIcon = document.getElementById('popupIcon');

        popupMessage.textContent = message;

        // 根據類型設置圖標
        if (type === 'success') {
            popupIcon.innerHTML = '<svg xmlns="http://www.w3.org/2000/svg" class="h-6 w-6 text-green-500" fill="none" viewBox="0 0 24 24" stroke="currentColor"><path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M5 13l4 4L19 7" /></svg>';
        } else if (type === 'error') {
            popupIcon.innerHTML = '<svg xmlns="http://www.w3.org/2000/svg" class="h-6 w-6 text-red-500" fill="none" viewBox="0 0 24 24" stroke="currentColor"><path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M6 18L18 6M6 6l12 12" /></svg>';
        } else {
            popupIcon.innerHTML = '<svg xmlns="http://www.w3.org/2000/svg" class="h-6 w-6 text-blue-500" fill="none" viewBox="0 0 24 24" stroke="currentColor"><path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M13 16h-1v-4h-1m1-4h.01M21 12a9 9 0 11-18 0 9 9 0 0118 0z" /></svg>';
        }

        popup.style.display = 'flex';

        // 3秒後自動關閉
        setTimeout(() => {
            popup.style.display = 'none';
        }, 3000);
    }

    // 顯示確認彈窗的函數
    window.showConfirm = function (message, action, userId = null, tokenId = null) {
        confirmMessage.textContent = message;
        currentAction = action;
        currentUserId = userId;
        currentTokenId = tokenId;
        confirmPopup.style.display = 'flex';
    }

    // 關閉彈窗的點擊事件
    document.getElementById('closePopup').addEventListener('click', () => {
        document.getElementById('customPopup').style.display = 'none';
    });

    // 確認按鈕事件
    confirmButton.addEventListener('click', async () => {
        console.log('Confirm action:', currentAction, 'User ID:', currentUserId, 'Token ID:', currentTokenId);
        confirmPopup.style.display = 'none';

        try {
            if (currentAction === 'mark-error' && currentTokenId) {
                await window.executeMarkAsError(currentTokenId);
            } else if (currentAction === 'delete-token' && currentTokenId) {
                await window.executeDeleteToken(currentTokenId);
            } else if (currentAction === 'clear-tokens') {
                await window.executeClearTokens();
            } else if (currentAction === 'toggle-user-active' && currentUserId) {
                await window.executeToggleUserActive(currentUserId);
            } else if (currentAction === 'toggle-user-role' && currentUserId) {
                await window.executeToggleUserRole(currentUserId);
            }
        } catch (error) {
            console.error('Error in confirm action:', error);
            showPopup(`操作失敗: ${error.message}`, 'error');
        }

        // 重置當前操作
        currentAction = null;
        currentUserId = null;
        currentTokenId = null;
    });

    // 取消按鈕事件
    cancelButton.addEventListener('click', () => {
        confirmPopup.style.display = 'none';
        currentAction = null;
        currentUserId = null;
        currentTokenId = null;
    });

    // ============= 使用者管理功能 =============
    if (activeTab === 'users') {
        // 載入使用者列表
        window.loadUsers = async function () {
            try {
                const response = await fetch(`${apiBaseUrl}/api/admin/users`);
                if (!response.ok) {
                    throw new Error('獲取使用者列表失敗');
                }

                const data = await response.json();
                const usersTableBody = document.getElementById('usersTableBody');

                if (data.status === 'success' && data.users && data.users.length > 0) {
                    usersTableBody.innerHTML = '';

                    data.users.forEach(user => {
                        const lastActive = user.last_active ? new Date(user.last_active).toLocaleString() : '未知';

                        const tr = document.createElement('tr');
                        tr.innerHTML = `
                            <td class="px-6 py-4 whitespace-nowrap">${user.id}</td>
                            <td class="px-6 py-4 whitespace-nowrap">${user.name}</td>
                            <td class="px-6 py-4 whitespace-nowrap">${user.email}</td>
                            <td class="px-6 py-4 whitespace-nowrap text-center">
                                ${user.active ?
                                '<svg xmlns="http://www.w3.org/2000/svg" class="h-6 w-6 text-green-500 mx-auto" fill="none" viewBox="0 0 24 24" stroke="currentColor"><path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M5 13l4 4L19 7" /></svg>' :
                                '<svg xmlns="http://www.w3.org/2000/svg" class="h-6 w-6 text-red-500 mx-auto" fill="none" viewBox="0 0 24 24" stroke="currentColor"><path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M6 18L18 6M6 6l12 12" /></svg>'}
                            </td>
                            <td class="px-6 py-4 whitespace-nowrap">
                                <span class="${user.role === 'admin' ? 'bg-purple-100 text-purple-800' : 'bg-blue-100 text-blue-800'} px-2 py-1 inline-flex text-xs leading-5 font-semibold rounded-full">
                                    ${user.role}
                                </span>
                            </td>
                            <td class="px-6 py-4 whitespace-nowrap">${lastActive}</td>
                            <td class="px-6 py-4 whitespace-nowrap text-sm font-medium">
                                ${user.id !== currentUserId ? `
                                    <button onclick="executeToggleUserActive(${user.id})" class="${user.active ? 'bg-yellow-500 hover:bg-yellow-600' : 'bg-green-500 hover:bg-green-600'} text-white py-1 px-2 rounded mr-2">
                                        ${user.active ? 'Disable' : 'Enable'}
                                    </button>
                                    <button onclick="executeToggleUserRole(${user.id})" class="bg-blue-500 hover:bg-blue-600 text-white py-1 px-2 rounded">
                                        ${user.role === 'admin' ? '設為 User' : '設為 Admin'}
                                    </button>
                                ` : '<span class="text-gray-500">（當前用戶）</span>'}
                            </td>
                        `;
                        usersTableBody.appendChild(tr);
                    });
                } else {
                    usersTableBody.innerHTML = `
                        <tr>
                            <td colspan="7" class="px-6 py-4 text-center text-gray-500">沒有找到使用者數據</td>
                        </tr>
                    `;
                }
            } catch (error) {
                console.error('Error loading users:', error);
                document.getElementById('usersTableBody').innerHTML = `
                    <tr>
                        <td colspan="7" class="px-6 py-4 text-center text-red-500">載入使用者失敗: ${error.message}</td>
                    </tr>
                `;
            }
        };

        window.loadUsers();
    }

    // ============= Token 管理功能 =============
    if (activeTab === 'tokens') {
        const uploadForm = document.getElementById('uploadForm');
        const clearForm = document.getElementById('clearForm');
        const tokensList = document.getElementById('tokensList');
        const errorTokensList = document.getElementById('errorTokensList');

        // 設置表單動作 URL
        const tokenAddUrl = `${apiBaseUrl}/api/token/add`;
        const tokenClearUrl = `${apiBaseUrl}/api/token/clear`;
        const tokenListUrl = `${apiBaseUrl}/api/token/list`;

        // 載入 tokens 和 error tokens
        window.loadTokens = async function () {
            try {
                const response = await fetch(tokenListUrl);
                const data = await response.json();

                // 更新正常 tokens 列表
                tokensList.innerHTML = '';
                data.tokens.forEach(token => {
                    const tr = document.createElement('tr');
                    tr.innerHTML = `
                        <td class="border p-2 truncate max-w-[200px]">${token.token}</td>
                        <td class="border p-2">${token.description || '無描述'}</td>
                        <td class="border p-2">
                            <button onclick="showConfirm('確定要將此 Token 標記為錯誤嗎？', 'mark-error', null, ${token.id})" class="bg-yellow-500 text-white py-1 px-2 rounded hover:bg-yellow-600 mr-2">標記為錯誤</button>
                            <button onclick="showConfirm('確定要刪除此 Token 嗎？這個操作不可撤銷！', 'delete-token', null, ${token.id})" class="bg-red-500 text-white py-1 px-2 rounded hover:bg-red-600">刪除</button>
                        </td>
                    `;
                    tokensList.appendChild(tr);
                });

                if (data.tokens.length === 0) {
                    tokensList.innerHTML = `
                        <tr>
                            <td colspan="3" class="border p-4 text-center text-gray-500">暫無可用 Token</td>
                        </tr>
                    `;
                }

                // 更新錯誤 tokens 列表
                errorTokensList.innerHTML = '';
                data.error_tokens.forEach(token => {
                    const tr = document.createElement('tr');
                    tr.innerHTML = `
                        <td class="border p-2 truncate max-w-[200px]">${token.token}</td>
                        <td class="border p-2">${token.description || '無描述'}</td>
                        <td class="border p-2">
                            <button onclick="showConfirm('確定要刪除此 Token 嗎？這個操作不可撤銷！', 'delete-token', null, ${token.id})" class="bg-red-500 text-white py-1 px-2 rounded hover:bg-red-600">刪除</button>
                        </td>
                    `;
                    errorTokensList.appendChild(tr);
                });

                if (data.error_tokens.length === 0) {
                    errorTokensList.innerHTML = `
                        <tr>
                            <td colspan="3" class="border p-4 text-center text-gray-500">暫無錯誤 Token</td>
                        </tr>
                    `;
                }

                // 更新計數
                document.getElementById('tokensCount').textContent = data.tokens.length;
                document.getElementById('errorTokensCount').textContent = data.error_tokens.length;
            } catch (error) {
                console.error('Error loading tokens:', error);
                showPopup(`載入 tokens 失敗: ${error.message}`, 'error');
                errorTokensList.innerHTML = `
                    <tr>
                        <td colspan="3" class="border p-4 text-center text-red-500">載入失敗: ${error.message}</td>
                    </tr>
                `;
                tokensList.innerHTML = `
                    <tr>
                        <td colspan="3" class="border p-4 text-center text-red-500">載入失敗: ${error.message}</td>
                    </tr>
                `;
            }
        };

        // 初始載入
        window.loadTokens();

        // 添加 Token
        if (uploadForm) {
            uploadForm.addEventListener('submit', async (e) => {
                e.preventDefault();
                const tokenInput = document.getElementById('tokenInput');
                const descriptionInput = document.getElementById('descriptionInput');

                if (!tokenInput.value) {
                    showPopup('Token 不能為空', 'error');
                    return;
                }

                const formData = new FormData();
                formData.append('token', tokenInput.value);
                formData.append('description', descriptionInput.value || '手動添加');

                try {
                    const response = await fetch(tokenAddUrl, {
                        method: 'POST',
                        body: formData
                    });

                    if (response.ok) {
                        tokenInput.value = '';
                        descriptionInput.value = '';
                        loadTokens();
                        showPopup('Token 添加成功', 'success');
                    } else {
                        const errorData = await response.json();
                        showPopup(`錯誤: ${errorData.detail}`, 'error');
                    }
                } catch (error) {
                    console.error('Error adding token:', error);
                    showPopup('添加 token 時發生錯誤', 'error');
                }
            });
        }

        // 清空所有 Tokens
        if (clearForm) {
            clearForm.addEventListener('submit', async (e) => {
                e.preventDefault();
                showConfirm('確定要清空所有 Tokens 嗎？這個操作不可撤銷！', 'clear-tokens');
            });
        }

        // 為全局作用域定義函數，以便從HTML中調用
        window.executeMarkAsError = executeMarkAsError;
        window.executeDeleteToken = executeDeleteToken;
        window.executeClearTokens = executeClearTokens;
    }
});