<template>
  <svg
    viewBox="0 0 24 24"
    :width="size"
    :height="size"
    :class="className"
    :style="{ display: inline ? 'inline-block' : 'block', verticalAlign: inline ? 'middle' : 'baseline', flexShrink: 0 }"
    xmlns="http://www.w3.org/2000/svg"
  >
    <!-- ✈️ 飞机 — App 标题 / 分享卡片（蓝色填充） -->
    <g v-if="name === 'plane'">
      <path fill="#2563eb" stroke="#1e40af" stroke-width=".3"
        d="M21 16v-2l-8-5V3.5A1.5 1.5 0 0 0 11.5 2 1.5 1.5 0 0 0 10 3.5V9l-8 5v2l8-2.5V19l-2 1.5V22l3.5-1 3.5 1v-1.5L13 19v-5.5l8 2.5z"/>
    </g>

    <!-- 🛫 候机楼 + 塔台 — ICAO 卡片标题（彩色） -->
    <g v-else-if="name === 'takeoff'" transform="matrix(0.02344 0 0 0.02344 0 0)">
      <path d="M466.2 102.9c38.8 0 74.2 14.7 100.8 38.9 14.2-5.9 29.7-9.1 46-9.1 61.7 0 112.5 46.5 119.3 106.4 0.5 4.5 1.5 13.7-11.4 13.7H328.4c-7.8 0-11.9-9.9-11.4-14.8 7.5-75.8 71.4-135.1 149.2-135.1z" fill="#00B3E3"/>
      <path d="M379.6 227.7c1.1-10.4-6.7-19-17.2-19H147.7c-10.5 0-18.2 8.5-17.2 19l8.5 84.5c1.1 10.4 10.5 19 21 19h190.1c10.5 0 19.9-8.5 21-19l8.5-84.5z" fill="#0071CE"/>
      <path d="M131 233.1l2.9 28.6h242.3l2.9-28.6zM135.2 274.4l3.8 37.8c1.1 10.4 10.5 19 21 19h190.1c10.5 0 19.9-8.5 21-19l3.8-37.8H135.2z"/>
      <path d="M173.3 433.8h163.6v465.9H173.3z" fill="#A4A9AD"/>
      <path d="M173.3 433.8h163.6v87.8H173.3z"/>
      <path d="M959.7 913.5c0 4.2-3.5 7.7-7.7 7.7H73.1c-4.2 0-7.7-3.5-7.7-7.7v-27.6c0-4.2 3.5-7.7 7.7-7.7H952c4.2 0 7.7 3.5 7.7 7.7v27.6z" fill="#333E48"/>
      <path d="M403.5 308.7c1.3-10.4-6.2-18.9-16.7-18.9H123.2c-10.5 0-18 8.5-16.7 18.9l18.8 147.4c1.3 10.4 11 18.9 21.5 18.9h216.5c10.5 0 20.2-8.5 21.5-18.9l18.7-147.4z" fill="#A4A9AD"/>
      <path d="M193.1 289.8h123.8v79.1H193.1z" fill="#D1D3D3"/>
      <path d="M111.3 345.6l9.3 73.6h268.9l9.3-73.6z" fill="#0071CE"/>
      <path d="M240.7 345.6h28.6v73.6h-28.6z m-87.8 0h28.6v73.6h-28.6z m175.7 0h28.6v73.6h-28.6z"/>
      <path d="M173.3 587.7h163.6v127.8H173.3z m112.2-357.5c0 16.8-13.6 30.4-30.4 30.4-16.8 0-30.4-13.6-30.4-30.4v-21.5c0-16.8 13.6-30.4 30.4-30.4s30.4 13.6 30.4 30.4v21.5z" fill="#D1D3D3"/>
      <path d="M952 878.2H406v43h546c4.2 0 7.7-3.5 7.7-7.7v-27.6c0-4.3-3.5-7.7-7.7-7.7z" fill="#A4A9AD"/>
      <path d="M824.4 668.2H562l-57.4-57.4c-6.8-6.4-15.9-10.3-26-10.3-20.8 0-37.8 16.9-37.8 37.7v105.5c0 41.7 33.8 75.5 75.5 75.5h308c41.7 0 75.5-33.8 75.5-75.5 0.1-41.7-33.7-75.5-75.4-75.5z" fill="#D1D3D3"/>
      <path d="M720.1 788.6h-144c-7.9 0-14.3-6.4-14.3-14.3s6.4-14.3 14.3-14.3h144c7.9 0 14.3 6.4 14.3 14.3s-6.4 14.3-14.3 14.3z" fill="#A4A9AD"/>
      <path d="M878.3 690.9h-77.1c-14.6 0-26.5 11.8-26.5 26.5 0 14.6 11.8 26.5 26.5 26.5h98.7v-0.1c0-20.7-8.3-39.3-21.6-52.9z" fill="#0071CE"/>
      <path d="M764.7 848.7a29.5 29.5 0 1 0 59 0 29.5 29.5 0 1 0-59 0zM566.1 848.7a29.5 29.5 0 1 0 59 0 29.5 29.5 0 1 0-59 0z" fill="#333E48"/>
      <path d="M562 668.2l-57.4-57.4c-6.8-6.4-15.9-10.3-26-10.3-20.8 0-37.8 16.9-37.8 37.7v105.5c0 26.1 13.3 49.2 33.5 62.7 14.2-46.7 59.8-138.2 187.1-138.2H562z" fill="#0071CE"/>
      <path d="M523.1 629.4c-33.4 12-61.7 32-82.3 51.4v42.5c16.1-20.8 54.1-57.5 105-71.1l-22.7-22.8z" fill="#00B3E3"/>
      <path d="M683.9 428a90.8 90.8 0 1 0 181.6 0 90.8 90.8 0 1 0-181.6 0z" fill="#FFB819"/>
    </g>

    <!-- 🌦️ METAR 天气 — 云 + 太阳 -->
    <g v-else-if="name === 'weather'" transform="matrix(0.02344 0 0 0.02344 0 0)">
      <path d="M456.71619 203.337143a36.571429 36.571429 0 1 1 49.980953-13.409524 36.571429 36.571429 0 0 1-49.980953 13.409524zM335.055238 170.666667a36.571429 36.571429 0 1 1 36.571429-36.571429 36.571429 36.571429 0 0 1-36.571429 36.571429z m-121.660952 32.670476a36.571429 36.571429 0 1 1 13.287619-49.980953 36.742095 36.742095 0 0 1-13.287619 49.980953z m-139.093334 102.4a36.571429 36.571429 0 1 1 49.980953-13.409524 36.571429 36.571429 0 0 1-49.980953 13.409524z m17.310477 108.373333a36.571429 36.571429 0 1 1-36.571429-36.571428 36.571429 36.571429 0 0 1 36.571429 36.571428zM335.055238 207.238095a207.238095 207.238095 0 0 1 188.708572 121.904762h-85.211429a134.095238 134.095238 0 0 0-222.841905 146.285714h-78.750476a207.299048 207.299048 0 0 1 198.095238-268.190476z" fill="#FBBF24"/>
      <path d="M871.43619 417.889524a267.76381 267.76381 0 0 0-420.693333 159.817143A182.735238 182.735238 0 0 0 167.558095 792.380952h-77.775238a256.109714 256.109714 0 0 1 321.219048-317.683809 341.333333 341.333333 0 0 1 460.434285-143.116191v86.308572z" fill="#504BFF" opacity=".1"/>
      <path d="M664.198095 926.47619c-4.144762 0-8.167619-0.365714-12.190476-0.487619V926.47619h-365.714286a256 256 0 1 1 75.946667-500.540952A341.333333 341.333333 0 1 1 664.198095 926.47619z m0-609.523809a268.190476 268.190476 0 0 0-262.217143 211.992381A182.857143 182.857143 0 1 0 286.293333 853.333333h365.714286v-0.365714c4.022857 0.24381 8.045714 0.365714 12.190476 0.365714a268.190476 268.190476 0 0 0 0-536.380952z" fill="#569AF7"/>
    </g>

    <!-- 📡 天线 / 信号（currentColor） -->
    <g v-else-if="name === 'antenna'" fill="none" stroke="currentColor" stroke-width="1.8" stroke-linecap="round">
      <circle cx="12" cy="19.5" r="1.8"/>
      <path d="M7.5 14a6.5 6.5 0 0 1 9 0"/>
      <path d="M4.5 9a11 11 0 0 1 15 0"/>
      <line x1="12" y1="17.5" x2="12" y2="3"/>
      <circle cx="12" cy="3" r="1.3" fill="currentColor" stroke="none"/>
    </g>

    <!-- 📸 相机（currentColor） -->
    <g v-else-if="name === 'camera'" fill="none" stroke="currentColor" stroke-width="1.6" stroke-linecap="round" stroke-linejoin="round">
      <rect x="2.5" y="7" width="19" height="13" rx="3"/>
      <circle cx="12" cy="13.5" r="4.2"/>
      <path d="M7 4.5h2.5L11 2h2l1.5 2.5H17"/>
      <circle cx="17.5" cy="10" r=".6" fill="currentColor" stroke="none"/>
    </g>

    <!-- 📋 剪贴板（currentColor） -->
    <g v-else-if="name === 'clipboard'" fill="none" stroke="currentColor" stroke-width="1.6" stroke-linecap="round" stroke-linejoin="round">
      <rect x="4.5" y="2.5" width="15" height="19" rx="2.5"/>
      <path d="M8.5 2.5V1.2a2 2 0 0 1 2-2h3a2 2 0 0 1 2 2v1.3"/>
      <line x1="8" y1="10.5" x2="16" y2="10.5"/>
      <line x1="8" y1="14.5" x2="14" y2="14.5"/>
    </g>

    <!-- 🔍 搜索（currentColor） -->
    <g v-else-if="name === 'search'" fill="none" stroke="currentColor" stroke-width="1.8" stroke-linecap="round">
      <circle cx="10" cy="10" r="7.3"/>
      <line x1="15.5" y1="15.5" x2="21.5" y2="21.5"/>
    </g>

    <!-- 🗺️ 地图 + 定位针（绿色 + 红色 pin） -->
    <g v-else-if="name === 'map'">
      <path fill="#dcfce7" stroke="#16a34a" stroke-width=".8" stroke-linejoin="round"
        d="M3 7.5 8.5 5l7 3 5.5-2.5v9.5l-5.5 2.5-7-3-5.5 2.5Z"/>
      <line x1="8.5" y1="5" x2="8.5" y2="17.5" stroke="#86efac" stroke-width=".4"/>
      <line x1="15.5" y1="8" x2="15.5" y2="20" stroke="#86efac" stroke-width=".4"/>
      <circle cx="6" cy="10" r="1.8" fill="#ef4444"/>
      <path fill="#ef4444" d="M6 10 4.4 10.3v4.5l1.6-.3z"/>
    </g>

    <!-- 🌐 地球仪（蓝色海 + 绿色大陆） -->
    <g v-else-if="name === 'globe'">
      <circle cx="12" cy="12" r="10" fill="#dbeafe" stroke="#3b82f6" stroke-width="1"/>
      <ellipse cx="12" cy="12" rx="3.2" ry="10" fill="none" stroke="#93c5fd" stroke-width=".6"/>
      <line x1="2" y1="12" x2="22" y2="12" stroke="#93c5fd" stroke-width=".6"/>
      <path fill="#4ade80" d="M5.5 12.5a10 10 0 0 1 3-6.5 5 7 0 0 1 2 4 5 7 0 0 1-.5 5 6 4 0 0 1-3 2Z"/>
      <path fill="#22c55e" d="M12 3.5c1.5 0 3 3 3 6s-1.5 7-3 10Z"/>
      <path fill="#4ade80" d="M17.5 6a10.5 10.5 0 0 1 2 5.5 10.5 10.5 0 0 1-2 6 5 4 0 0 0-2-3 7 6 0 0 1-.5-4.5 4 4 0 0 1 2.5-4Z"/>
    </g>

    <!-- 🌤️ 晴间多云（黄色太阳 + 浅蓝云） -->
    <g v-else-if="name === 'cloud-sun'">
      <circle cx="7.5" cy="7" r="4.5" fill="#fbbf24"/>
      <g fill="#f59e0b">
        <rect x="6.5" y=".5" width="2" height="2" rx="1"/>
        <rect x="6.5" y="11.5" width="2" height="2" rx="1"/>
        <rect x="1" y="6" width="2" height="2" rx="1"/>
        <rect x="12" y="6" width="2" height="2" rx="1"/>
        <rect x="2.5" y="2.5" width="2" height="2" rx="1" transform="rotate(-45 3.5 3.5)"/>
        <rect x="9.5" y="9.5" width="2" height="2" rx="1" transform="rotate(-45 10.5 10.5)"/>
        <rect x="10" y="2.5" width="2" height="2" rx="1" transform="rotate(45 11 2.5)"/>
        <rect x="3" y="9.5" width="2" height="2" rx="1" transform="rotate(45 4 10.5)"/>
      </g>
      <path fill="#93c5fd" stroke="#60a5fa" stroke-width=".6"
        d="M2 14.5c0-2.5 2-4.5 4.5-4.5h6c2.5 0 4.5 2 4.5 4.5a3.5 3.5 0 0 1-2.7 6H4.7a3.5 3.5 0 0 1-2.7-6Z"/>
    </g>

    <!-- 🕐 时钟（白底 + 红时针 + 黑分针） -->
    <g v-else-if="name === 'clock'">
      <circle cx="12" cy="12" r="10" fill="#fff" stroke="#334155" stroke-width="1.2"/>
      <circle cx="12" cy="12" r=".6" fill="#334155"/>
      <line x1="12" y1="12" x2="12" y2="6" stroke="#ef4444" stroke-width="1.6" stroke-linecap="round"/>
      <line x1="12" y1="12" x2="15.5" y2="14.5" stroke="#334155" stroke-width="1.6" stroke-linecap="round"/>
    </g>

    <!-- ⚡ 闪电 — 页脚声明（currentColor 填充 + 微光晕） -->
    <g v-else-if="name === 'bolt'" fill="currentColor">
      <path opacity=".25" d="M14 2 5.5 13.5h5l-2.2 8.5L18 10.5h-5.5L14 2Z"/>
      <path d="M13.3 2.8 5.8 13.3h4.8l-2 7.7 9.2-11h-5l2-7.2Z"/>
    </g>

    <!-- 📊 柱状图（currentColor） -->
    <g v-else-if="name === 'chart'" fill="none" stroke="currentColor" stroke-width="1.6" stroke-linecap="round">
      <rect x="2.5" y="11" width="4.5" height="10" rx="1"/>
      <rect x="9.75" y="6" width="4.5" height="15" rx="1"/>
      <rect x="17" y="2.5" width="4.5" height="18.5" rx="1"/>
    </g>

    <!-- 🈂️ 翻译报文 — 左文档 + 右双向圆弧箭头 -->
    <g v-else-if="name === 'translate'" fill="none" stroke="currentColor" stroke-width="1.6" stroke-linecap="round" stroke-linejoin="round">
      <rect x="1.5" y="3" width="16" height="17" rx="2.2"/>
      <line x1="5" y1="8" x2="14.5" y2="8"/>
      <line x1="5" y1="11.5" x2="12" y2="11.5"/>
      <line x1="5" y1="15" x2="8.5" y2="15"/>
      <path d="M17.5 4 A3.5 3.5 0 0 1 17.5 11"/>
      <polyline points="16 5.5 17.5 4 19 5.5"/>
      <path d="M17.5 13 A3.5 3.5 0 0 0 17.5 20"/>
      <polyline points="16 18.5 17.5 20 19 18.5"/>
    </g>

    <!-- ☁️⬇️ 云下载 / 获取实时报文 — 圆底云 + 小圆圈下载箭头 -->
    <g v-else-if="name === 'cloud-download'" fill="none" stroke="currentColor" stroke-width="1.5" stroke-linecap="round" stroke-linejoin="round">
      <path d="M3 14a5.5 5.5 0 0 1 5-5.4 5 5 0 0 1 9 2.4 4.5 4.5 0 0 1 2.5 8h-9a5 5 0 0 1-7.5-5Z"/>
      <circle cx="12" cy="19" r="4.5" fill="currentColor" stroke="none" opacity=".1"/>
      <polyline points="9.5 19 12 22.5 14.5 19"/>
      <line x1="12" y1="15" x2="12" y2="22.5"/>
    </g>
  </svg>
</template>

<script setup>
defineProps({
  name: { type: String, required: true },
  size: { type: [String, Number], default: 24 },
  className: { type: String, default: '' },
  inline: { type: Boolean, default: true }
})
</script>
