import { ref } from 'vue'

const shareHtml = ref('')
const shareTime = ref('')
const shareCardRef = ref(null)

export function useShare() {
  async function shareAsImage(resultText, title) {
    const shareCard = shareCardRef.value
    if (!shareCard) return

    shareTime.value = new Date().toLocaleString()
    shareHtml.value = resultText
      .replace(/ /g, '&nbsp;')
      .replace(/\n/g, '<br>')

    await new Promise(r => setTimeout(r, 100))

    try {
      const canvas = await window.html2canvas(shareCard, { scale: 2, backgroundColor: '#ffffff' })
      const blob = await new Promise(resolve => canvas.toBlob(resolve, 'image/png'))

      if (navigator.clipboard && navigator.clipboard.write) {
        await navigator.clipboard.write([
          new ClipboardItem({ [blob.type]: blob })
        ])
        return 'success'
      } else {
        const link = document.createElement('a')
        link.download = `aviation_${title}.png`
        link.href = canvas.toDataURL()
        link.click()
        return 'download'
      }
    } catch {
      return 'error'
    }
  }

  return { shareHtml, shareTime, shareCardRef, shareAsImage }
}
