import streamlit as st
import streamlit_authenticator as stauth
import yaml
from yaml.loader import SafeLoader
import os

# 页面配置
st.set_page_config(
    page_title="基于角色的访问控制系统",
    page_icon="🔒",
    layout="centered",
    initial_sidebar_state="collapsed"
)

# 自定义样式
st.markdown("""
<style>
    /* 隐藏默认的汉堡菜单和页脚 */
    #MainMenu {visibility: hidden;}
    footer {visibility: hidden;}
    
    /* 登录卡片样式 */
    .login-card {
        max-width: 400px;
        padding: 30px;
        margin: 0 auto;
        border-radius: 10px;
        box-shadow: 0 4px 8px rgba(0,0,0,0.1);
        background-color: #ffffff;
    }
    
    /* 角色标签样式 */
    .role-tag {
        display: inline-block;
        padding: 2px 10px;
        border-radius: 15px;
        font-size: 0.8em;
        font-weight: bold;
        margin-left: 10px;
    }
    
    .admin { background-color: #ff4b4b; color: white; }
    .editor { background-color: #4b8df8; color: white; }
    .viewer { background-color: #00c292; color: white; }
    
    /* 按钮样式 */
    .stButton>button {
        width: 100%;
        background-color: #4b8df8;
        color: white;
    }
    
    /* 页面标题 */
    .page-title {
        text-align: center;
        margin-bottom: 30px;
    }
</style>
""", unsafe_allow_html=True)

# 用户配置文件路径
USER_CONFIG_PATH = "config.yaml"

# 初始化用户配置文件
def init_user_config():
    """创建默认用户配置文件"""
    if not os.path.exists(USER_CONFIG_PATH):
        default_config = {
            'credentials': {
                'usernames': {
                    'admin': {
                        'email': 'admin@example.com',
                        'name': '系统管理员',
                        'password': stauth.Hasher.hash('admin123'),
                        'role': 'admin'
                    },
                    'editor': {
                        'email': 'editor@example.com',
                        'name': '内容编辑',
                        'password': stauth.Hasher.hash('editor123'),
                        'role': 'editor'
                    },
                    'viewer': {
                        'email': 'viewer@example.com',
                        'name': '数据查看',
                        'password': stauth.Hasher.hash('viewer123'),
                        'role': 'viewer'
                    }
                }
            },
            'cookie': {
                'expiry_days': 30,
                'key': 'role_based_auth',
                'name': 'role_auth_cookie'
            }

        }
        
        with open(USER_CONFIG_PATH, 'w') as file:
            yaml.dump(default_config, file, default_flow_style=False)

# 加载用户配置
def load_user_config():
    """加载用户配置文件"""
    with open(USER_CONFIG_PATH) as file:
        return yaml.load(file, Loader=SafeLoader)

# 角色页面内容
def admin_page():
    """管理员页面"""
    st.title("🔐 管理员控制面板")
    st.subheader(f"欢迎, {st.session_state['name']}!")
    st.markdown(f'<div class="role-tag admin">管理员</div>', unsafe_allow_html=True)
    
    st.divider()
    st.header("系统管理功能")
    col1, col2, col3 = st.columns(3)
    with col1:
        st.info("用户管理")
        st.write("管理所有系统用户账户")
    with col2:
        st.info("权限设置")
        st.write("配置角色和访问权限")
    with col3:
        st.info("系统监控")
        st.write("监控系统运行状态")
    
    st.divider()
    st.header("用户列表")
    config = load_user_config()
    users = config['credentials']['usernames']
    
    for username, user_data in users.items():
        with st.expander(f"{user_data['name']} ({username})"):
            col1, col2 = st.columns([1, 3])
            with col1:
                st.text_input("邮箱", user_data['email'], key=f"email_{username}", disabled=True)
            with col2:
                role = st.selectbox(
                    "角色", 
                    ['admin', 'editor', 'viewer'], 
                    index=['admin', 'editor', 'viewer'].index(user_data['role']),
                    key=f"role_{username}"
                )
                
                # 保存更改
                if st.button("更新", key=f"btn_{username}"):
                    users[username]['role'] = role
                    with open(USER_CONFIG_PATH, 'w') as file:
                        yaml.dump(config, file, default_flow_style=False)
                    st.success("用户信息已更新!")

def editor_page():
    """编辑页面"""
    st.title("📝 内容编辑中心")
    st.subheader(f"欢迎, {st.session_state['name']}!")
    st.markdown(f'<div class="role-tag editor">编辑</div>', unsafe_allow_html=True)
    
    st.divider()
    st.header("内容创作")
    title = st.text_input("文章标题")
    content = st.text_area("文章内容", height=300)
    
    col1, col2 = st.columns(2)
    with col1:
        category = st.selectbox("分类", ["技术", "新闻", "教程", "观点"])
    with col2:
        tags = st.multiselect("标签", ["Python", "Streamlit", "AI", "数据分析", "可视化"])
    
    if st.button("发布文章"):
        st.success("文章已成功发布!")
    
    st.divider()
    st.header("内容管理")
    st.dataframe([
        {"标题": "Streamlit入门指南", "分类": "教程", "状态": "已发布", "阅读量": 1240},
        {"标题": "使用Python进行数据分析", "分类": "技术", "状态": "草稿", "阅读量": 0},
        {"标题": "2023年AI趋势预测", "分类": "观点", "状态": "已发布", "阅读量": 3560}
    ])

def viewer_page():
    """查看者页面"""
    st.title("📊 数据分析中心")
    st.subheader(f"欢迎, {st.session_state['name']}!")
    st.markdown(f'<div class="role-tag viewer">查看者</div>', unsafe_allow_html=True)
    
    st.divider()
    st.header("数据仪表盘")
    
    col1, col2, col3 = st.columns(3)
    with col1:
        st.metric("总用户数", "1,248", "+24 (1.9%)")
    with col2:
        st.metric("活跃用户", "842", "-12 (1.4%)")
    with col3:
        st.metric("平均停留时间", "4分32秒", "+0:32")
    
    st.divider()
    st.header("用户行为分析")
    tab1, tab2, tab3 = st.tabs(["时间分布", "地域分布", "设备分析"])
    
    with tab1:
        st.subheader("用户活跃时间分布")
        st.bar_chart({
            "00-03": 120,
            "03-06": 85,
            "06-09": 320,
            "09-12": 680,
            "12-15": 720,
            "15-18": 650,
            "18-21": 890,
            "21-24": 640
        })
    
    with tab2:
        st.subheader("用户地域分布")
        st.map(pd.DataFrame({
            "lat": [37.76, 34.05, 40.71, 31.23, 39.90, 22.54],
            "lon": [-122.4, -118.24, -74.00, 121.47, 116.40, 114.05],
            "name": ["旧金山", "洛杉矶", "纽约", "上海", "北京", "香港"],
            "value": [120, 98, 150, 210, 180, 95]
        }), zoom=1)
    
    with tab3:
        st.subheader("设备使用情况")
        st.write("移动设备: 68%")
        st.progress(0.68)
        st.write("桌面设备: 28%")
        st.progress(0.28)
        st.write("平板设备: 4%")
        st.progress(0.04)

# 初始化用户配置
init_user_config()

# 主应用逻辑
def main():
    """主应用函数"""
    
    # 检查用户是否已登录
    if 'authentication_status' not in st.session_state:
        st.session_state.authentication_status = None
    
    # 加载用户配置
    config = load_user_config()
    
    # 创建认证对象
    authenticator = stauth.Authenticate(
        config['credentials'],
        config['cookie']['name'],
        config['cookie']['key'],
        config['cookie']['expiry_days']
        # config['preauthorized']
    )
    
    # 显示登录界面（如果未登录）
    if not st.session_state.get("authentication_status"):
        # 登录卡片容器
        with st.container():
            st.markdown("<div class='login-card'>", unsafe_allow_html=True)
            
            st.markdown("<h1 class='page-title'>角色访问控制系统</h1>", unsafe_allow_html=True)
            st.markdown("<p style='text-align:center'>请使用您的账户登录系统</p>", unsafe_allow_html=True)
            
            # 登录表单
            authenticator.login()
            name =  st.session_state.get('name')
            authentication_status =st.session_state.get('authentication_status')
            username = st.session_state.get('username')
            if authentication_status is False:
                st.error("用户名或密码不正确")
            elif authentication_status is None:
                st.warning("请输入您的用户名和密码")
            
            # 注册新用户（仅管理员可见）
            if authentication_status:
                if username == 'admin':
                    st.divider()
                    st.subheader("注册新用户")
                    
                    with st.form("register_form"):
                        new_username = st.text_input("用户名")
                        new_name = st.text_input("姓名")
                        new_email = st.text_input("邮箱")
                        new_password = st.text_input("密码", type="password")
                        new_role = st.selectbox("角色", ["admin", "editor", "viewer"])
                        
                        submitted = st.form_submit_button("注册")
                        if submitted:
                            if new_username in config['credentials']['usernames']:
                                st.error("用户名已存在")
                            else:
                                # 添加新用户
                                config['credentials']['usernames'][new_username] = {
                                    'email': new_email,
                                    'name': new_name,
                                    'password': stauth.Hasher([new_password]).generate()[0],
                                    'role': new_role
                                }
                                
                                # 保存配置
                                with open(USER_CONFIG_PATH, 'w') as file:
                                    yaml.dump(config, file, default_flow_style=False)
                                
                                st.success("用户注册成功!")
            
            st.markdown("</div>", unsafe_allow_html=True)
    
    # 处理登录后的页面跳转
    if st.session_state.get("authentication_status"):
        # 从会话状态获取用户信息
        username = st.session_state["username"]
        
        # 获取用户角色
        user_role = config['credentials']['usernames'][username]['role']
        
        # 登出按钮
        authenticator.logout('退出登录', 'sidebar')
        
        # 根据角色跳转到不同页面
        if user_role == 'admin':
            admin_page()
        elif user_role == 'editor':
            editor_page()
        elif user_role == 'viewer':
            viewer_page()
        
        # 在侧边栏显示用户信息
        with st.sidebar:
            st.subheader("用户信息")
            st.write(f"用户名: {username}")
            st.write(f"姓名: {st.session_state['name']}")
            st.write(f"邮箱: {config['credentials']['usernames'][username]['email']}")
            st.markdown(f"角色: <span class='role-tag {user_role}'>{user_role}</span>", unsafe_allow_html=True)
            
            # 用户管理（仅管理员）
            if user_role == 'admin':
                st.divider()
                st.subheader("系统管理")
                if st.button("刷新用户配置"):
                    st.session_state.clear()
                    st.rerun()
    
    # 显示登录状态
    st.sidebar.write(f"登录状态: {'已登录' if st.session_state.get('authentication_status') else '未登录'}")

# 运行主应用
if __name__ == '__main__':
    # 为了演示目的，导入pandas（实际viewer_page中需要）
    import pandas as pd
    main()