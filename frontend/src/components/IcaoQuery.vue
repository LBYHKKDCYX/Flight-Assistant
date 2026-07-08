<template>
  <div class="card">
    <div class="card-header">
      <h2><i><AeroIcon name="takeoff" :size="42" /></i> ICAO 代码查询</h2>
    </div>
    <div class="card-body">
      <div class="input-group">
        <label>机场 ICAO 代码（4字母）</label>
        <div class="input-wrap input-suggest-wrap">
          <div class="btn-row">
            <button class="btn btn-sm" @click="copyInput"><AeroIcon name="clipboard" :size="14" /> 复制</button>
          </div>
          <input
            v-model="icaoInput"
            type="text"
            placeholder="例如: ZBAA, KJFK, EGLL"
            maxlength="4"
            autocomplete="off"
            @input="onInput"
            @keydown="onKeydown"
            @focus="onFocus"
            @blur="onBlur"
          >
          <ul class="suggest-dropdown" v-if="showSuggestions && suggestions.length">
            <li
              v-for="(s, idx) in suggestions"
              :key="s.icao"
              :class="{ active: idx === activeIdx }"
              @mousedown.prevent="selectSuggestion(s)"
            >
              <span class="s-icao">{{ s.icao }}</span>
              <span class="s-body">
                <span class="s-name">{{ s.name }}</span>
                <span class="s-iata" v-if="s.iata">{{ s.iata }}</span>
              </span>
              <span class="s-loc">{{ s.city }}{{ s.country ? ', ' + s.country : '' }}</span>
            </li>
          </ul>
        </div>
        <div class="history-row" v-if="historyList.length && !showSuggestions">
          <span class="history-hint">最近查询：</span>
          <button
            v-for="h in historyList"
            :key="h"
            class="history-btn"
            @click="selectHistory(h)"
          >{{ h }}</button>
        </div>
      </div>

      <button class="btn" @click="query"><AeroIcon name="search" :size="16" /> 查询机场信息</button>

      <div class="result-wrap">
        <div class="btn-row">
          <button class="btn btn-sm" @click="copyResult"><AeroIcon name="clipboard" :size="14" /> 复制</button>
          <button class="btn btn-sm" @click="shareResult"><AeroIcon name="camera" :size="14" /> 分享</button>
        </div>
        <div :class="resultClass" v-html="resultHtml"></div>
      </div>
    </div>
  </div>
</template>

<script setup>
import { ref, computed } from 'vue'
import { useToast } from '../composables/useToast.js'
import { useHistory } from '../composables/useHistory.js'
import { useShare } from '../composables/useShare.js'
import AeroIcon from './AeroIcon.vue'

const { showToast } = useToast()
const { historyList, addToHistory } = useHistory()
const { shareAsImage } = useShare()

const icaoInput = ref('')
const resultText = ref('等待输入…')
const loading = ref(false)
const error = ref(false)

// 联想相关状态
const suggestions = ref([])
const showSuggestions = ref(false)
const activeIdx = ref(-1)
let debounceTimer = null

const resultHtml = computed(() => {
  if (loading.value) return '<div class="spinner"></div> 加载中...'
  return resultText.value.replace(/\n/g, '<br>')
})

const resultClass = computed(() => ({
  'result-box': true,
  'loading': loading.value,
  'error': error.value
}))

async function fetchSuggestions(query) {
  if (!query || query.length < 1) {
    suggestions.value = []
    showSuggestions.value = false
    return
  }
  try {
    const res = await fetch(`/api_web/suggest?q=${encodeURIComponent(query)}`)
    const data = await res.json()
    suggestions.value = data.suggestions || []
    activeIdx.value = -1
    showSuggestions.value = suggestions.value.length > 0
  } catch {
    suggestions.value = []
    showSuggestions.value = false
  }
}

function onInput() {
  clearTimeout(debounceTimer)
  debounceTimer = setTimeout(() => {
    fetchSuggestions(icaoInput.value.trim())
  }, 200)
}

function onFocus() {
  if (icaoInput.value.trim() && suggestions.value.length) {
    showSuggestions.value = true
  }
}

function onBlur() {
  // 延迟关闭，让 mousedown 先触发
  setTimeout(() => {
    showSuggestions.value = false
  }, 150)
}

function onKeydown(e) {
  if (!showSuggestions.value || !suggestions.value.length) {
    if (e.key === 'Enter') {
      e.preventDefault()
      query()
    }
    return
  }

  switch (e.key) {
    case 'ArrowDown':
      e.preventDefault()
      activeIdx.value = (activeIdx.value + 1) % suggestions.value.length
      break
    case 'ArrowUp':
      e.preventDefault()
      activeIdx.value = activeIdx.value <= 0
        ? suggestions.value.length - 1
        : activeIdx.value - 1
      break
    case 'Enter':
      e.preventDefault()
      if (activeIdx.value >= 0) {
        selectSuggestion(suggestions.value[activeIdx.value])
      } else {
        showSuggestions.value = false
        query()
      }
      break
    case 'Escape':
      showSuggestions.value = false
      break
  }
}

function selectSuggestion(s) {
  icaoInput.value = s.icao
  showSuggestions.value = false
  query()
}

async function query() {
  const icao = icaoInput.value.trim().toUpperCase()
  if (!icao) {
    error.value = true
    resultText.value = '⚠️ 请输入 ICAO 代码 (例如 ZBAA)'
    return
  }
  if (!/^[A-Z]{4}$/.test(icao)) {
    error.value = true
    resultText.value = '❌ ICAO 代码应为 4 个大写字母 (A-Z)'
    return
  }

  loading.value = true
  error.value = false
  try {
    const res = await fetch('/api_web/icao', {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({ icao })
    })
    const data = await res.json()
    if (data.error) {
      error.value = true
      resultText.value = `❌ ${data.error}`
    } else {
      resultText.value = data.result
      addToHistory(icao)
    }
  } catch (err) {
    error.value = true
    resultText.value = `⚠️ 网络错误: ${err.message}\n请确保后端服务已启动 (Flask)`
  } finally {
    loading.value = false
  }
}

function selectHistory(icao) {
  icaoInput.value = icao
  query()
}

function copyInput() {
  if (!icaoInput.value.trim()) {
    showToast('输入框为空，无内容可复制', 'warning')
    return
  }
  navigator.clipboard.writeText(icaoInput.value).then(() => {
    showToast('✅ ICAO 代码已复制', 'success')
  }).catch(() => {
    showToast('❌ 复制失败，请手动复制', 'error')
  })
}

function copyResult() {
  if (resultText.value === '等待输入…') {
    showToast('暂无内容可复制', 'warning')
    return
  }
  navigator.clipboard.writeText(resultText.value).then(() => {
    showToast('✅ 结果已复制到剪贴板', 'success')
  }).catch(() => {
    showToast('❌ 复制失败，请手动复制', 'error')
  })
}

async function shareResult() {
  if (resultText.value === '等待输入…') {
    showToast('暂无内容可分享', 'warning')
    return
  }
  const r = await shareAsImage(resultText.value, 'ICAO')
  if (r === 'success') showToast('✅ 图片已复制到剪贴板', 'success')
  else if (r === 'download') showToast('⚠️ 您的浏览器不支持直接复制图片，已为您下载图片', 'warning')
  else showToast('❌ 复制失败，请尝试手动截图', 'error')
}
</script>
