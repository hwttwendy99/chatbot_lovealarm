/**
 * 恋爱铃 - 导航栏组件
 * 提供统一的导航栏界面
 */

// 创建导航栏
function createNavbar() {
    const navbarContainer = document.getElementById('navbarContainer');
    
    if (!navbarContainer) return;
    
    navbarContainer.innerHTML = `
        <nav class="bg-white bg-opacity-80 shadow-md py-4">
            <div class="container mx-auto px-4 flex justify-between items-center">
                <a href="0801chatbot.html" class="text-2xl font-medium text-gray-800">
                    <span class="text-pink-400">恋爱铃</span>
                </a>
                <div class="flex items-center space-x-6" id="navbarUserContainer">
                    <!-- 用户信息将通过JavaScript动态填充 -->
                    <div class="loading"></div>
                </div>
            </div>
        </nav>
    `;
}

// 页面加载时执行
document.addEventListener('DOMContentLoaded', function() {
    createNavbar();
});