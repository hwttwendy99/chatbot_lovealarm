/**
 * 恋爱铃 - 鉴权检查脚本
 * 用于在页面加载时检查用户登录状态
 */

// 检查用户是否已登录
function checkLoginStatus() {
    const isLoggedIn = localStorage.getItem('isLoggedIn');
    const userStr = localStorage.getItem('user');
    
    if (isLoggedIn !== 'true' || !userStr) {
        // 未登录，跳转到登录页面
        window.location.href = 'login.html';
        return false;
    }
    
    try {
        // 解析用户数据
        const user = JSON.parse(userStr);
        
        // 检查用户状态
        if (user.status !== 'active') {
            alert('您的账户已被禁用，请联系管理员');
            localStorage.removeItem('isLoggedIn');
            localStorage.removeItem('user');
            window.location.href = 'login.html';
            return false;
        }
        
        return true;
    } catch (error) {
        console.error('解析用户数据错误:', error);
        localStorage.removeItem('isLoggedIn');
        localStorage.removeItem('user');
        window.location.href = 'login.html';
        return false;
    }
}

// 更新用户界面
function updateUserInterface() {
    const userStr = localStorage.getItem('user');
    
    if (!userStr) return;
    
    try {
        const user = JSON.parse(userStr);
        
        // 更新用户名显示
        const usernameElements = document.querySelectorAll('.user-username');
        usernameElements.forEach(element => {
            element.textContent = user.username;
        });
        
        // 显示管理员入口
        if (user.role === 'admin') {
            const adminElements = document.querySelectorAll('.admin-only');
            adminElements.forEach(element => {
                element.classList.remove('hidden');
            });
        }
        
        // 显示用户登录后的元素
        const loggedInElements = document.querySelectorAll('.logged-in-only');
        loggedInElements.forEach(element => {
            element.classList.remove('hidden');
        });
        
        // 隐藏未登录时的元素
        const loggedOutElements = document.querySelectorAll('.logged-out-only');
        loggedOutElements.forEach(element => {
            element.classList.add('hidden');
        });
    } catch (error) {
        console.error('解析用户数据错误:', error);
    }
}

// 页面加载时执行
document.addEventListener('DOMContentLoaded', function() {
    // 检查当前页面是否需要登录
    const requiresAuth = document.body.hasAttribute('data-requires-auth');
    
    if (requiresAuth) {
        // 需要登录才能访问
        if (!checkLoginStatus()) return;
    }
    
    // 更新用户界面
    updateUserInterface();
});