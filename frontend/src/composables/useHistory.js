import { ref } from 'vue'

const HISTORY_KEY = 'icao_history'
const MAX_HISTORY = 5
const historyList = ref(getHistory())

function getHistory() {
  try {
    const stored = localStorage.getItem(HISTORY_KEY)
    return stored ? JSON.parse(stored) : []
  } catch {
    return []
  }
}

function saveHistory(list) {
  localStorage.setItem(HISTORY_KEY, JSON.stringify(list))
}

export function useHistory() {
  function addToHistory(icao) {
    let list = [...historyList.value]
    list = list.filter(item => item !== icao)
    list.unshift(icao)
    if (list.length > MAX_HISTORY) list.pop()
    saveHistory(list)
    historyList.value = list
  }

  return { historyList, addToHistory }
}
