let currentPipelineValves = {};
let hasUnsavedChanges = false;


function initializeFileInput() {
    const fileInput = document.getElementById('fileInput');
    const uploadedFileName = document.getElementById('uploadedFileName');
    const uploadPipelineBtn = document.getElementById('uploadPipelineBtn');
    
    if (fileInput && uploadedFileName) {
        // 初始狀態下禁用上傳按鈕，因為還沒有選擇檔案
        if (uploadPipelineBtn) {
            uploadPipelineBtn.disabled = true;
        }
        
        fileInput.addEventListener('change', function() {
            if (this.files.length > 0) {
                uploadedFileName.textContent = `上傳檔案：${this.files[0].name}`;
                uploadedFileName.classList.remove('hidden');
                // 選擇檔案後啟用上傳按鈕
                if (uploadPipelineBtn) {
                    uploadPipelineBtn.disabled = false;
                }
            } else {
                uploadedFileName.classList.add('hidden');
                // 沒有選擇檔案時禁用上傳按鈕
                if (uploadPipelineBtn) {
                    uploadPipelineBtn.disabled = true;
                }
            }
        });
    }
}

async function loadPipelines() {
    let pipelinesList = document.getElementById('pipelinesList');
    try {
        const response = await fetch(`${apiBaseUrl}/api/pipelines/list`);
        if (!response.ok) {
            throw new Error(`獲取 Pipeline 列表失敗 (HTTP ${response.status})`);
        }

        const data = await response.json();

        // 更新 Pipeline 列表
        renderPipelinesList(data.data);

        // 更新 Pipeline 選擇下拉框
        updatePipelineSelect(data.data);

    } catch (error) {
        console.error('加載 Pipeline 列表錯誤:', error);
        showPopup(`加載失敗: ${error.message}`, 'error');

        if (pipelinesList) {
            pipelinesList.innerHTML = `
                <tr>
                    <td colspan="5" class="border p-4 text-center text-red-500">加載 Pipeline 列表失敗: ${error.message}</td>
                </tr>
            `;
        }
    }
}

function renderPipelinesList(pipelines) {
    let pipelinesList = document.getElementById('pipelinesList');
    let pipelineSelect = document.getElementById('pipelineSelect');
    let valveSettingsContainer = document.getElementById('valveSettingsContainer');

    if (!pipelinesList) return;

    pipelinesList.innerHTML = '';

    if (pipelines && pipelines.length > 0) {
        pipelines.forEach(pipeline => {
            const tr = document.createElement('tr');

            // ID
            const tdId = document.createElement('td');
            tdId.className = "border p-2";
            tdId.textContent = pipeline.id;

            // 名稱
            const tdName = document.createElement('td');
            tdName.className = "border p-2";
            tdName.textContent = pipeline.name;

            // 類型
            const tdType = document.createElement('td');
            tdType.className = "border p-2";
            tdType.textContent = pipeline.type || 'N/A';

            // URL
            const tdUrl = document.createElement('td');
            tdUrl.className = "border p-2";
            tdUrl.textContent = pipeline.url || 'Local';

            // 操作
            const tdActions = document.createElement('td');
            tdActions.className = "border p-2";

            // 閥門設置按鈕
            const valveBtn = document.createElement('button');
            valveBtn.textContent = '閥門設置';
            valveBtn.className = 'bg-blue-500 text-white py-1 px-2 rounded hover:bg-blue-600 mr-2';
            valveBtn.addEventListener('click', () => {
                pipelineSelect.value = pipeline.id;
                pipelineSelect.dispatchEvent(new Event('change'));
                // 滾動到閥門設置區域
                valveSettingsContainer.scrollIntoView({ behavior: 'smooth' });
            });

            tdActions.appendChild(valveBtn);

            tr.appendChild(tdId);
            tr.appendChild(tdName);
            tr.appendChild(tdType);
            tr.appendChild(tdUrl);
            tr.appendChild(tdActions);

            pipelinesList.appendChild(tr);
        });
    } else {
        pipelinesList.innerHTML = `
            <tr>
                <td colspan="5" class="border p-4 text-center text-gray-500">暫無 Pipeline</td>
            </tr>
        `;
    }
}

function updatePipelineSelect(pipelines) {
    let pipelineSelect = document.getElementById('pipelineSelect');

    if (!pipelineSelect) return;

    // 保存當前選擇的值
    const currentValue = pipelineSelect.value;

    // 完全清空選擇框
    pipelineSelect.innerHTML = '';
    
    // 完成加載後預設選項
    const defaultOption = document.createElement('option');
    defaultOption.value = '';
    defaultOption.textContent = '-- 請選擇一個 Pipeline --';
    pipelineSelect.appendChild(defaultOption);

    // 添加新選項
    if (pipelines && pipelines.length > 0) {
        pipelines.forEach(pipeline => {
            const option = document.createElement('option');
            option.value = pipeline.id;
            option.textContent = pipeline.name;
            pipelineSelect.appendChild(option);
        });

        // 嘗試恢復之前的選擇
        if (currentValue) {
            pipelineSelect.value = currentValue;
        }
    }
}


async function loadValveSettings(pipelineId) {
    let settingsContainer = document.getElementById('valveSettingsContainer');
    let currentPipelineConfig = {};

    if (!pipelineId) {
        settingsContainer.innerHTML = `<p class="text-gray-500 text-center">請選擇一個 Pipeline 以加載配置設置</p>`;
        hasUnsavedChanges = false;
        return;
    }

    try {
        settingsContainer.innerHTML = `<p class="text-gray-500 text-center">正在加載配置設置...</p>`;

        // 首先獲取欄位規格以了解被處理的欄位類型
        const specResponse = await fetch(`${apiBaseUrl}/api/pipelines/${pipelineId}/valves/spec`);
        if (!specResponse.ok) {
            throw new Error(`獲取單元規格失敗 (HTTP ${specResponse.status})`);
        }
        const fieldSpecs = await specResponse.json();
        
        // 然後獲取實際的酬門值
        const valveResponse = await fetch(`${apiBaseUrl}/api/pipelines/${pipelineId}/valves`);
        if (!valveResponse.ok) {
            throw new Error(`獲取閥門值失敗 (HTTP ${valveResponse.status})`);
        }
        const valveData = await valveResponse.json();

        // 渲染表單，使用規格信息確定正確的類型
        renderValveSettingsWithSpecs(valveData, fieldSpecs);
        hasUnsavedChanges = false;
    } catch (error) {
        console.error('加載配置設置錯誤:', error);
        settingsContainer.innerHTML = `<p class="text-red-500 text-center">加載配置設置失敗: ${error.message || '未知錯誤'}</p>`;
        hasUnsavedChanges = false;
    }
}


function renderValveSettingsWithSpecs(valveData, fieldSpecs) {
    let valveSettingsContainer = document.getElementById('valveSettingsContainer');

    if (!valveSettingsContainer) return;

    if (!valveData || Object.keys(valveData).length === 0) {
        valveSettingsContainer.innerHTML = `<p class="text-gray-500 text-center">此 Pipeline 沒有可配置的閥門</p>`;
        return;
    }

    let html = `<div class="grid grid-cols-1 gap-4">`;

    // 取得選項長度
    const orderedKeys = Object.keys(valveData);

    orderedKeys.forEach(key => {
        // 取得該欄位的值、類型規格和標題
        const value = valveData[key];
        const spec = fieldSpecs[key] || {};
        const inputId = `valve_${key}`;
        const fieldType = getFieldType(spec); // 從規格確定欄位類型
        const fieldTitle = spec.title || key;
        const isNullable = spec.anyOf && spec.anyOf.some(type => type.type === "null");
        
        // 安全處理原始值
        const originalValue = (value === null || value === undefined) ? '' : String(value);
        const displayValue = (value === null || value === undefined) ? '' : value;
        
        html += `<div class="mb-4">`;
        html += `<label for="${inputId}" class="block text-sm font-medium text-gray-700 mb-1">${fieldTitle}</label>`;

        // 根據欄位類型渲染不同的輸入控件
        switch (fieldType) {
            case 'boolean':
                const checked = value === true || value === "true" ? 'checked' : '';
                html += `
                    <div class="flex items-center">
                        <input type="checkbox" id="${inputId}" 
                            class="h-5 w-5 border border-gray-300 rounded focus:outline-none focus:ring-2 focus:ring-blue-400"
                            ${checked}
                            data-valve-id="${key}"
                            data-valve-type="${fieldType}"
                            data-original-value="${value === true || value === "true" ? 'true' : 'false'}"
                            onchange="window.checkValveChanges(this)"
                        >
                        <label for="${inputId}" class="ml-2">啟用</label>
                    </div>
                `;
                break;
                
            case 'integer':
            case 'number':
                // 取得數字欄位限制
                const min = spec.minimum !== undefined ? spec.minimum : '';
                const max = spec.maximum !== undefined ? spec.maximum : '';
                
                html += `
                    <input type="number" id="${inputId}" 
                        class="w-full p-2 border border-gray-300 rounded focus:outline-none focus:ring-2 focus:ring-blue-400"
                        value="${displayValue}" 
                        ${min !== '' ? `min="${min}"` : ''}
                        ${max !== '' ? `max="${max}"` : ''}
                        data-valve-id="${key}"
                        data-valve-type="${fieldType}"
                        data-original-value="${originalValue}"
                        onchange="window.checkValveChanges(this)"
                    >
                    ${isNullable ? `<p class="text-xs text-gray-500 mt-1">可以為空值。</p>` : ''}
                `;
                break;
                
            case 'array':
                let arrayValue = '';
                try {
                    if (value) {
                        // 確保數組會被正確格式化
                        arrayValue = JSON.stringify(value, null, 2);
                    }
                } catch (e) {
                    // 如果不是有效的 JSON，使用原始文本
                    arrayValue = String(value || '');
                }
                
                html += `
                    <textarea id="${inputId}" 
                        class="w-full p-2 border border-gray-300 rounded focus:outline-none focus:ring-2 focus:ring-blue-400 font-mono text-sm"
                        rows="4"
                        data-valve-id="${key}"
                        data-valve-type="${fieldType}"
                        data-original-value="${escapeHtml(originalValue)}"
                        onchange="window.checkValveChanges(this)"
                    >${escapeHtml(arrayValue)}</textarea>
                    <p class="text-xs text-gray-500 mt-1">請輸入有效的 JSON 數組。</p>
                `;
                break;
                
            case 'object':
                let objectValue = '';
                try {
                    if (value) {
                        // 確保物件會被正確格式化
                        objectValue = JSON.stringify(value, null, 2);
                    }
                } catch (e) {
                    // 如果不是有效的 JSON，使用原始文本
                    objectValue = String(value || '');
                }
                
                html += `
                    <textarea id="${inputId}" 
                        class="w-full p-2 border border-gray-300 rounded focus:outline-none focus:ring-2 focus:ring-blue-400 font-mono text-sm"
                        rows="4"
                        data-valve-id="${key}"
                        data-valve-type="${fieldType}"
                        data-original-value="${escapeHtml(originalValue)}"
                        onchange="window.checkValveChanges(this)"
                    >${escapeHtml(objectValue)}</textarea>
                    <p class="text-xs text-gray-500 mt-1">請輸入有效的 JSON 物件。</p>
                `;
                break;
                
            case 'enum':
                html += `<select id="${inputId}" 
                    class="w-full p-2 border border-gray-300 rounded focus:outline-none focus:ring-2 focus:ring-blue-400"
                    data-valve-id="${key}"
                    data-valve-type="${fieldType}"
                    data-original-value="${originalValue}"
                    onchange="window.checkValveChanges(this)"
                >`;

                // 如果可為空值，增加空選項
                if (isNullable) {
                    html += `<option value=""${!value ? ' selected' : ''}>-- 請選擇 --</option>`;
                }

                // 添加所有可用選項
                if (spec.enum && Array.isArray(spec.enum)) {
                    spec.enum.forEach(option => {
                        const optionValue = String(option);
                        const optionLabel = option;
                        const selected = String(value) === optionValue ? 'selected' : '';

                        html += `<option value="${optionValue}"${selected}>${optionLabel}</option>`;
                    });
                }

                html += `</select>`;
                break;
                
            default: // string 或其他所有默認類型
                html += `
                    <input type="text" id="${inputId}" 
                        class="w-full p-2 border border-gray-300 rounded focus:outline-none focus:ring-2 focus:ring-blue-400"
                        value="${escapeHtml(displayValue)}"
                        data-valve-id="${key}"
                        data-valve-type="${fieldType}"
                        data-original-value="${escapeHtml(originalValue)}"
                        onchange="window.checkValveChanges(this)"
                    >
                    ${isNullable ? `<p class="text-xs text-gray-500 mt-1">可以為空值。</p>` : ''}
                `;
        }

        html += `</div>`;
    });

    html += `</div>`;

    valveSettingsContainer.innerHTML = html;

    // 為 JSON 區域添加失去焦點事件，執行格式化
    document.querySelectorAll('textarea[data-valve-type="array"], textarea[data-valve-type="object"]').forEach(elem => {
        elem.addEventListener('blur', function () {
            try {
                const value = this.value.trim();
                if (value) {
                    this.value = JSON.stringify(JSON.parse(value), null, 2);
                    this.classList.remove('border-red-500');
                }
            } catch (e) {
                console.warn('JSON 格式化失敗:', e.message);
                this.classList.add('border-red-500'); // 增加紅色警示框
            }
        });
    });
}

// 根據規格確定欄位類型
function getFieldType(spec) {
    // 直接使用規格中的類型字段
    if (spec.type) {
        // 若類型是正常的原始類型，直接返回
        if (['string', 'number', 'integer', 'boolean', 'array', 'object'].includes(spec.type)) {
            return spec.type;
        }
    }
    
    // 檢查是否為枚舉類型
    if (spec.enum && Array.isArray(spec.enum)) {
        return 'enum';
    }
    
    // 檢查 anyOf 給空值型別
    if (spec.anyOf && Array.isArray(spec.anyOf)) {
        // 找出非 NULL 的類型
        for (const typeOption of spec.anyOf) {
            if (typeOption.type !== 'null') {
                return typeOption.type;
            }
        }
    }
    
    // 默認返回字串類型
    return 'string';
}



function escapeHtml(unsafe) {
    if (unsafe === null || typeof unsafe === 'undefined') return '';
    return String(unsafe)
        .replace(/&/g, "&")
        .replace(/</g, "<")
        .replace(/>/g, ">")
        .replace(/\"/g, "\"")
        .replace(/'/g, "'");
}



function renderValveSettings(valves) {
    let valveSettingsContainer = document.getElementById('valveSettingsContainer');

    if (!valveSettingsContainer) return;

    if (!valves || valves.length === 0) {
        valveSettingsContainer.innerHTML = `<p class="text-gray-500 text-center">此 Pipeline 沒有可配置的閥門</p>`;
        return;
    }

    let html = `<div class="grid grid-cols-1 gap-4">`;

    // 按照 order 排序閥門
    valves.sort((a, b) => (a.order || 0) - (b.order || 0));

    valves.forEach(valve => {
        const valveId = `valve_${valve.id}`;

        html += `
            <div class="mb-4 p-4 border rounded">
                <div class="font-semibold mb-2">${valve.name}</div>
                <p class="text-sm text-gray-600 mb-2">${valve.description || ''}</p>
        `;

        // 根據類型渲染不同的輸入控件
        switch (valve.type) {
            case 'string':
                html += `
                    <input type="text" id="${valveId}" 
                        class="w-full p-2 border border-gray-300 rounded focus:outline-none focus:ring-2 focus:ring-blue-400"
                        value="${valve.value || ''}" 
                        ${valve.required ? 'required' : ''}
                        data-valve-id="${valve.id}"
                        data-valve-type="${valve.type}"
                        data-original-value="${valve.value || ''}"
                        onchange="checkValveChanges(this)"
                    >
                `;
                break;

            case 'number':
                html += `
                    <input type="number" id="${valveId}" 
                        class="w-full p-2 border border-gray-300 rounded focus:outline-none focus:ring-2 focus:ring-blue-400"
                        value="${valve.value || ''}" 
                        ${valve.min_value !== null ? `min="${valve.min_value}"` : ''}
                        ${valve.max_value !== null ? `max="${valve.max_value}"` : ''}
                        ${valve.required ? 'required' : ''}
                        data-valve-id="${valve.id}"
                        data-valve-type="${valve.type}"
                        data-original-value="${valve.value || ''}"
                        onchange="checkValveChanges(this)"
                    >
                `;
                break;

            case 'boolean':
                const checked = valve.value === 'true' || valve.value === true ? 'checked' : '';
                html += `
                    <div class="flex items-center">
                        <input type="checkbox" id="${valveId}" 
                            class="h-5 w-5 border border-gray-300 rounded focus:outline-none focus:ring-2 focus:ring-blue-400"
                            ${checked}
                            data-valve-id="${valve.id}"
                            data-valve-type="${valve.type}"
                            data-original-value="${valve.value === 'true' || valve.value === true ? 'true' : 'false'}"
                            onchange="checkValveChanges(this)"
                        >
                        <label for="${valveId}" class="ml-2">啟用</label>
                    </div>
                `;
                break;

            case 'json':
                let jsonValue = '';
                try {
                    if (valve.value) {
                        jsonValue = JSON.stringify(JSON.parse(valve.value), null, 2);
                    }
                } catch (e) {
                    jsonValue = valve.value || '';
                }

                html += `
                    <textarea id="${valveId}" 
                        class="w-full p-2 border border-gray-300 rounded focus:outline-none focus:ring-2 focus:ring-blue-400 font-mono text-sm"
                        rows="4"
                        ${valve.required ? 'required' : ''}
                        data-valve-id="${valve.id}"
                        data-valve-type="${valve.type}"
                        data-original-value="${valve.value ? valve.value.replace(/"/g, '&quot;') : ''}"
                        onchange="checkValveChanges(this)"
                    >${jsonValue}</textarea>
                `;
                break;

            case 'select':
                html += `<select id="${valveId}" 
                    class="w-full p-2 border border-gray-300 rounded focus:outline-none focus:ring-2 focus:ring-blue-400"
                    ${valve.required ? 'required' : ''}
                    data-valve-id="${valve.id}"
                    data-valve-type="${valve.type}"
                    data-original-value="${valve.value || ''}"
                    onchange="checkValveChanges(this)"
                >`;

                // 添加空選項
                if (!valve.required) {
                    html += `<option value=""${!valve.value ? ' selected' : ''}>-- 請選擇 --</option>`;
                }

                // 添加選項
                if (valve.options && Array.isArray(valve.options)) {
                    valve.options.forEach(option => {
                        const optionValue = typeof option === 'object' ? option.value : option;
                        const optionLabel = typeof option === 'object' ? option.label : option;
                        const selected = valve.value === optionValue.toString() ? 'selected' : '';

                        html += `<option value="${optionValue}"${selected}>${optionLabel}</option>`;
                    });
                }

                html += `</select>`;
                break;

            default:
                html += `
                    <input type="text" id="${valveId}" 
                        class="w-full p-2 border border-gray-300 rounded focus:outline-none focus:ring-2 focus:ring-blue-400"
                        value="${valve.value || ''}" 
                        ${valve.required ? 'required' : ''}
                        data-valve-id="${valve.id}"
                        data-valve-type="${valve.type}"
                        data-original-value="${valve.value || ''}"
                        onchange="checkValveChanges(this)"
                    >
                `;
        }

        html += `</div>`;
    });

    html += `</div>`;

    valveSettingsContainer.innerHTML = html;

    // 初始化 JSON 編輯器
    document.querySelectorAll('[data-valve-type="json"]').forEach(elem => {
        elem.addEventListener('blur', function () {
            try {
                // 嘗試格式化 JSON
                const value = this.value.trim();
                if (value) {
                    this.value = JSON.stringify(JSON.parse(value), null, 2);
                }
            } catch (e) {
                // 如果格式化失敗，保持原樣
                console.warn('JSON 格式化失敗:', e);
            }
        });
    });
}



function checkValveChanges(element) {
    if (!element) return;

    const originalValue = element.getAttribute('data-original-value');
    let currentValue;

    // 根據元素類型獲取當前值
    if (element.type === 'checkbox') {
        currentValue = element.checked ? 'true' : 'false';
    } else {
        currentValue = element.value;
    }

    // 檢查值是否變更
    if (originalValue !== currentValue) {
        hasUnsavedChanges = true;
        element.classList.add('bg-yellow-50');
    } else {
        element.classList.remove('bg-yellow-50');

        // 檢查是否還有其他未保存的變更
        hasUnsavedChanges = Array.from(
            document.querySelectorAll('[data-valve-id]')
        ).some(el => {
            const origVal = el.getAttribute('data-original-value');
            const currVal = el.type === 'checkbox' ? (el.checked ? 'true' : 'false') : el.value;
            return origVal !== currVal;
        });
    }
}



async function saveValveSettings() {
    let pipelineSelect = document.getElementById('pipelineSelect');
    let saveBtn = document.getElementById('savePipelineSettingsBtn');

    const pipelineId = pipelineSelect.value;
    if (!pipelineId) {
        showPopup('請先選擇一個 Pipeline', 'error');
        return;
    }

    try {
        // 加載該 Pipeline 的欄位規格，以了解哪些欄位可為 null
        const specResponse = await fetch(`${apiBaseUrl}/api/pipelines/${pipelineId}/valves/spec`);
        if (!specResponse.ok) {
            throw new Error(`獲取單元規格失敗 (HTTP ${specResponse.status})`);
        }
        const fieldSpecs = await specResponse.json();

        // 收集所有閥門設置
        const valveSettings = {};
        document.querySelectorAll('[data-valve-id]').forEach(element => {
            const valveId = element.getAttribute('data-valve-id');
            const valveType = element.getAttribute('data-valve-type');
            const spec = fieldSpecs[valveId] || {};
            const isNullable = spec.anyOf && spec.anyOf.some(type => type.type === "null");
            let value;

            // 根據類型獲取值
            if (element.type === 'checkbox') {
                value = element.checked;
            } else {
                value = element.value;
            }

            // 從特定屬性的處理方式開始
            // 直接給值而不是包裝在物件中
            if (valveId === 'pipelines') {
                // 特別處理 pipelines 欄位，將其轉換為數組
                try {
                    if (value && value.trim() !== '') {
                        // 先嘗試作為 JSON 數組解析
                        try {
                            value = JSON.parse(value);
                            if (!Array.isArray(value)) {
                                // 如果解析成功但不是數組，轉換為數組
                                value = [value];
                            }
                        } catch (e) {
                            // 如果解析失敗，將逗號分隔的字串拆分為數組
                            value = value.split(/\s*,\s*/).filter(Boolean);
                        }
                    } else if (isNullable) {
                        value = null;
                    } else {
                        value = []; // 默認空數組
                    }
                } catch (e) {
                    console.error('處理 pipelines 欄位錯誤:', e);
                    showPopup(`解析 pipelines 欄位失敗: ${e.message}`, 'error');
                    throw e;
                }
                valveSettings[valveId] = value; // 直接設置相應值
            } else if (valveId === 'priority') {
                // priority 需要是整數
                valveSettings[valveId] = value === '' || value === null ? 0 : parseInt(value);
            } else if ([
                'requests_per_minute',
                'requests_per_hour',
                'sliding_window_limit',
                'sliding_window_minutes'
            ].includes(valveId)) {
                // 讓這些值可以為空，空則為 null
                valveSettings[valveId] = value === '' ? null : parseInt(value);
            } else if (valveType === 'number' || valveType === 'integer') {
                // 一般數字欄位的處理
                if (value !== '' && value !== null) {
                    if (String(value).includes('.')) {
                        valveSettings[valveId] = parseFloat(value);
                    } else {
                        valveSettings[valveId] = parseInt(value);
                    }
                } else if (isNullable) {
                    valveSettings[valveId] = null;
                } else {
                    valveSettings[valveId] = 0; // 非空欄位的默認值
                }
            } else if (valveType === 'array') {
                try {
                    if (value && value.trim() !== '') {
                        valveSettings[valveId] = JSON.parse(value);
                    } else if (isNullable) {
                        valveSettings[valveId] = null;
                    } else {
                        valveSettings[valveId] = []; // 默認空數組
                    }
                } catch (e) {
                    console.error('JSON 解析錯誤:', e);
                    showPopup(`JSON 格式錯誤: ${e.message}`, 'error');
                    throw e;
                }
            } else if (valveType === 'object') {
                try {
                    if (value && value.trim() !== '') {
                        valveSettings[valveId] = JSON.parse(value);
                    } else if (isNullable) {
                        valveSettings[valveId] = null;
                    } else {
                        valveSettings[valveId] = {}; // 默認空物件
                    }
                } catch (e) {
                    console.error('JSON 解析錯誤:', e);
                    showPopup(`JSON 格式錯誤: ${e.message}`, 'error');
                    throw e;
                }
            } else {
                // 其他一般值就直接設置
                valveSettings[valveId] = value;
            }
        });
        
        console.log('Submitting settings:', valveSettings);

        // 設置按鈕為載入狀態
        saveBtn.setAttribute('data-loading', 'true');
        const originalContent = saveBtn.textContent;
        saveBtn.innerHTML = `
            <svg class="animate-spin -ml-1 mr-2 h-5 w-5 text-white inline" xmlns="http://www.w3.org/2000/svg" fill="none" viewBox="0 0 24 24">
                <circle class="opacity-25" cx="12" cy="12" r="10" stroke="currentColor" stroke-width="4"></circle>
                <path class="opacity-75" fill="currentColor" d="M4 12a8 8 0 018-8V0C5.373 0 0 5.373 0 12h4zm2 5.291A7.962 7.962 0 014 12H0c0 3.042 1.135 5.824 3 7.938l3-2.647z"></path>
            </svg>
            儲存中...
        `;
        saveBtn.disabled = true;

        const response = await fetch(`${apiBaseUrl}/api/pipelines/${pipelineId}/valves/update`, {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json'
            },
            body: JSON.stringify(valveSettings)
        });

        if (!response.ok) {
            const errorData = await response.json();
            throw new Error(errorData.detail || `保存失敗 (HTTP ${response.status})`);
        }

        showPopup('閥門設置已保存', 'success');
        hasUnsavedChanges = false;

        // 重新加載閥門設置
        loadValveSettings(pipelineId);

    } catch (error) {
        console.error('保存閥門設置錯誤:', error);
        showPopup(`保存失敗: ${error.message}`, 'error');
    } finally {
        // 無論是否成功都恢復按鈕狀態
        saveBtn.setAttribute('data-loading', 'false');
        saveBtn.innerHTML = '儲存';
        saveBtn.disabled = false;
    }
}



async function handleUploadPipeline(event) {
    let uploadPipelineForm = document.getElementById('uploadPipelineForm');
    const uploadPipelineBtn = document.getElementById('uploadPipelineBtn');
    const uploadedFileName = document.getElementById('uploadedFileName');

    event.preventDefault();
    const formData = new FormData(uploadPipelineForm);

    try {
        // 保存原始圖標
        const originalContent = uploadPipelineBtn.innerHTML;
        uploadPipelineBtn.innerHTML = `
            <svg class="animate-spin h-5 w-5 text-white" xmlns="http://www.w3.org/2000/svg" fill="none" viewBox="0 0 24 24">
                <circle class="opacity-25" cx="12" cy="12" r="10" stroke="currentColor" stroke-width="4"></circle>
                <path class="opacity-75" fill="currentColor" d="M4 12a8 8 0 018-8V0C5.373 0 0 5.373 0 12h4zm2 5.291A7.962 7.962 0 014 12H0c0 3.042 1.135 5.824 3 7.938l3-2.647z"></path>
            </svg>
        `;
        uploadPipelineBtn.disabled = true;

        const response = await fetch(`${apiBaseUrl}/api/pipelines/upload`, {
            method: 'POST',
            body: formData
        });

        if (!response.ok) {
            const errorData = await response.json();
            throw new Error(errorData.detail || `上傳失敗 (HTTP ${response.status})`);
        }

        showPopup('Pipeline 上傳成功!', 'success');
        
        // 恢復原始圖標
        uploadPipelineBtn.innerHTML = originalContent;
        uploadPipelineBtn.disabled = false;
        
        // 清空表單和檔案名稱顯示
        uploadPipelineForm.reset();
        uploadedFileName.textContent = '';
        uploadedFileName.classList.add('hidden');

        // 重新載入 pipeline 列表
        loadPipelines();
    } catch (error) {
        console.error('上傳 Pipeline 錯誤:', error);
        showPopup(`上傳失敗: ${error.message}`, 'error');
        uploadPipelineBtn.innerHTML = `
            <svg xmlns="http://www.w3.org/2000/svg" class="h-5 w-5" viewBox="0 0 20 20" fill="currentColor">
                <path fill-rule="evenodd" d="M3 17a1 1 0 011-1h12a1 1 0 110 2H4a1 1 0 01-1-1zM6.293 9.293a1 1 0 011.414 0L9 10.586V3a1 1 0 012 0v7.586l1.293-1.293a1 1 0 111.414 1.414l-3 3a1 1 0 01-1.414 0l-3-3a1 1 0 010-1.414z" transform="rotate(180 10 10)" clip-rule="evenodd" />
            </svg>
        `;
        uploadPipelineBtn.disabled = false;
    }
}



async function handleDeletePipeline(pipelineId) {
    let pipelineSelect = document.getElementById('pipelineSelect');
    let valveSettingsContainer = document.getElementById('valveSettingsContainer');
    let deleteBtn = document.getElementById('deleteSelectedPipelineBtn');

    try {
        const confirmed = await showConfirm('確定要刪除此 Pipeline 嗎？這個操作不可撤銷！');
        if (!confirmed) return;
        
        // 設置為載入中狀態
        deleteBtn.setAttribute('data-loading', 'true');
        deleteBtn.innerHTML = `
            <svg class="animate-spin h-5 w-5 text-white" xmlns="http://www.w3.org/2000/svg" fill="none" viewBox="0 0 24 24">
                <circle class="opacity-25" cx="12" cy="12" r="10" stroke="currentColor" stroke-width="4"></circle>
                <path class="opacity-75" fill="currentColor" d="M4 12a8 8 0 018-8V0C5.373 0 0 5.373 0 12h4zm2 5.291A7.962 7.962 0 014 12H0c0 3.042 1.135 5.824 3 7.938l3-2.647z"></path>
            </svg>
        `;
        deleteBtn.disabled = true;

        const response = await fetch(`${apiBaseUrl}/api/pipelines/delete?id=${pipelineId}`, {
            method: 'DELETE',
        });

        if (!response.ok) {
            const errorData = await response.json();
            throw new Error(errorData.detail || `刪除失敗 (HTTP ${response.status})`);
        }

        showPopup('Pipeline 已刪除', 'success');
        loadPipelines();

        // 如果刪除的是當前選中的 pipeline，清空閥門設置
        if (pipelineSelect.value === pipelineId) {
            pipelineSelect.value = '';
            valveSettingsContainer.innerHTML = `<p class="text-gray-500 text-center">請選擇一個 Pipeline 以加載閥門設置</p>`;
        }
    } catch (error) {
        console.error('刪除 Pipeline 錯誤:', error);
        showPopup(`刪除失敗: ${error.message}`, 'error');
    } finally {
        // 恢復按鈕狀態
        deleteBtn.setAttribute('data-loading', 'false');
        deleteBtn.innerHTML = `
            <svg xmlns="http://www.w3.org/2000/svg" class="h-5 w-5" viewBox="0 0 20 20" fill="currentColor">
                <path fill-rule="evenodd" d="M9 2a1 1 0 00-.894.553L7.382 4H4a1 1 0 000 2v10a2 2 0 002 2h8a2 2 0 002-2V6a1 1 0 100-2h-3.382l-.724-1.447A1 1 0 0011 2H9zM7 8a1 1 0 012 0v6a1 1 0 11-2 0V8zm5-1a1 1 0 00-1 1v6a1 1 0 102 0V8a1 1 0 00-1-1z" clip-rule="evenodd" />
            </svg>
        `;
        deleteBtn.disabled = false;
    }
}



function initializeEventListeners() {
    let pipelineSelect = document.getElementById('pipelineSelect');
    let saveValveSettingsBtn = document.getElementById('saveValveSettingsBtn');
    let uploadPipelineForm = document.getElementById('uploadPipelineForm');
    const deleteBtn = document.getElementById('deleteSelectedPipelineBtn');
    
    // 初始化檔案輸入框
    initializeFileInput();

    // Pipeline 選擇變更
    if (pipelineSelect) {
        pipelineSelect.addEventListener('change', async function () {
            if (hasUnsavedChanges) {
                const confirmed = await showConfirm('您有未保存的變更，確定要切換 Pipeline 嗎？');
                if (!confirmed) {
                    this.value = this.getAttribute('data-last-value') || '';
                    return;
                }
            }

            // 保存當前選擇，用於取消時恢復
            this.setAttribute('data-last-value', this.value);

            loadValveSettings(this.value);

            if (deleteBtn) {
                deleteBtn.disabled = this.value === '';
            }
        });
    }

    // 保存按鈕點擊
    if (saveValveSettingsBtn) {
        saveValveSettingsBtn.addEventListener('click', saveValveSettings);
    }

    // 上傳表單提交
    if (uploadPipelineForm) {
        uploadPipelineForm.addEventListener('submit', handleUploadPipeline);
    }

    // 關閉代碼查看對話框
    const closeCodeModalBtn = document.getElementById('closeCodeModalBtn');
    if (closeCodeModalBtn) {
        closeCodeModalBtn.addEventListener('click', function () {
            document.getElementById('codeViewModal').style.display = 'none';
        });
    }

    // 關閉閥門編輯對話框
    const closeValveModalBtn = document.getElementById('closeValveModalBtn');
    if (closeValveModalBtn) {
        closeValveModalBtn.addEventListener('click', function () {
            document.getElementById('valveEditModal').style.display = 'none';
        });
    }

    // 刪除按鈕點擊
    if (deleteBtn) {
        deleteBtn.addEventListener('click', async function () {
            if (pipelineSelect.value) {
                await handleDeletePipeline(pipelineSelect.value);
            }
        });
    }
}
