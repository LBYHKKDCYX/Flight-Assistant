<template>
  <div class="card">
    <div class="card-header">
      <h2><i><AeroIcon name="weather" :size="42" /></i> METAR 报文翻译</h2>
    </div>
    <div class="card-body">
      <div class="input-group">
        <label>手动输入 METAR 报文（若使用获取实时报文，则此处是查询到的原始报文）</label>
        <div class="input-wrap">
          <div class="btn-row">
            <button class="btn btn-sm" @click="copyMetarInput"><AeroIcon name="clipboard" :size="14" /> 复制</button>
          </div>
          <textarea
            v-model="metarInput"
            placeholder="示例: ZSSS 251200Z 12005KT 9999 FEW020 18/12 Q1018 NOSIG"
            @keydown.ctrl.enter.prevent="translate"
            @keydown.meta.enter.prevent="translate"
          ></textarea>
        </div>
      </div>

      <div class="input-group fetch-row">
        <label>或通过 ICAO 获取实时报文</label>
        <div class="fetch-bar">
          <div class="fetch-input-wrap input-suggest-wrap">
            <div class="btn-row">
              <button class="btn btn-sm" @click="copyFetchIcao"><AeroIcon name="clipboard" :size="14" /> 复制</button>
            </div>
            <input
              v-model="fetchIcao"
              type="text"
              placeholder="ICAO 代码"
              maxlength="4"
              autocomplete="off"
              @input="onFetchInput"
              @keydown="onFetchKeydown"
              @focus="onFetchFocus"
              @blur="onFetchBlur"
            >
            <ul class="suggest-dropdown" v-if="showFetchSuggest && fetchSuggestions.length">
              <li
                v-for="(s, idx) in fetchSuggestions"
                :key="s.icao"
                :class="{ active: idx === fetchActiveIdx }"
                @mousedown.prevent="selectFetchSuggestion(s)"
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
          <button class="btn" @click="fetchMetar"><AeroIcon name="cloud-download" :size="20" /> 获取实时报文</button>
        </div>
        <div class="history-row" v-if="historyList.length && !showFetchSuggest">
          <span class="history-hint">最近查询：</span>
          <button
            v-for="h in historyList"
            :key="h"
            class="history-btn"
            @click="selectFetchHistory(h)"
          >{{ h }}</button>
        </div>
      </div>

      <button class="btn" @click="translate"><AeroIcon name="translate" :size="18" /> 翻译报文</button>

      <div class="result-wrap">
        <div class="btn-row">
          <button class="btn btn-sm" @click="copyMetarResult"><AeroIcon name="clipboard" :size="14" /> 复制</button>
          <button class="btn btn-sm" @click="shareMetarResult"><AeroIcon name="camera" :size="14" /> 分享</button>
        </div>
        <div :class="resultClass" v-html="metarResultHtml"></div>
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

const metarInput = ref('')
const fetchIcao = ref('')
const metarResultText = ref('等待输入…')
const metarLoading = ref(false)
const metarError = ref(false)

// 联想相关状态
const fetchSuggestions = ref([])
const showFetchSuggest = ref(false)
const fetchActiveIdx = ref(-1)
let fetchDebounce = null

const metarResultHtml = computed(() => {
  if (metarLoading.value) return '<div class="spinner"></div> 加载中...'
  return metarResultText.value.replace(/\n/g, '<br>')
})

const resultClass = computed(() => ({
  'result-box': true,
  'loading': metarLoading.value,
  'error': metarError.value
}))

// ---- 联想搜索 ----
async function doFetchSuggest(query) {
  if (!query || query.length < 1) {
    fetchSuggestions.value = []
    showFetchSuggest.value = false
    return
  }
  try {
    const res = await fetch(`/api_web/suggest?q=${encodeURIComponent(query)}`)
    const data = await res.json()
    fetchSuggestions.value = data.suggestions || []
    fetchActiveIdx.value = -1
    showFetchSuggest.value = fetchSuggestions.value.length > 0
  } catch {
    fetchSuggestions.value = []
    showFetchSuggest.value = false
  }
}

function onFetchInput() {
  clearTimeout(fetchDebounce)
  fetchDebounce = setTimeout(() => {
    doFetchSuggest(fetchIcao.value.trim())
  }, 200)
}

function onFetchFocus() {
  if (fetchIcao.value.trim() && fetchSuggestions.value.length) {
    showFetchSuggest.value = true
  }
}

function onFetchBlur() {
  setTimeout(() => { showFetchSuggest.value = false }, 150)
}

function onFetchKeydown(e) {
  if (!showFetchSuggest.value || !fetchSuggestions.value.length) {
    if (e.key === 'Enter') { e.preventDefault(); fetchMetar() }
    return
  }
  switch (e.key) {
    case 'ArrowDown':
      e.preventDefault()
      fetchActiveIdx.value = (fetchActiveIdx.value + 1) % fetchSuggestions.value.length
      break
    case 'ArrowUp':
      e.preventDefault()
      fetchActiveIdx.value = fetchActiveIdx.value <= 0
        ? fetchSuggestions.value.length - 1
        : fetchActiveIdx.value - 1
      break
    case 'Enter':
      e.preventDefault()
      if (fetchActiveIdx.value >= 0) {
        selectFetchSuggestion(fetchSuggestions.value[fetchActiveIdx.value])
      } else {
        showFetchSuggest.value = false
        fetchMetar()
      }
      break
    case 'Escape':
      showFetchSuggest.value = false
      break
  }
}

function selectFetchSuggestion(s) {
  fetchIcao.value = s.icao
  showFetchSuggest.value = false
  fetchMetar()
}

async function translate() {
  const m = metarInput.value.trim()
  if (!m) {
    metarError.value = true
    metarResultText.value = '⚠️ 请输入 METAR 报文内容'
    return
  }

  metarLoading.value = true
  metarError.value = false
  try {
    const res = await fetch('/api_web/metar', {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({ metar: m })
    })
    const data = await res.json()
    if (data.error) {
      metarError.value = true
      metarResultText.value = `❌ ${data.error}`
    } else {
      metarResultText.value = data.result
    }
  } catch (err) {
    metarError.value = true
    metarResultText.value = `⚠️ 网络错误: ${err.message}\n请检查后端服务状态`
  } finally {
    metarLoading.value = false
  }
}

async function fetchMetar() {
  const icao = fetchIcao.value.trim().toUpperCase()
  if (!icao) {
    showToast('请输入 ICAO 代码', 'warning')
    return
  }
  if (!/^[A-Z]{4}$/.test(icao)) {
    showToast('ICAO 代码应为 4 个大写字母', 'warning')
    return
  }

  metarResultText.value = '<div class="spinner"></div> 获取中...'
  metarLoading.value = true
  try {
    const res = await fetch('/api_web/fetch_metar', {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({ icao })
    })
    const data = await res.json()
    if (data.error) {
      metarLoading.value = false
      metarError.value = true
      metarResultText.value = `❌ ${data.error}`
    } else {
      metarInput.value = data.metar
      addToHistory(icao)
      metarLoading.value = false
      await translate()
    }
  } catch (err) {
    metarLoading.value = false
    metarError.value = true
    metarResultText.value = `⚠️ 请求失败: ${err.message}`
  }
}

function selectFetchHistory(icao) {
  fetchIcao.value = icao
  fetchMetar()
}

function copyMetarInput() {
  if (!metarInput.value.trim()) {
    showToast('输入框为空，无内容可复制', 'warning')
    return
  }
  navigator.clipboard.writeText(metarInput.value).then(() => {
    showToast('✅ METAR 报文已复制', 'success')
  }).catch(() => {
    showToast('❌ 复制失败，请手动复制', 'error')
  })
}

function copyFetchIcao() {
  if (!fetchIcao.value.trim()) {
    showToast('输入框为空，无内容可复制', 'warning')
    return
  }
  navigator.clipboard.writeText(fetchIcao.value).then(() => {
    showToast('✅ ICAO 代码已复制', 'success')
  }).catch(() => {
    showToast('❌ 复制失败，请手动复制', 'error')
  })
}

function copyMetarResult() {
  if (metarResultText.value === '等待输入…') {
    showToast('暂无内容可复制', 'warning')
    return
  }
  navigator.clipboard.writeText(metarResultText.value).then(() => {
    showToast('✅ 结果已复制到剪贴板', 'success')
  }).catch(() => {
    showToast('❌ 复制失败，请手动复制', 'error')
  })
}

async function shareMetarResult() {
  if (metarResultText.value === '等待输入…') {
    showToast('暂无内容可分享', 'warning')
    return
  }
  const r = await shareAsImage(metarResultText.value, 'METAR')
  if (r === 'success') showToast('✅ 图片已复制到剪贴板', 'success')
  else if (r === 'download') showToast('⚠️ 您的浏览器不支持直接复制图片，已为您下载图片', 'warning')
  else showToast('❌ 复制失败，请尝试手动截图', 'error')
}
</script>
