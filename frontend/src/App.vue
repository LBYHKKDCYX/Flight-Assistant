<template>
  <div class="container">
    <div class="header">
      <h1><AeroIcon name="plane" :size="36" /> 航空助手</h1>
      <p>ICAO 机场查询 · METAR 气象报文翻译</p>
    </div>

    <div class="grid">
      <IcaoQuery />
      <MetarTranslate />
    </div>

    <div ref="shareCardRef" class="share-card">
      <h3 style="margin:0 0 10px 0;"><AeroIcon name="plane" :size="20" /> 航空助手</h3>
      <div v-html="shareContent" style="font-size: 14px; line-height: 1.6;"></div>
      <div style="margin-top: 15px; font-size: 12px; color: #666;">生成时间: {{ shareTime }}</div>
      <div class="footer">数据基于 mwgg_airports 数据库 &amp; IP2Location 国家代码数据库 | 时区自动转换</div>
    </div>

    <div class="footer">
      <AeroIcon name="bolt" :size="14" /> 数据基于 mwgg_airports 数据库 &amp; IP2Location 国家代码数据库 | 时区自动转换
    </div>

    <ToastContainer />
  </div>
</template>

<script setup>
import { computed } from 'vue'
import IcaoQuery from './components/IcaoQuery.vue'
import MetarTranslate from './components/MetarTranslate.vue'
import ToastContainer from './components/ToastContainer.vue'
import AeroIcon from './components/AeroIcon.vue'
import { useShare } from './composables/useShare.js'

const { shareHtml, shareTime, shareCardRef } = useShare()

const shareContent = computed(() =>
  `<div style="font-size: 14px; line-height: 1.6;">${shareHtml.value}</div>`
)
</script>

<style scoped>
.share-card {
  position: fixed;
  left: -9999px;
  top: 0;
  background: white;
  padding: 20px;
  border-radius: 16px;
  box-shadow: 0 4px 12px rgba(0,0,0,0.1);
  width: 500px;
}
</style>
