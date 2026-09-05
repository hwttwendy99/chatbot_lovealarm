/**
 * 恋爱铃 - 用户鉴权模块
 * 提供用户登录状态检查、权限控制等功能
 */

// 检查用户是否已登录
function checkLogin() {
    const isLoggedIn = localStorage.getItem('isLoggedIn');
    const userStr = localStorage.getItem('user');
    
    if (isLoggedIn !== 'true' || !userStr) {
        // 未登录，跳转到登录页面
        window.location.href = 'login.html';
        return false;
    }
    
    return true;
}

// 检查用户是否为管理员
function checkAdmin() {
    const isLoggedIn = localStorage.getItem('isLoggedIn');
    const userStr = localStorage.getItem('user');
    
    if (isLoggedIn !== 'true' || !userStr) {
        // 未登录，跳转到登录页面
        window.location.href = 'login.html';
        return false;
    }
    
    try {
        const user = JSON.parse(userStr);
        if (user.role !== 'admin') {
            // 不是管理员，跳转到主页
            alert('您没有管理员权限');
            window.location.href = '0801chatbot.html';
            return false;
        }
        
        return true;
    } catch (error) {
        console.error('解析用户数据错误:', error);
        window.location.href = 'login.html';
        return false;
    }
}

// 获取当前登录用户信息
function getCurrentUser() {
    const userStr = localStorage.getItem('user');
    
    if (!userStr) {
        return null;
    }
    
    try {
        return JSON.parse(userStr);
    } catch (error) {
        console.error('解析用户数据错误:', error);
        return null;
    }
}

// 退出登录
function logout() {
    localStorage.removeItem('isLoggedIn');
    localStorage.removeItem('user');
    window.location.href = 'login.html';
}

// 更新导航栏用户信息
function updateNavbar() {
    const user = getCurrentUser();
    const navbarUserContainer = document.getElementById('navbarUserContainer');
    
    if (!navbarUserContainer) return;
    
    if (user) {
        // 已登录状态
        const isAdmin = user.role === 'admin';
        
        navbarUserContainer.innerHTML = `
            <span class="text-sm mr-2">欢迎，${user.username}</span>
            ${isAdmin ? '<a href="admin.html" class="nav-link mr-4"><i class="fas fa-cog mr-1"></i> 管理控制台</a>' : ''}
            <a href="profile.html" class="nav-link mr-4"><i class="fas fa-user mr-1"></i> 个人信息</a>
            <button id="logoutBtn" class="nav-link"><i class="fas fa-sign-out-alt mr-1"></i> 退出登录</button>
        `;
        
        // 添加退出登录按钮事件
        document.getElementById('logoutBtn').addEventListener('click', logout);
    } else {
        // 未登录状态
        navbarUserContainer.innerHTML = `
            <a href="login.html" class="nav-link mr-4"><i class="fas fa-sign-in-alt mr-1"></i> 登录</a>
            <a href="register.html" class="nav-link"><i class="fas fa-user-plus mr-1"></i> 注册</a>
        `;
    }
}

// 页面加载时执行
document.addEventListener('DOMContentLoaded', function() {
    // 检查当前页面是否需要登录
    const requiresAuth = document.body.hasAttribute('data-requires-auth');
    const requiresAdmin = document.body.hasAttribute('data-requires-admin');
    
    if (requiresAdmin) {
        // 需要管理员权限
        if (!checkAdmin()) return;
    } else if (requiresAuth) {
        // 需要登录
        if (!checkLogin()) return;
    }
    
    // 更新导航栏
    updateNavbar();
});