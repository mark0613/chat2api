const loggedInUserId = window.currentUserId;
const apiPrefix = window.apiPrefix;
const activeTab = window.activeTab;

let apiBaseUrl = "";
if (apiPrefix && apiPrefix !== "None") {
    apiBaseUrl = `/${apiPrefix}`;
}

document.addEventListener('DOMContentLoaded', function () {
    // 用戶管理相關函數
    window.executeToggleUserActive = async function (userIdToToggle) {
        try {
            console.log('Toggling user active status for:', userIdToToggle);
            const formData = new FormData();
            formData.append('active', 'toggle');

            const response = await fetch(`${apiBaseUrl}/api/admin/users/${userIdToToggle}/update`, {
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
                throw new Error(result.detail || '操作未成功完成');
            }
        } catch (error) {
            console.error('Error toggling user active status:', error);
            showPopup(`更新用戶狀態失敗: ${error.message}`, 'error');
        }
    };

    window.executeToggleUserRole = async function (userIdToToggle) {
        try {
            console.log('Toggling user role for:', userIdToToggle);
            const formData = new FormData();
            formData.append('role', 'toggle');

            const response = await fetch(`${apiBaseUrl}/api/admin/users/${userIdToToggle}/update`, {
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
                throw new Error(result.detail || '操作未成功完成');
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
                throw new Error(errorData.detail || `標記錯誤失敗 (HTTP ${response.status})`);
            }
        } catch (error) {
            console.error('Error in executeMarkAsError:', error);
            throw error;
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
                throw new Error(errorData.detail || `刪除失敗 (HTTP ${response.status})`);
            }
        } catch (error) {
            console.error('Error in executeDeleteToken:', error);
            throw error;
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
                throw new Error(errorData.detail || `清空失敗 (HTTP ${response.status})`);
            }
        } catch (error) {
            console.error('Error in executeClearTokens:', error);
            throw error;
        }
    };

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

    // ============= 使用者管理功能 =============
    if (activeTab === 'users') {
        const usersTableBody = document.getElementById('usersTableBody');

        if (!usersTableBody) {
            console.error("Element with ID 'usersTableBody' not found.");
        } else {
            window.loadUsers = async function () {
                try {
                    const response = await fetch(`${apiBaseUrl}/api/admin/users`);
                    if (!response.ok) {
                        throw new Error('獲取使用者列表失敗');
                    }

                    const data = await response.json();
                    usersTableBody.innerHTML = '';

                    if (data.status === 'success' && data.users && data.users.length > 0) {
                        data.users.forEach(user => {
                            const lastActive = user.last_active ? new Date(user.last_active).toLocaleString() : '未知';
                            const isCurrentUser = user.id === loggedInUserId;

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
                                    ${!isCurrentUser ? `
                                        <button onclick="window.executeToggleUserActive(${user.id})" class="${user.active ? 'bg-yellow-500 hover:bg-yellow-600' : 'bg-green-500 hover:bg-green-600'} text-white py-1 px-2 rounded mr-2">
                                            ${user.active ? 'Disable' : 'Enable'}
                                        </button>
                                        <button onclick="window.executeToggleUserRole(${user.id})" class="bg-blue-500 hover:bg-blue-600 text-white py-1 px-2 rounded">
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
                                <td colspan="7" class="px-6 py-4 text-center text-gray-500">${data.users && data.users.length === 0 ? '沒有找到使用者數據' : (data.message || '無法解析用戶數據')}</td>
                            </tr>
                        `;
                    }
                } catch (error) {
                    console.error('Error loading users:', error);
                    usersTableBody.innerHTML = `
                        <tr>
                            <td colspan="7" class="px-6 py-4 text-center text-red-500">載入使用者失敗: ${error.message}</td>
                        </tr>
                    `;
                    showPopup(`載入使用者失敗: ${error.message}`, 'error');
                }
            };

            window.loadUsers();
        }
    }

    // ============= Token 管理功能 =============
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
            // 設置 API URLs
            const tokenAddUrl = `${apiBaseUrl}/api/token/add`;
            const tokenListUrl = `${apiBaseUrl}/api/token/list`;

            // 載入 tokens 和 error tokens
            window.loadTokens = async function () {
                try {
                    const response = await fetch(tokenListUrl);
                    if (!response.ok) {
                        throw new Error(`獲取Token列表失敗 (HTTP ${response.status})`);
                    }
                    const data = await response.json();

                    // 更新正常 tokens 列表
                    tokensList.innerHTML = '';
                    if (data.tokens && data.tokens.length > 0) {
                        data.tokens.forEach(token => {
                            const tr = document.createElement('tr');
                            const tdToken = document.createElement('td');
                            tdToken.className = "border p-2 truncate max-w-[200px]";
                            tdToken.textContent = token.token;

                            const tdDesc = document.createElement('td');
                            tdDesc.className = "border p-2";
                            tdDesc.textContent = token.description || '無描述';

                            const tdActions = document.createElement('td');
                            tdActions.className = "border p-2";

                            // --- 標記為錯誤按鈕 (使用 addEventListener) ---
                            const markErrorButton = document.createElement('button');
                            markErrorButton.textContent = '標記為錯誤';
                            markErrorButton.className = 'bg-yellow-500 text-white py-1 px-2 rounded hover:bg-yellow-600 mr-2';
                            markErrorButton.addEventListener('click', async () => {
                                const confirmed = await showConfirm('確定要將此 Token 標記為錯誤嗎？');
                                if (confirmed) {
                                    try {
                                        await window.executeMarkAsError(token.id);
                                        // 成功消息由 executeMarkAsError 內部處理
                                    } catch (error) {
                                        console.error('Error marking token as error from button:', error);
                                        showPopup(`標記錯誤失敗: ${error.message}`, 'error'); // 顯示執行錯誤
                                    }
                                } else {
                                    console.log('Mark as error cancelled.');
                                }
                            });

                            // --- 刪除按鈕 (使用 addEventListener) ---
                            const deleteButton = document.createElement('button');
                            deleteButton.textContent = '刪除';
                            deleteButton.className = 'bg-red-500 text-white py-1 px-2 rounded hover:bg-red-600';
                            deleteButton.addEventListener('click', async () => {
                                const confirmed = await showConfirm('確定要刪除此 Token 嗎？這個操作不可撤銷！');
                                if (confirmed) {
                                    try {
                                        await window.executeDeleteToken(token.id);
                                        // 成功消息由 executeDeleteToken 內部處理
                                    } catch (error) {
                                        console.error('Error deleting token from button:', error);
                                        showPopup(`刪除失敗: ${error.message}`, 'error'); // 顯示執行錯誤
                                    }
                                } else {
                                    console.log('Delete token cancelled.');
                                }
                            });

                            tdActions.appendChild(markErrorButton);
                            tdActions.appendChild(deleteButton);
                            tr.appendChild(tdToken);
                            tr.appendChild(tdDesc);
                            tr.appendChild(tdActions);
                            tokensList.appendChild(tr);
                        });
                    } else {
                        tokensList.innerHTML = `
                            <tr>
                                <td colspan="3" class="border p-4 text-center text-gray-500">暫無可用 Token</td>
                            </tr>
                        `;
                    }

                    // --- 更新錯誤 tokens 列表 ---
                    errorTokensList.innerHTML = ''; // 清空
                    if (data.error_tokens && data.error_tokens.length > 0) {
                        data.error_tokens.forEach(token => {
                            const tr = document.createElement('tr');
                            const tdToken = document.createElement('td');
                            tdToken.className = "border p-2 truncate max-w-[200px]";
                            tdToken.textContent = token.token;

                            const tdDesc = document.createElement('td');
                            tdDesc.className = "border p-2";
                            tdDesc.textContent = token.description || '無描述';

                            const tdActions = document.createElement('td');
                            tdActions.className = "border p-2";

                            // --- 刪除按鈕 (錯誤 Token) ---
                            const deleteErrorButton = document.createElement('button');
                            deleteErrorButton.textContent = '刪除';
                            deleteErrorButton.className = 'bg-red-500 text-white py-1 px-2 rounded hover:bg-red-600';
                            deleteErrorButton.addEventListener('click', async () => {
                                const confirmed = await showConfirm('確定要刪除此 Token 嗎？這個操作不可撤銷！');
                                if (confirmed) {
                                    try {
                                        await window.executeDeleteToken(token.id);
                                    } catch (error) {
                                        console.error('Error deleting error token from button:', error);
                                        showPopup(`刪除失敗: ${error.message}`, 'error');
                                    }
                                } else {
                                    console.log('Delete error token cancelled.');
                                }
                            });

                            tdActions.appendChild(deleteErrorButton);
                            tr.appendChild(tdToken);
                            tr.appendChild(tdDesc);
                            tr.appendChild(tdActions);
                            errorTokensList.appendChild(tr);
                        });
                    } else {
                        errorTokensList.innerHTML = `
                            <tr>
                                <td colspan="3" class="border p-4 text-center text-gray-500">暫無錯誤 Token</td>
                            </tr>
                        `;
                    }

                    // 更新計數
                    tokensCountEl.textContent = (data.tokens && data.tokens.length) || 0;
                    errorTokensCountEl.textContent = (data.error_tokens && data.error_tokens.length) || 0;

                } catch (error) {
                    console.error('Error loading tokens:', error);
                    const errorMsg = `載入 tokens 失敗: ${error.message}`;
                    showPopup(errorMsg, 'error');
                    const errorRowHtml = `<tr><td colspan="3" class="border p-4 text-center text-red-500">${errorMsg}</td></tr>`;
                    errorTokensList.innerHTML = errorRowHtml;
                    tokensList.innerHTML = errorRowHtml;
                    // 重置計數
                    tokensCountEl.textContent = 'N/A';
                    errorTokensCountEl.textContent = 'N/A';
                }
            };

            // 初始載入
            window.loadTokens();

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
                        const response = await fetch(tokenAddUrl, {
                            method: 'POST',
                            body: formData
                        });

                        if (response.ok) {
                            tokenInput.value = '';
                            if (descriptionInput) descriptionInput.value = '';
                            window.loadTokens(); // 重新載入列表
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
                            await window.executeClearTokens();
                            // 成功消息由 executeClearTokens 處理
                        } catch (error) {
                            console.error('Error clearing tokens from form:', error);
                            showPopup(`清空失敗: ${error.message}`, 'error'); // 顯示執行錯誤
                        }
                    } else {
                        console.log('Clear tokens cancelled.');
                    }
                });
            } else {
                console.warn("Element with ID 'clearForm' not found.");
            }
        }
    }
});