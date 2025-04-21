async function loadTokens() {
    const tokensCountEl = document.getElementById('tokensCount');
    const errorTokensCountEl = document.getElementById('errorTokensCount');
    const tokenSearchInput = document.getElementById('tokenSearchInput');
    const allTokensList = document.getElementById('allTokensList');

    try {
        const response = await fetch(`${apiBaseUrl}/api/token/list`);
        if (!response.ok) {
            throw new Error(`獲取Token列表失敗 (HTTP ${response.status})`);
        }
        const data = await response.json();

        // 合併所有 tokens 到一個陣列
        const allTokens = [
            ...(data.tokens || []).map(token => ({ ...token, is_error: false })),
            ...(data.error_tokens || []).map(token => ({ ...token, is_error: true }))
        ];

        // 設置搜尋功能
        if (tokenSearchInput) {
            tokenSearchInput.addEventListener('input', function () {
                const searchTerm = this.value.toLowerCase().trim();
                displayFilteredTokens(allTokens, searchTerm);
            });
        }

        // 初始顯示所有tokens
        displayFilteredTokens(allTokens, '');

        // 更新計數
        if (tokensCountEl && errorTokensCountEl) {
            tokensCountEl.textContent = data.tokens?.length || 0;
            errorTokensCountEl.textContent = data.error_tokens?.length || 0;
        }

    } catch (error) {
        console.error('Error loading tokens:', error);
        const errorMsg = `載入 tokens 失敗: ${error.message}`;
        showPopup(errorMsg, 'error');
        if (allTokensList) {
            const errorRowHtml = `<tr><td colspan="6" class="border p-4 text-center text-red-500">${errorMsg}</td></tr>`;
            allTokensList.innerHTML = errorRowHtml;
        }
        // 重置計數
        if (tokensCountEl && errorTokensCountEl) {
            tokensCountEl.textContent = 'N/A';
            errorTokensCountEl.textContent = 'N/A';
        }
    }
};

// 顯示筛選後的 tokens
function displayFilteredTokens(allTokens, searchTerm) {
    const allTokensList = document.getElementById('allTokensList');
    if (!allTokensList) return;

    allTokensList.innerHTML = '';

    // 筛選符合搜尋條件的 tokens
    const filteredTokens = allTokens.filter(token =>
        token.token.toLowerCase().includes(searchTerm)
    );

    if (filteredTokens.length > 0) {
        filteredTokens.forEach(token => {
            const tr = document.createElement('tr');
            tr.className = token.is_error ? 'bg-red-50' : '';

            // ID 列
            const tdId = document.createElement('td');
            tdId.className = "border p-2";
            tdId.textContent = token.id;
            tr.appendChild(tdId);

            // Token 列
            const tdToken = document.createElement('td');
            tdToken.className = "border p-2 truncate max-w-[80px]";
            tdToken.textContent = token.token;
            tr.appendChild(tdToken);

            // 描述列
            const tdDesc = document.createElement('td');
            tdDesc.className = "border p-2";
            tdDesc.textContent = token.description || '無描述';
            tr.appendChild(tdDesc);

            // 建立時間列
            const tdCreatedAt = document.createElement('td');
            tdCreatedAt.className = "border p-2";
            // 格式化時間為本地格式
            const createdDate = new Date(token.created_at);
            tdCreatedAt.textContent = createdDate.toLocaleString();
            tr.appendChild(tdCreatedAt);

            // 可用狀態列
            const tdStatus = document.createElement('td');
            tdStatus.className = "border p-2";

            const statusSpan = document.createElement('span');
            statusSpan.className = token.is_error ? 'bg-red-200 text-red-800 py-1 px-2 rounded' : 'bg-green-200 text-green-800 py-1 px-2 rounded';
            statusSpan.textContent = token.is_error ? '不可用' : '可用';
            tdStatus.appendChild(statusSpan);

            tr.appendChild(tdStatus);

            // 操作列
            const tdActions = document.createElement('td');
            tdActions.className = "border p-2";

            // 狀態切換按鈕
            const toggleStatusButton = document.createElement('button');
            if (token.is_error) {
                toggleStatusButton.textContent = '標記為可用';
                toggleStatusButton.className = 'bg-green-500 text-white py-1 px-2 rounded hover:bg-green-600 mr-2';
                toggleStatusButton.addEventListener('click', async () => {
                    const confirmed = await showConfirm('確定要將此 Token 標記為可用嗎？');
                    if (confirmed) {
                        try {
                            await window.executeMarkAsValid(token.id);
                        } catch (error) {
                            console.error('Error marking token as valid from button:', error);
                            showPopup(`標記為可用失敗: ${error.message}`, 'error');
                        }
                    }
                });
            } else {
                toggleStatusButton.textContent = '標記為錯誤';
                toggleStatusButton.className = 'bg-yellow-500 text-white py-1 px-2 rounded hover:bg-yellow-600 mr-2';
                toggleStatusButton.addEventListener('click', async () => {
                    const confirmed = await showConfirm('確定要將此 Token 標記為錯誤嗎？');
                    if (confirmed) {
                        try {
                            await window.executeMarkAsError(token.id);
                        } catch (error) {
                            console.error('Error marking token as error from button:', error);
                            showPopup(`標記錯誤失敗: ${error.message}`, 'error');
                        }
                    }
                });
            }

            // 刪除按鈕
            const deleteButton = document.createElement('button');
            deleteButton.textContent = '刪除';
            deleteButton.className = 'bg-red-500 text-white py-1 px-2 rounded hover:bg-red-600';
            deleteButton.addEventListener('click', async () => {
                const confirmed = await showConfirm('確定要刪除此 Token 嗎？這個操作不可撤銷！');
                if (confirmed) {
                    try {
                        await window.executeDeleteToken(token.id);
                    } catch (error) {
                        console.error('Error deleting token from button:', error);
                        showPopup(`刪除失敗: ${error.message}`, 'error');
                    }
                }
            });

            tdActions.appendChild(toggleStatusButton);
            tdActions.appendChild(deleteButton);
            tr.appendChild(tdActions);

            allTokensList.appendChild(tr);
        });
    } else {
        allTokensList.innerHTML = `
            <tr>
                <td colspan="6" class="border p-4 text-center text-gray-500">沒有找到符合條件的 Token</td>
            </tr>
        `;
    }
}

async function executeUpdateTokenStatus(tokenId, isError) {
    const formData = new FormData();
    formData.append('is_error', isError);
    try {
        const url = `${apiBaseUrl}/api/token/update-status/${tokenId}`;
        const response = await fetch(url, {
            method: 'POST',
            body: formData,
        });
        if (response.ok) {
            if (loadTokens) loadTokens();
            showPopup('Token 狀態已更新', 'success');
        } else {
            const errorData = await response.json();
            throw new Error(errorData.detail || `更新狀態失敗 (HTTP ${response.status})`);
        }
    } catch (error) {
        console.error('Error in executeUpdateTokenStatus:', error);
        throw error;
    }
}

async function executeMarkAsError(tokenId) {
    await executeUpdateTokenStatus(tokenId, true);
};

async function executeMarkAsValid(tokenId) {
    await executeUpdateTokenStatus(tokenId, false);
}

async function executeDeleteToken(tokenId) {
    try {
        const url = `${apiBaseUrl}/api/token/delete/${tokenId}`;
        const response = await fetch(url, {
            method: 'POST'
        });

        if (response.ok) {
            if (loadTokens) loadTokens();
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

async function executeClearTokens() {
    try {
        const response = await fetch(`${apiBaseUrl}/api/token/clear`, {
            method: 'POST'
        });

        if (response.ok) {
            if (loadTokens) loadTokens();
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