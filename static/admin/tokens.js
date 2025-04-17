async function loadTokens() {
    const tokensCountEl = document.getElementById('tokensCount');
    const errorTokensCountEl = document.getElementById('errorTokensCount');

    try {
        const response = await fetch(`${apiBaseUrl}/api/token/list`);
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


async function executeMarkAsError(tokenId) {
    try {
        const url = `${apiBaseUrl}/api/token/mark-error/${tokenId}`;
        const response = await fetch(url, {
            method: 'POST'
        });

        if (response.ok) {
            if (loadTokens) loadTokens();
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
