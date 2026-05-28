/**
 * API 客户端 - 封装后端 API 调用
 */

const API_BASE_URL = '/api/v1';

/**
 * 创建 Axios 实例
 */
const apiClient = axios.create({
    baseURL: API_BASE_URL,
    timeout: 30000,
    headers: {
        'Content-Type': 'application/json'
    }
});

/**
 * 请求拦截器
 */
apiClient.interceptors.request.use(
    config => {
        console.log(`📤 请求: ${config.method.toUpperCase()} ${config.url}`);
        return config;
    },
    error => {
        console.error('❌ 请求错误:', error);
        return Promise.reject(error);
    }
);

/**
 * 响应拦截器
 */
apiClient.interceptors.response.use(
    response => {
        console.log(`📥 响应: ${response.status}`, response.data);
        return response.data;
    },
    error => {
        console.error('❌ 响应错误:', error);
        if (error.response) {
            return Promise.reject({
                status: error.response.status,
                message: error.response.data?.detail || '请求失败',
                data: error.response.data
            });
        }
        return Promise.reject({
            status: 0,
            message: error.message || '网络错误'
        });
    }
);

/**
 * Chat API - 发送消息
 * @param {string} message - 用户消息
 * @param {string} threadId - 对话线程 ID
 * @param {string} imageUrl - 图片 URL（可选）
 * @returns {Promise}
 */
async function sendChatMessage(message, threadId, imageUrl = null) {
    try {
        const payload = {
            message,
            thread_id: threadId
        };

        if (imageUrl) {
            payload.image_url = imageUrl;
        }

        const response = await apiClient.post('/chat', payload);
        return response;
    } catch (error) {
        console.error('❌ Chat API 错误:', error);
        throw error;
    }
}

/**
 * OSS API - 获取上传签名
 * @returns {Promise}
 */
async function getOSSSignature() {
    try {
        const response = await apiClient.post('/upload-signature');
        return response;
    } catch (error) {
        console.error('❌ OSS API 错误:', error);
        throw error;
    }
}

/**
 * 上传文件到 OSS
 * @param {File} file - 文件对象
 * @returns {Promise}
 */
async function uploadFileToOSS(file) {
    try {
        // 获取签名
        const signatureData = await getOSSSignature();
        const { signature: sig } = signatureData;

        // 创建 FormData
        const formData = new FormData();
        formData.append('key', `${sig.dir}${Date.now()}_${file.name}`);
        formData.append('policy', sig.policy);
        formData.append('OSSAccessKeyId', sig.accessKeyId);
        formData.append('signature', sig.signature);
        formData.append('file', file);

        // 上传到 OSS
        const response = await axios.post(sig.host, formData, {
            headers: {
                'Content-Type': 'multipart/form-data'
            }
        });

        // 返回文件 URL
        const fileUrl = `${sig.host}/${formData.get('key')}`;
        return fileUrl;
    } catch (error) {
        console.error('❌ 文件上传错误:', error);
        throw error;
    }
}

// 导出 API 函数
window.API = {
    sendChatMessage,
    getOSSSignature,
    uploadFileToOSS
};
