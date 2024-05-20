<template>
  <div id="app">
    <div class="user-conf-wrapper">
      <DebugPanel /> <!-- 添加 DebugPanel 组件 -->
      <FakePhone />
    </div>
    <!-- 其他内容可以放在这里，它们将占据右半边的空间 -->
  </div>
</template>

<script>
import FakePhone from './components/FakePhone.vue' // 导入 FakePhone 组件
import DebugPanel from './components/DebugPanel.vue' // 导入 DebugPanel 组件

export default {
  name: 'App',
  components: {
    DebugPanel, // 在 components 对象中添加 DebugPanel
    FakePhone // 在 components 对象中添加 FakePhone
  }
}
</script>

<style>
#app {
  font-family: Avenir, Helvetica, Arial, sans-serif;
  -webkit-font-smoothing: antialiased;
  -moz-osx-font-smoothing: grayscale;
  text-align: center;
  color: #2c3e50;
  margin-top: 60px;
  display: flex; /* 使用 flex 布局 */
  justify-content: center; /* 水平居中 */
  align-items: center; /* 垂直居中 */
}

.user-conf-wrapper {
  display: flex; /* 使用 flex 布局 */
}

</style>