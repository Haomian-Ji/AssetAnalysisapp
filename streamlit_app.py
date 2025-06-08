import streamlit as st
import streamlit_authenticator as stauth

import yaml
from yaml.loader import SafeLoader
from streamlit_authenticator.utilities import *
import base64

# 连接数据库
# conn = st.connection("snowflake")
# df = conn.query("SELECT * FROM mytable;", ttl="10m")

# for row in df.itertuples():
#     st.write(f"{row.NAME} has a :{row.PET}:")

# 页面配置
st.set_page_config(
    page_title="韦德合伙人后台登录",
    # page_icon="🔒",
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
    .user { background-color: #00c292; color: white; }
    
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

# 将图片转换为base64
def get_image_base64(path):
    with open(path, "rb") as img_file:
        return base64.b64encode(img_file.read()).decode('utf-8')

# 获取base64图片数据（替换为你的图片路径）
img_path = "logo_app.png"  # 👈 修改为你的图片路径
img_base64 = get_image_base64(img_path)

# 用户配置文件路径
USER_CONFIG_PATH = "data/config.yaml"

    
# 打开用户文件
with open(USER_CONFIG_PATH) as file:
    config = yaml.load(file, Loader=SafeLoader)


def main():
    """主应用函数"""
    
    # 检查用户是否已登录
    if 'authentication_status' not in st.session_state:
        st.session_state.authentication_status = None

        # 创建认证对象
    authenticator = stauth.Authenticate(
        config['credentials'],
        config['cookie']['name'],
        config['cookie']['key'],
        config['cookie']['expiry_days'],
    )

    st.session_state.authenticator = authenticator
    st.session_state.config= config

    # 显示登录界面（如果未登录）
    if not st.session_state.get("authentication_status"):
        # 登录卡片容器
        with st.container():
            st.markdown(
                f"""
                <div class='login-card'>
                    <img src="data:image/png;base64,{img_base64}" alt="Your Image" style="width:100%">
                </div>
                """,
                unsafe_allow_html=True
            )
            
            st.markdown("<h1 class='page-title'>韦德合伙人后台登录</h1>", unsafe_allow_html=True)
            st.markdown("<p style='text-align:center'>请使用您的账户登录系统</p>", unsafe_allow_html=True)
            
            # 登录表单
            # name, authentication_status, username = authenticator.login(key='登录', location='main')
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
                        new_role = st.selectbox("角色", ["admin", "user"])
                        
                        submitted = st.form_submit_button("注册")
                        if submitted:
                            if new_username in config['credentials']['usernames']:
                                st.error("用户名已存在")
                            else:
                                # 添加新用户
                                config['credentials']['usernames'][new_username] = {
                                    'email': new_email,
                                    'name': new_name,
                                    'password': stauth.Hasher.hash([new_password]),
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
        user_role = config['credentials']['usernames'][username]['roles'][0]
        
        # 登出按钮
        authenticator.logout('退出登录', 'sidebar')
        
        # 根据不同的角色配置页面
        # logout_page = st.Page(logout, title="登出", icon=":material/logout:")
        analysis_page = st.Page("assetanalysis.py",title="资产分析")
        fundingdetails_page = st.Page("fundingdetails.py", title="资金详情")
        # settings_page = st.Page("settings.py", title="设置", icon= ":material/settings:")


        moneymanagement_page = st.Page("moneymanagement.py", title="资金管理", icon=":material/settings:")
        createuser_page = st.Page("createuser.py", title="创建用户", icon=":material/settings:")


        # accout_pages = [logout_page, settings_page]
        user_pages = [analysis_page,fundingdetails_page]
        admin_pages = [moneymanagement_page, createuser_page]

        # page_dict = {}
        # if st.session_state.role == "用户":
        #     page_dict["User"] = user_pages
        # elif st.session_state.role == "管理员":
        #     page_dict["Admin"] = admin_pages

        # if len(page_dict) > 0:
        #     pg = st.navigation(page_dict|{"Account": accout_pages} )
        # else:
        #     pg = st.navigation([st.Page(login)])

        # pg.run()




        
        # 在侧边栏显示用户信息
        with st.sidebar:
            st.subheader("用户信息")
            st.write(f"用户名: {username}")
            st.write(f"姓名: {st.session_state['name']}")
            st.write(f"邮箱: {config['credentials']['usernames'][username]['email']}")
            st.markdown(f"角色: <span class='role-tag {user_role}'>{user_role}</span>", unsafe_allow_html=True)
            
            # # 用户管理（仅管理员）
            # if user_role == 'admin':
            #     st.divider()
            #     st.subheader("系统管理")
            #     if st.button("刷新用户配置"):
            #         st.session_state.clear()
            #         st.rerun()
        
        page_dict = {}
        page_dict["用户"] = user_pages
        pg =st.navigation(page_dict)
        # 根据角色跳转到不同页面
        if user_role == 'admin':
            pg = st.navigation(page_dict|{"管理": admin_pages} )
        pg.run()
    # 显示登录状态
    st.sidebar.write(f"登录状态: {'已登录' if st.session_state.get('authentication_status') else '未登录'}")
# 运行主应用
if __name__ == '__main__':
    main()





        





