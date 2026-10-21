# 🗺️ study-map

用**数据结构**管理你的学习数据。
学一个数据结构，就给自己的系统升一级。

---

## 🚀 快速开始

```bash
# 查看全部课程概览
python3 study_map.py

# 查看所有待办任务（按截止时间排序）
python3 study_map.py --todo

# 按优先级排序
python3 study_map.py --priority

# 查看某门课详情
python3 study_map.py --course probability
```

---

## 📈 升级路线图

| 版本 | 数据结构 | 对应能力 | 状态 |
|------|---------|---------|------|
| v0.1 | 列表 (list) + 字典 (dict) | 课程清单 + 课程档案 | ✅ 当前版本 |
| v0.2 | 哈希表 (dict 进阶) | 快速查课、按标签分类 | 🔜 下一步 |
| v0.3 | 图 (graph) | 任务依赖、拓扑排序 | 待开发 |
| v0.4 | 堆 (heap) / 优先队列 | 智能优先级调度 | 待开发 |

---

## 🐙 GitHub 新手入门教程

### 第一步：注册账号

1. 打开 https://github.com
2. 用邮箱注册一个账号（用户名想好，以后会一直用）
3. 验证邮箱

### 第二步：安装 Git

**Windows：**
- 去 https://git-scm.com/download/win 下载安装包
- 一路默认下一步就行
- 安装完后，开始菜单里找到 "Git Bash"，打开它

**Mac：**
- 打开终端，输入 `git --version`
- 如果没装，会提示你安装，跟着走就行

### 第三步：配置 Git（只需要做一次）

打开 Git Bash（Windows）或终端（Mac），输入：

```bash
git config --global user.name "你的GitHub用户名"
git config --global user.email "你的GitHub邮箱"
```

验证一下：
```bash
git config --global user.name
git config --global user.email
```
能看到你刚填的就对了。

### 第四步：在 GitHub 上创建仓库

1. 登录 GitHub，点右上角 **+** → **New repository**
2. Repository name 填 `study-map`
3. 选 **Public**（公开，别人能看到）或 **Private**（只有你能看到）
4. **不要勾选** "Add a README file"（我们已经有了）
5. 点 **Create repository**

创建完后，你会看到一个 Quick setup 页面，先放着别动。

### 第五步：把本地代码推上去

打开 Git Bash / 终端，进入到 study-map 文件夹：

```bash
# 进入文件夹（路径换成你自己的）
cd 你的路径/study-map

# 初始化 git 仓库
git init

# 把所有文件加入暂存区
git add .

# 提交（"first commit" 可以改成你想说的话）
git commit -m "first commit: v0.1 课程清单 + 待办"

# 关联远程仓库（下面的 URL 换成你 GitHub 上显示的那个）
git remote add origin https://github.com/你的用户名/study-map.git

# 推送到 GitHub
git push -u origin main
```

刷新你的 GitHub 页面——代码已经上去了！🎉

### 第六步：以后怎么更新代码（日常流程）

每次写完新东西，三步走：

```bash
git add .                    # 把改动加进去
git commit -m "做了什么改动"  # 提交，写清楚改了啥
git push                     # 推到 GitHub
```

就这么简单。三个命令，每天用你就会了。

### 常用命令速查

| 命令 | 作用 |
|------|------|
| `git status` | 查看当前状态（改了哪些文件） |
| `git log` | 查看提交历史 |
| `git diff` | 看具体改了什么 |
| `git clone <地址>` | 把别人的仓库下载到本地 |
| `git pull` | 把远程的最新代码拉下来 |

### 常见问题

**Q：push 的时候要输密码？**
A：现在 GitHub 不支持密码了，要用 "Personal Access Token"。
   设置路径：Settings → Developer settings → Personal access tokens → Tokens (classic) → Generate new token
   勾选 repo 权限，生成后复制，当密码用。

**Q：我改乱了，想回到上一个版本？**
A：`git log` 找到 commit 的哈希值（一长串字母数字），然后 `git checkout 那个哈希值` 就能回去看。

---

## 📁 文件结构

```
study-map/
├── study_map.py        # 主程序
├── data/
│   └── courses.json    # 课程数据
└── README.md           # 你正在看的这个文件
```

---

## 💡 设计理念

- **学的就是用的**：每学一个数据结构，就给自己的系统加一个功能
- **心里有数 > 资料越多越好**：系统是帮你看清全局的，不是堆资料的
- **从简单开始，逐步升级**：v0.1 能跑就行，后面慢慢加
