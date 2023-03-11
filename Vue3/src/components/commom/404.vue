<template>
  <div class="exception-page">
    <div class="img">
      <img :src="config.img" />
    </div>
    <div class="content">
      <h1>{{ config.title }}</h1>
      <div class="desc">{{ config.desc }}</div>
      <div class="action">
        <el-button type="primary" @click="backHome">返回首页</el-button>
      </div>
    </div>
  </div>
</template>

<script setup>
  import { ref } from '@vue/reactivity'
  import { useRouter } from 'vue-router'

  let router = useRouter()
  let config = ref({
    img: 'https://gw.alipayobjects.com/zos/rmsportal/KpnpchXsobRgLElEozzI.svg',
    title: '404',
    desc: '抱歉，你访问的页面不存在或仍在开发中',
  })

  function backHome() {
    router.push({ name: 'index' })
  }
</script>

<style lang="less" scoped>
.exception-page {
  height: 100%;
  border-radius: 4px;
  display: flex;
  justify-content: center;
  align-items: center;
  background-color: #ecf5ff;
  .img {
    padding-right: 52px;
    zoom: 1;
    img {
      max-width: 430px;
    }
  }
  .content {
    h1 {
      color: #434e59;
      font-size: 72px;
      font-weight: 600;
      line-height: 72px;
      margin-bottom: 24px;
    }
    .desc {
      font-size: 20px;
      line-height: 28px;
      margin-bottom: 16px;
    }
  }
}
</style>
