import { reactive } from 'vue'

const toasts = reactive([])
let _id = 0

export function useToast() {
  function showToast(message, type = 'info', duration = 2000) {
    const id = ++_id
    toasts.push({ id, message, type, show: false })
    requestAnimationFrame(() => {
      const t = toasts.find(t => t.id === id)
      if (t) t.show = true
    })
    setTimeout(() => {
      const idx = toasts.findIndex(t => t.id === id)
      if (idx !== -1) toasts[idx].show = false
      setTimeout(() => {
        const idx2 = toasts.findIndex(t => t.id === id)
        if (idx2 !== -1) toasts.splice(idx2, 1)
      }, 300)
    }, duration)
  }

  return { toasts, showToast }
}
