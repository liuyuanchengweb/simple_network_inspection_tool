# Vue 3 + Vite Project Template

#### **框架**

- vue 3
- vuex
- vue-router



#### UI **组件库**

- element-plus



#### **第三方库**

- less
- mock.js
- vite-plugin-mock
- vite-plugin-compression



#### 初始化

**拉取模板**

```bash
git clone https://gitee.com/yxsw/Vue3_Vite_Project_Template.git
```

**安装依赖**

```bash
npm install
```

**运行项目**

```bash
npm statr
```

**构建项目**

```bash
npm run build
```



#### **vite** 配置

**项目配置**

**viteMockServe**

```js
viteMockServe({
    mockPath: "./mock", // 解析，路径可根据实际变动
    localEnabled: false, // 开发环境
    prodEnabled: true, // 生产环境设为true，也可以根据官方文档格式
    injectCode: 
    ` import { setupProdMockServer } from './src/mock';
    setupProdMockServer(); `,
    watchFiles: true, // 监听文件内容变更
    injectFile: resolve("src/main.ts"), 
    // 在main.ts注册后需要在此处注入，否则可能报找不到setupProdMockServer的错误
})
```

 **打包配置** **viteCompression**

- filter：过滤器，对哪些类型的文件进行压缩，默认为 ‘/.(js|mjs|json|css|html)$/i’
- verbose: true：是否在控制台输出压缩结果，默认为 true
- threshold：启用压缩的文件大小限制，单位是字节，默认为 0
- disable: false：是否禁用压缩，默认为 false
- deleteOriginFile：压缩后是否删除原文件，默认为 false
- algorithm：采用的压缩算法，默认是 gzip
- ext：生成的压缩包后缀



**server** **开发配置**

```js
  server: {
    port: 1212,
    open: false,
    host: '0.0.0.0',
    // https: {
    //   // 主要是下面两行的配置文件，不要忘记引入 fs 和 path 两个对象
    //   cert: fs.readFileSync(path.join(__dirname, './cert.crt')),
    //   key: fs.readFileSync(path.join(__dirname, './cert.key')),
    // },
    proxy: {
      '/api': {
        secure: false,
        changeOrigin: true,
        target: 'https://192.168.0.102',
        rewrite: (path) => path.replace(/^\/api/, ''),
      },
    },
  },
```



#### Docker

**创建镜像**

```bash
docker image build . -t vue3_temp
```

**运行容器**

-- name 容器取别名

-d 后台运行

80:80 将容器80端口映射到主机80端口 *主机端口:容器端口*

```bash
docker run --name vue3temp -d -p 80:80 vue3_temp
```

