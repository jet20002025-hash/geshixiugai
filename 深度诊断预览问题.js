// 深度诊断预览页面问题
// 在预览页面的浏览器控制台中运行此代码

(async function diagnosePreview() {
    console.log('========== 开始诊断 ==========');
    
    const urlParams = new URLSearchParams(window.location.search);
    const docId = urlParams.get('id') || urlParams.get('document_id');
    
    if (!docId) {
        console.error('❌ 未找到文档ID');
        return;
    }
    
    console.log('✅ 文档ID:', docId);
    
    // 1. 检查页面元素
    console.log('\n--- 检查页面元素 ---');
    const loading = document.getElementById('loading');
    const error = document.getElementById('error');
    const mainPreview = document.getElementById('mainPreview');
    const loadingStep = document.getElementById('loadingStep');
    
    console.log('加载元素显示状态:', loading?.style.display || 'block');
    console.log('错误元素显示状态:', error?.style.display || 'none');
    console.log('预览容器显示状态:', mainPreview?.style.display || 'none');
    console.log('加载步骤文本:', loadingStep?.textContent);
    
    // 2. 测试预览API
    console.log('\n--- 测试预览API ---');
    try {
        const response = await fetch(`/documents/${docId}/preview`);
        console.log('响应状态:', response.status, response.statusText);
        console.log('Content-Type:', response.headers.get('content-type'));
        console.log('Content-Length:', response.headers.get('content-length') || '未知');
        
        const contentType = response.headers.get('content-type') || '';
        
        if (contentType.includes('application/pdf') || contentType.includes('pdf')) {
            console.log('✅ 响应类型: PDF');
            const blob = await response.blob();
            console.log('PDF大小:', blob.size, 'bytes', `(${(blob.size / 1024).toFixed(2)} KB)`);
            console.log('Blob类型:', blob.type);
            
            // 检查PDF.js是否加载
            if (typeof pdfjsLib === 'undefined') {
                console.error('❌ PDF.js库未加载');
            } else {
                console.log('✅ PDF.js库已加载');
            }
        } else if (contentType.includes('text/html') || contentType.includes('html')) {
            console.log('✅ 响应类型: HTML');
            const text = await response.text();
            console.log('HTML长度:', text.length, '字符');
            console.log('HTML前200字符:', text.substring(0, 200));
            
            // 检查HTML是否有效
            if (text.includes('<html') || text.includes('<!DOCTYPE')) {
                console.log('✅ HTML格式有效');
            } else {
                console.warn('⚠️ HTML格式可能无效');
            }
        } else {
            console.log('响应类型:', contentType);
            const blob = await response.blob();
            console.log('Blob大小:', blob.size, 'bytes');
            console.log('Blob类型:', blob.type);
        }
    } catch (error) {
        console.error('❌ API请求失败:', error);
    }
    
    // 3. 测试Word预览API
    console.log('\n--- 测试Word预览API ---');
    try {
        const response = await fetch(`/documents/${docId}/preview-docx`);
        console.log('响应状态:', response.status, response.statusText);
        if (response.ok) {
            const blob = await response.blob();
            console.log('Word文档大小:', blob.size, 'bytes', `(${(blob.size / 1024).toFixed(2)} KB)`);
            console.log('Blob类型:', blob.type);
        }
    } catch (error) {
        console.warn('Word预览API错误:', error);
    }
    
    // 4. 检查函数是否存在
    console.log('\n--- 检查函数 ---');
    console.log('loadPreview函数:', typeof loadPreview);
    console.log('loadDocxPreview函数:', typeof loadDocxPreview);
    console.log('showError函数:', typeof showError);
    console.log('logStep函数:', typeof logStep);
    
    // 5. 检查全局变量
    console.log('\n--- 检查全局变量 ---');
    console.log('docId变量:', typeof docId !== 'undefined' ? docId : '未定义');
    console.log('perf对象:', typeof perf !== 'undefined' ? perf : '未定义');
    console.log('pdfjsLib:', typeof pdfjsLib !== 'undefined' ? '已加载' : '未加载');
    console.log('docxPreviewLoaded:', typeof window.docxPreviewLoaded !== 'undefined' ? window.docxPreviewLoaded : '未定义');
    
    // 6. 尝试手动触发加载
    console.log('\n--- 尝试手动触发加载 ---');
    if (typeof loadPreview === 'function') {
        console.log('✅ loadPreview函数存在，尝试手动调用...');
        try {
            await loadPreview();
            console.log('✅ loadPreview执行完成');
        } catch (error) {
            console.error('❌ loadPreview执行失败:', error);
            console.error('错误堆栈:', error.stack);
        }
    } else {
        console.error('❌ loadPreview函数不存在');
    }
    
    console.log('\n========== 诊断完成 ==========');
})();



