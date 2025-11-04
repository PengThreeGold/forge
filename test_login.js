// 测试登录功能的脚本
// 在浏览器控制台中运行此脚本以测试登录功能

async function testLogin() {
  try {
    console.log('开始测试登录功能...');
    
    // 1. 测试初始化管理员
    console.log('1. 测试初始化管理员账户...');
    const initResponse = await fetch('/api/auth/init-admin', {
      method: 'POST',
      headers: {
        'Content-Type': 'application/json',
      },
      body: JSON.stringify({
        username: 'admin',
        password: 'admin123',
        email: 'admin@example.com'
      })
    });
    
    if (initResponse.ok) {
      const initData = await initResponse.json();
      console.log('管理员账户初始化成功:', initData);
    } else {
      const initError = await initResponse.json();
      console.log('管理员账户初始化失败:', initError);
    }
    
    // 2. 测试登录
    console.log('2. 测试登录功能...');
    const loginResponse = await fetch('/api/auth/login', {
      method: 'POST',
      headers: {
        'Content-Type': 'application/json',
      },
      body: JSON.stringify({
        username: 'admin',
        password: 'admin123'
      })
    });
    
    if (loginResponse.ok) {
      const loginData = await loginResponse.json();
      console.log('登录成功:', loginData);
      
      // 保存token以便后续测试
      if (loginData.success && loginData.data && loginData.data.access_token) {
        localStorage.setItem('token', loginData.data.access_token);
        console.log('Token已保存到localStorage');
        
        // 3. 测试获取用户信息
        console.log('3. 测试获取用户信息...');
        const profileResponse = await fetch('/api/auth/profile', {
          method: 'GET',
          headers: {
            'Authorization': `Bearer ${loginData.data.access_token}`,
            'Content-Type': 'application/json',
          }
        });
        
        if (profileResponse.ok) {
          const profileData = await profileResponse.json();
          console.log('获取用户信息成功:', profileData);
        } else {
          const profileError = await profileResponse.json();
          console.log('获取用户信息失败:', profileError);
        }
      }
    } else {
      const loginError = await loginResponse.json();
      console.log('登录失败:', loginError);
    }
  } catch (error) {
    console.error('测试过程中发生错误:', error);
  }
}

// 执行测试
testLogin();