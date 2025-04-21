async function loadUsers() {
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
                                ${user.active ? '禁用' : '啟用'}
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


async function executeToggleUserActive(userIdToToggle) {
    try {
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
            if (loadUsers) loadUsers();
        } else {
            throw new Error(result.detail || '操作未成功完成');
        }
    } catch (error) {
        console.error('Error toggling user active status:', error);
        showPopup(`更新用戶狀態失敗: ${error.message}`, 'error');
    }
};


async function executeToggleUserRole(userIdToToggle) {
    try {
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
            if (loadUsers) loadUsers();
        } else {
            throw new Error(result.detail || '操作未成功完成');
        }
    } catch (error) {
        console.error('Error toggling user role:', error);
        showPopup(`更新用戶角色失敗: ${error.message}`, 'error');
    }
};
